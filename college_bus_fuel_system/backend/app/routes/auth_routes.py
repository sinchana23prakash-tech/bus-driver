from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user import User
from app.extensions import db
from app.utils.auth_helpers import log_audit_action, get_current_authenticated_user

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/setup-status', methods=['GET'])
def setup_status():
    """Checks whether the system requires initial administrator setup."""
    admin_count = User.query.filter_by(role='ADMIN').count()
    return jsonify({
        'needs_initial_setup': (admin_count == 0),
        'admin_count': admin_count
    }), 200

@auth_bp.route('/setup-initial-admin', methods=['POST'])
def setup_initial_admin():
    """
    Creates the first Administrator account during initial system deployment.
    Permanently disabled as soon as any ADMIN account exists.
    """
    admin_count = User.query.filter_by(role='ADMIN').count()
    if admin_count > 0:
        return jsonify({'error': 'Initial administrator setup has already been completed.'}), 403

    data = request.get_json() or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()
    phone_number = data.get('phone_number', '').strip()

    if not username or not email or not password or not full_name:
        return jsonify({'error': 'Username, email, password, and full name are required.'}), 400

    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters long.'}), 400

    # Ensure no collision with another username/email
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'error': 'Username or email already in use.'}), 400

    admin_user = User(
        username=username,
        email=email,
        full_name=full_name,
        phone_number=phone_number,
        role='ADMIN',
        is_active=True
    )
    admin_user.set_password(password)
    db.session.add(admin_user)
    db.session.commit()

    log_audit_action(
        actor_user=admin_user,
        action='INITIAL_ADMIN_SETUP',
        entity_type='USER',
        entity_id=admin_user.id,
        new_state=admin_user.to_dict(),
        details=f"System initialized with primary administrator: {admin_user.username}"
    )

    token = create_access_token(identity=str(admin_user.id))
    return jsonify({
        'message': 'Initial Administrator account successfully created.',
        'user': admin_user.to_dict(),
        'access_token': token
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticates users (Admin, VC, Driver) using email/username and password."""
    data = request.get_json() or {}
    identifier = data.get('identifier', '').strip()
    password = data.get('password', '')

    if not identifier or not password:
        return jsonify({'error': 'Email/username and password are required.'}), 400

    user = User.query.filter(
        (User.username == identifier) | (User.email == identifier.lower())
    ).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials.'}), 401

    if not user.is_active:
        return jsonify({'error': 'Account has been deactivated. Please contact administrator.'}), 403

    token = create_access_token(identity=str(user.id))
    
    log_audit_action(
        actor_user=user,
        action='USER_LOGIN',
        entity_type='USER',
        entity_id=user.id,
        details=f"User {user.username} ({user.role}) logged in successfully."
    )

    vc_can_approve = current_app.config.get('VC_CAN_APPROVE', False)

    return jsonify({
        'message': 'Authentication successful.',
        'access_token': token,
        'user': user.to_dict(),
        'policies': {
            'vc_can_approve': vc_can_approve
        }
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user_profile():
    """Returns profile of currently authenticated user with policy flags."""
    user = get_current_authenticated_user()
    if not user:
        return jsonify({'error': 'User not found or inactive.'}), 404

    vc_can_approve = current_app.config.get('VC_CAN_APPROVE', False)

    return jsonify({
        'user': user.to_dict(),
        'policies': {
            'vc_can_approve': vc_can_approve
        }
    }), 200

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Allows user to update their current password securely."""
    user = get_current_authenticated_user()
    if not user:
        return jsonify({'error': 'User not found.'}), 404

    data = request.get_json() or {}
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')

    if not user.check_password(current_password):
        return jsonify({'error': 'Current password is incorrect.'}), 400

    if len(new_password) < 8:
        return jsonify({'error': 'New password must be at least 8 characters long.'}), 400

    user.set_password(new_password)
    db.session.commit()

    log_audit_action(
        actor_user=user,
        action='PASSWORD_CHANGED',
        entity_type='USER',
        entity_id=user.id,
        details=f"User {user.username} changed account password."
    )

    return jsonify({'message': 'Password updated successfully.'}), 200
