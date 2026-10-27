from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.models.fuel_record import FuelRecord
from app.models.bus import Bus
from app.extensions import db
from app.utils.auth_helpers import role_required, get_current_authenticated_user, log_audit_action
from app.services.mileage_service import calculate_record_mileage

approval_bp = Blueprint('approvals', __name__, url_prefix='/api/approvals')

def verify_approval_permission(actor):
    """
    Validates whether the current actor has permission to approve/reject.
    Enforces the configurable VC policy.
    """
    if actor.role == 'ADMIN':
        return True, None

    if actor.role == 'VC':
        vc_allowed = current_app.config.get('VC_CAN_APPROVE', False)
        if not vc_allowed:
            return False, "Vice-Chancellor approval authority is currently disabled by college governance policy (Audit-Only Mode)."
        return True, None

    return False, "Access denied: Only Fleet Administrators and authorized Vice-Chancellor can perform review actions."

@approval_bp.route('/<int:record_id>/approve', methods=['POST'])
@jwt_required()
@role_required('ADMIN', 'VC')
def approve_fuel_record(record_id):
    """Approves a fuel submission and commits verified odometer updates to the fleet."""
    actor = get_current_authenticated_user()
    has_perm, err_msg = verify_approval_permission(actor)
    if not has_perm:
        return jsonify({'error': err_msg}), 403

    record = FuelRecord.query.get_or_404(record_id)
    if record.status == 'APPROVED':
        return jsonify({'error': 'Record has already been approved.'}), 400

    prev_state = record.to_dict()
    data = request.get_json() or {}
    remarks = data.get('remarks', '').strip()

    record.status = 'APPROVED'
    record.reviewed_by = actor.id
    record.reviewed_at = datetime.utcnow()
    
    if actor.role == 'ADMIN':
        record.admin_remarks = remarks
    else:
        record.vc_remarks = remarks

    # Update Bus current odometer reading if greater
    bus = Bus.query.get(record.bus_id)
    if bus and float(record.odometer_reading) > float(bus.current_odometer):
        bus.current_odometer = record.odometer_reading

    db.session.commit()

    # Re-verify and solidify mileage log
    calculate_record_mileage(record)
    db.session.commit()

    log_audit_action(
        actor_user=actor,
        action='RECORD_APPROVED',
        entity_type='FUEL_RECORD',
        entity_id=record.id,
        previous_state=prev_state,
        new_state=record.to_dict(),
        details=f"Fuel record {record.reference_code} approved by {actor.role} {actor.full_name}. Remarks: {remarks}"
    )

    return jsonify({
        'message': f'Fuel record {record.reference_code} approved successfully.',
        'fuel_record': record.to_dict()
    }), 200

@approval_bp.route('/<int:record_id>/reject', methods=['POST'])
@jwt_required()
@role_required('ADMIN', 'VC')
def reject_fuel_record(record_id):
    """Rejects a fuel submission with required explanation."""
    actor = get_current_authenticated_user()
    has_perm, err_msg = verify_approval_permission(actor)
    if not has_perm:
        return jsonify({'error': err_msg}), 403

    record = FuelRecord.query.get_or_404(record_id)
    prev_state = record.to_dict()

    data = request.get_json() or {}
    rejection_reason = data.get('rejection_reason', '').strip()
    if not rejection_reason:
        return jsonify({'error': 'A rejection reason is required.'}), 400

    record.status = 'REJECTED'
    record.reviewed_by = actor.id
    record.reviewed_at = datetime.utcnow()
    
    if actor.role == 'ADMIN':
        record.admin_remarks = rejection_reason
    else:
        record.vc_remarks = rejection_reason

    db.session.commit()

    log_audit_action(
        actor_user=actor,
        action='RECORD_REJECTED',
        entity_type='FUEL_RECORD',
        entity_id=record.id,
        previous_state=prev_state,
        new_state=record.to_dict(),
        details=f"Fuel record {record.reference_code} rejected by {actor.role} {actor.full_name}. Reason: {rejection_reason}"
    )

    return jsonify({
        'message': f'Fuel record {record.reference_code} rejected.',
        'fuel_record': record.to_dict()
    }), 200

@approval_bp.route('/<int:record_id>/request-correction', methods=['POST'])
@jwt_required()
@role_required('ADMIN', 'VC')
def request_record_correction(record_id):
    """Requests driver correction for unreadable receipt or mismatched odometer."""
    actor = get_current_authenticated_user()
    has_perm, err_msg = verify_approval_permission(actor)
    if not has_perm:
        return jsonify({'error': err_msg}), 403

    record = FuelRecord.query.get_or_404(record_id)
    prev_state = record.to_dict()

    data = request.get_json() or {}
    correction_notes = data.get('correction_notes', '').strip()
    if not correction_notes:
        return jsonify({'error': 'Correction notes explaining what the driver needs to fix are required.'}), 400

    record.status = 'CORRECTION_REQUIRED'
    record.correction_notes = correction_notes
    record.reviewed_by = actor.id
    record.reviewed_at = datetime.utcnow()

    db.session.commit()

    log_audit_action(
        actor_user=actor,
        action='RECORD_CORRECTION_REQUESTED',
        entity_type='FUEL_RECORD',
        entity_id=record.id,
        previous_state=prev_state,
        new_state=record.to_dict(),
        details=f"Correction requested for {record.reference_code} by {actor.role} {actor.full_name}. Instructions: {correction_notes}"
    )

    return jsonify({
        'message': f'Correction requested for {record.reference_code}. Driver notified for resubmission.',
        'fuel_record': record.to_dict()
    }), 200
