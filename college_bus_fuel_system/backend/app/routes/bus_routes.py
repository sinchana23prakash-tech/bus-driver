from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.bus import Bus
from app.models.user import User
from app.extensions import db
from app.utils.auth_helpers import role_required, get_current_authenticated_user, log_audit_action

bus_bp = Blueprint('buses', __name__, url_prefix='/api/buses')

@bus_bp.route('', methods=['GET'])
@jwt_required()
def list_buses():
    """Lists buses with driver assignments."""
    buses = Bus.query.order_by(Bus.bus_number.asc()).all()
    return jsonify({'buses': [b.to_dict() for b in buses]}), 200

@bus_bp.route('/<int:bus_id>', methods=['GET'])
@jwt_required()
def get_bus_detail(bus_id):
    """Retrieves single bus details."""
    bus = Bus.query.get_or_404(bus_id)
    return jsonify({'bus': bus.to_dict()}), 200

@bus_bp.route('/my-assigned', methods=['GET'])
@jwt_required()
@role_required('DRIVER')
def get_my_assigned_bus():
    """Returns the bus assigned to the currently logged in driver."""
    driver = get_current_authenticated_user()
    bus = Bus.query.filter_by(assigned_driver_id=driver.id, status='ACTIVE').first()
    if not bus:
        return jsonify({'bus': None, 'message': 'No active bus currently assigned to your profile.'}), 200
    return jsonify({'bus': bus.to_dict()}), 200

@bus_bp.route('', methods=['POST'])
@jwt_required()
@role_required('ADMIN')
def create_bus():
    """Admin endpoint to register a new college bus."""
    admin_actor = get_current_authenticated_user()
    data = request.get_json() or {}

    bus_number = data.get('bus_number', '').strip()
    reg_number = data.get('registration_number', '').strip().upper()
    model_name = data.get('model_name', '').strip()
    tank_capacity = float(data.get('fuel_tank_capacity', 150.0))
    fuel_type = data.get('fuel_type', 'DIESEL').upper()
    current_odometer = float(data.get('current_odometer', 0.0))
    assigned_driver_id = data.get('assigned_driver_id')

    if not bus_number or not reg_number:
        return jsonify({'error': 'bus_number and registration_number are required.'}), 400

    if Bus.query.filter_by(bus_number=bus_number).first():
        return jsonify({'error': f'Bus number {bus_number} already exists.'}), 400

    if Bus.query.filter_by(registration_number=reg_number).first():
        return jsonify({'error': f'Registration number {reg_number} already exists.'}), 400

    new_bus = Bus(
        bus_number=bus_number,
        registration_number=reg_number,
        model_name=model_name,
        fuel_tank_capacity=tank_capacity,
        fuel_type=fuel_type,
        current_odometer=current_odometer,
        status='ACTIVE',
        assigned_driver_id=assigned_driver_id if assigned_driver_id else None
    )
    db.session.add(new_bus)
    db.session.commit()

    log_audit_action(
        actor_user=admin_actor,
        action='BUS_CREATED',
        entity_type='BUS',
        entity_id=new_bus.id,
        new_state=new_bus.to_dict(),
        details=f"Created college bus {bus_number} ({reg_number})"
    )

    return jsonify({'message': 'Bus registered successfully.', 'bus': new_bus.to_dict()}), 201

@bus_bp.route('/<int:bus_id>', methods=['PUT'])
@jwt_required()
@role_required('ADMIN')
def update_bus(bus_id):
    """Admin endpoint to update bus specifications or assigned driver."""
    admin_actor = get_current_authenticated_user()
    bus = Bus.query.get_or_404(bus_id)
    prev_state = bus.to_dict()

    data = request.get_json() or {}
    if 'bus_number' in data and data['bus_number'].strip():
        bus.bus_number = data['bus_number'].strip()
    if 'registration_number' in data and data['registration_number'].strip():
        bus.registration_number = data['registration_number'].strip().upper()
    if 'model_name' in data:
        bus.model_name = data['model_name'].strip()
    if 'fuel_tank_capacity' in data:
        bus.fuel_tank_capacity = float(data['fuel_tank_capacity'])
    if 'fuel_type' in data:
        bus.fuel_type = data['fuel_type'].upper()
    if 'current_odometer' in data:
        bus.current_odometer = float(data['current_odometer'])
    if 'status' in data:
        bus.status = data['status'].upper()
    if 'assigned_driver_id' in data:
        bus.assigned_driver_id = data['assigned_driver_id'] if data['assigned_driver_id'] else None

    db.session.commit()

    log_audit_action(
        actor_user=admin_actor,
        action='BUS_UPDATED',
        entity_type='BUS',
        entity_id=bus.id,
        previous_state=prev_state,
        new_state=bus.to_dict(),
        details=f"Updated details for bus {bus.bus_number}"
    )

    return jsonify({'message': 'Bus details updated successfully.', 'bus': bus.to_dict()}), 200
