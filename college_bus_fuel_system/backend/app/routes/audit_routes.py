from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.audit_log import AuditLog
from app.utils.auth_helpers import role_required

audit_bp = Blueprint('audit', __name__, url_prefix='/api/audit-logs')

@audit_bp.route('', methods=['GET'])
@audit_bp.route('/', methods=['GET'])
@jwt_required()
@role_required('ADMIN')
def list_audit_logs():
    """Lists immutable audit log entries for regulatory compliance and review. ADMIN ONLY."""
    action = request.args.get('action')
    entity_type = request.args.get('entity_type')

    query = AuditLog.query
    if action:
        query = query.filter_by(action=action)
    if entity_type:
        query = query.filter_by(entity_type=entity_type.upper())

    logs = query.order_by(AuditLog.created_at.desc()).limit(200).all()
    return jsonify({'audit_logs': [l.to_dict() for l in logs]}), 200
