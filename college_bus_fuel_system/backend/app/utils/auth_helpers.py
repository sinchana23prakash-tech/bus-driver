from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models.user import User
from app.models.audit_log import AuditLog
from app.extensions import db

def get_current_authenticated_user():
    """Returns current active User object based on JWT identity."""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        if not user_id:
            return None
        user = User.query.get(int(user_id))
        if user and user.is_active:
            return user
        return None
    except Exception:
        return None

def role_required(*allowed_roles):
    """
    Decorator to restrict endpoint access to specific roles (ADMIN, VC, DRIVER).
    Returns 401/403 with descriptive JSON errors.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))
            
            if not user or not user.is_active:
                return jsonify({'error': 'Account inactive or unauthorized'}), 403

            if user.role not in allowed_roles:
                return jsonify({
                    'error': f'Access forbidden: Role {user.role} does not have required permissions.',
                    'required_roles': list(allowed_roles)
                }), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator

def log_audit_action(actor_user, action: str, entity_type: str, entity_id: int,
                     previous_state=None, new_state=None, details: str = None, ip_address: str = None):
    """Creates an immutable audit log entry."""
    try:
        log_entry = AuditLog(
            actor_id=actor_user.id if actor_user else None,
            actor_role=actor_user.role if actor_user else 'SYSTEM',
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            previous_state=previous_state,
            new_state=new_state,
            details=details,
            ip_address=ip_address or (request.remote_addr if request else None)
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        # Audit logging failure should not break primary operation, but log to stderr
        print(f"Audit log recording error: {e}")
