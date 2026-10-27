from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.user import User
from app.extensions import db
from app.utils.auth_helpers import role_required, get_current_authenticated_user, log_audit_action
from app.utils.validators import validate_email_format

user_bp = Blueprint('users', __name__, url_prefix='/api/users')

@user_bp.route('', methods=['GET'])
@jwt_required()
@role_required('ADMIN', 'VC')
def list_users():
    """Lists users filtered by role or active status (Admin and VC)."""
    role = request.args.get('role')
    is_active = request.args.get('is_active')

    query = User.query
    if role:
        query = query.filter_by(role=role.upper())
    if is_active is not None:
        query = query.filter_by(is_active=is_active.lower() in ('true', '1'))

    users = query.order_by(User.id.asc()).all()
    return jsonify({'users': [u.to_dict() for u in users]}), 200

@user_bp.route('', methods=['POST'])
@jwt_required()
@role_required('ADMIN')
def create_user():
    """Admin endpoint to create verified Driver, VC, or Admin accounts."""
    admin_actor = get_current_authenticated_user()
    data = request.get_json() or {}

    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    full_name = data.get('full_name', '').strip()
    phone_number = data.get('phone_number', '').strip()
    role = data.get('role', 'DRIVER').upper()
    password = data.get('password', '')

    if role not in ('ADMIN', 'VC', 'DRIVER'):
        return jsonify({'error': 'Invalid role. Must be ADMIN, VC, or DRIVER.'}), 400

    if not username or not email or not full_name or not password:
        return jsonify({'error': 'Username, email, full name, and initial password are required.'}), 400

    if not validate_email_format(email):
        return jsonify({'error': 'Invalid email address format.'}), 400

    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters long.'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username is already taken.'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email address is already in use.'}), 400

    new_user = User(
        username=username,
        email=email,
        full_name=full_name,
        phone_number=phone_number,
        role=role,
        is_active=True
    )
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    log_audit_action(
        actor_user=admin_actor,
        action='USER_CREATED',
        entity_type='USER',
        entity_id=new_user.id,
        new_state=new_user.to_dict(),
        details=f"Created {role} user: {username} ({full_name})"
    )

    return jsonify({
        'message': f'User {username} created successfully with role {role}.',
        'user': new_user.to_dict()
    }), 201

@user_bp.route('/<int:user_id>/status', methods=['PUT'])
@jwt_required()
@role_required('ADMIN')
def toggle_user_status(user_id):
    """Admin endpoint to activate or deactivate user accounts."""
    admin_actor = get_current_authenticated_user()
    user = User.query.get_or_404(user_id)

    if user.id == admin_actor.id:
        return jsonify({'error': 'You cannot deactivate your own administrative account.'}), 400

    data = request.get_json() or {}
    new_status = data.get('is_active')
    if new_status is None:
        new_status = not user.is_active

    user.is_active = bool(new_status)
    db.session.commit()

    log_audit_action(
        actor_user=admin_actor,
        action='USER_STATUS_UPDATED',
        entity_type='USER',
        entity_id=user.id,
        details=f"Set user {user.username} active status to {user.is_active}"
    )

    return jsonify({
        'message': f'User {user.username} status updated to {"Active" if user.is_active else "Inactive"}.',
        'user': user.to_dict()
    }), 200

@user_bp.route('/<int:user_id>/reset-password', methods=['PUT'])
@jwt_required()
@role_required('ADMIN')
def admin_reset_password(user_id):
    """Admin endpoint to safely reset a driver or staff member's password."""
    admin_actor = get_current_authenticated_user()
    user = User.query.get_or_404(user_id)

    data = request.get_json() or {}
    new_password = data.get('new_password', '')

    if len(new_password) < 8:
        return jsonify({'error': 'New password must be at least 8 characters long.'}), 400

    user.set_password(new_password)
    db.session.commit()

    log_audit_action(
        actor_user=admin_actor,
        action='ADMIN_PASSWORD_RESET',
        entity_type='USER',
        entity_id=user.id,
        details=f"Admin {admin_actor.username} reset password for user {user.username}"
    )

    return jsonify({'message': f'Password for user {user.username} successfully reset.'}), 200
