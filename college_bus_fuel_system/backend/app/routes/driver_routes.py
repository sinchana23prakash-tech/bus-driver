from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from app.models.user import User
from app.models.bus import Bus
from app.models.fuel_record import FuelRecord
from app.utils.auth_helpers import get_current_authenticated_user, role_required

driver_bp = Blueprint('drivers', __name__, url_prefix='/api/drivers')

@driver_bp.route('', methods=['GET'])
@driver_bp.route('/', methods=['GET'])
@jwt_required()
@role_required('ADMIN', 'VC')
def list_drivers():
    """
    Lists all driver accounts with their assigned bus and summary record metrics.
    Accessible to ADMIN and VC.
    """
    drivers = User.query.filter_by(role='DRIVER').order_by(User.full_name.asc()).all()
    results = []

    for d in drivers:
        assigned_bus = Bus.query.filter_by(assigned_driver_id=d.id).first()
        
        # Summary counts
        total_records = FuelRecord.query.filter_by(driver_id=d.id).count()
        pending_count = FuelRecord.query.filter_by(driver_id=d.id, status='PENDING').count()
        approved_count = FuelRecord.query.filter_by(driver_id=d.id, status='APPROVED').count()
        approved_spend = FuelRecord.query.filter_by(driver_id=d.id, status='APPROVED').with_entities(
            func.sum(FuelRecord.total_cost)
        ).scalar() or 0.0

        results.append({
            'id': d.id,
            'username': d.username,
            'full_name': d.full_name,
            'email': d.email,
            'phone_number': d.phone_number,
            'is_active': d.is_active,
            'assigned_bus_id': assigned_bus.id if assigned_bus else None,
            'assigned_bus_number': assigned_bus.bus_number if assigned_bus else None,
            'assigned_bus_registration': assigned_bus.registration_number if assigned_bus else None,
            'assigned_bus_fuel_type': assigned_bus.fuel_type if assigned_bus else None,
            'total_records': total_records,
            'pending_count': pending_count,
            'approved_count': approved_count,
            'approved_spend': float(round(approved_spend, 2))
        })

    return jsonify({'drivers': results}), 200

@driver_bp.route('/<int:driver_id>/records', methods=['GET'])
@jwt_required()
def get_driver_records(driver_id):
    """
    Retrieves all fuel submissions and bills for a specific driver.
    ADMIN and VC can view any driver; DRIVER can only view their own.
    """
    current_user = get_current_authenticated_user()
    if not current_user:
        return jsonify({'error': 'Unauthorized'}), 401

    if current_user.role == 'DRIVER' and current_user.id != driver_id:
        return jsonify({'error': 'Forbidden: You cannot view records of other drivers.'}), 403

    driver = User.query.get_or_404(driver_id)
    if driver.role != 'DRIVER':
        return jsonify({'error': f'User ID {driver_id} is not a driver.'}), 400

    query = FuelRecord.query.filter_by(driver_id=driver_id)

    status_filter = request.args.get('status')
    if status_filter:
        query = query.filter_by(status=status_filter.upper())

    bus_id = request.args.get('bus_id')
    if bus_id:
        query = query.filter_by(bus_id=int(bus_id))

    records = query.order_by(FuelRecord.bill_date.desc(), FuelRecord.created_at.desc()).all()

    assigned_bus = Bus.query.filter_by(assigned_driver_id=driver.id).first()

    return jsonify({
        'driver': {
            'id': driver.id,
            'username': driver.username,
            'full_name': driver.full_name,
            'email': driver.email,
            'phone_number': driver.phone_number,
            'assigned_bus_number': assigned_bus.bus_number if assigned_bus else None,
            'assigned_bus_fuel_type': assigned_bus.fuel_type if assigned_bus else None
        },
        'records': [r.to_dict() for r in records]
    }), 200
