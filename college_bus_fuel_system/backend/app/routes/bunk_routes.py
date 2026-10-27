from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.petrol_bunk import ApprovedPetrolBunk
from app.extensions import db
from app.utils.auth_helpers import role_required, get_current_authenticated_user, log_audit_action

bunk_bp = Blueprint('bunks', __name__, url_prefix='/api/bunks')

@bunk_bp.route('', methods=['GET'])
@jwt_required()
def list_bunks():
    """Lists approved petrol bunk geofence locations."""
    bunks = ApprovedPetrolBunk.query.order_by(ApprovedPetrolBunk.name.asc()).all()
    return jsonify({'bunks': [b.to_dict() for b in bunks]}), 200

@bunk_bp.route('', methods=['POST'])
@jwt_required()
@role_required('ADMIN')
def add_bunk():
    """Admin configuration for actual authorized petrol bunk locations."""
    admin_actor = get_current_authenticated_user()
    data = request.get_json() or {}

    name = data.get('name', '').strip()
    address = data.get('address', '').strip()
    
    try:
        latitude = float(data.get('latitude'))
        longitude = float(data.get('longitude'))
        radius = int(data.get('geofence_radius_meters', 500))
    except (ValueError, TypeError):
        return jsonify({'error': 'Valid numeric latitude, longitude, and geofence radius are required.'}), 400

    if not name:
        return jsonify({'error': 'Fuel station name is required.'}), 400

    if not (-90.0 <= latitude <= 90.0) or not (-180.0 <= longitude <= 180.0):
        return jsonify({'error': 'Latitude (-90 to +90) or Longitude (-180 to +180) out of valid bounds.'}), 400

    new_bunk = ApprovedPetrolBunk(
        name=name,
        address=address,
        latitude=latitude,
        longitude=longitude,
        geofence_radius_meters=radius,
        is_active=True
    )
    db.session.add(new_bunk)
    db.session.commit()

    log_audit_action(
        actor_user=admin_actor,
        action='BUNK_CONFIGURED',
        entity_type='BUNK',
        entity_id=new_bunk.id,
        new_state=new_bunk.to_dict(),
        details=f"Authorized petrol station: {name} ({latitude}, {longitude}, radius: {radius}m)"
    )

    return jsonify({
        'message': f'Approved fuel station {name} configured successfully.',
        'bunk': new_bunk.to_dict()
    }), 201

@bunk_bp.route('/<int:bunk_id>', methods=['PUT'])
@jwt_required()
@role_required('ADMIN')
def update_bunk(bunk_id):
    """Admin endpoint to update bunk coordinates or radius."""
    admin_actor = get_current_authenticated_user()
    bunk = ApprovedPetrolBunk.query.get_or_404(bunk_id)
    prev = bunk.to_dict()

    data = request.get_json() or {}
    if 'name' in data and data['name'].strip():
        bunk.name = data['name'].strip()
    if 'address' in data:
        bunk.address = data['address'].strip()
    if 'latitude' in data:
        bunk.latitude = float(data['latitude'])
    if 'longitude' in data:
        bunk.longitude = float(data['longitude'])
    if 'geofence_radius_meters' in data:
        bunk.geofence_radius_meters = int(data['geofence_radius_meters'])
    if 'is_active' in data:
        bunk.is_active = bool(data['is_active'])

    db.session.commit()

    log_audit_action(
        actor_user=admin_actor,
        action='BUNK_UPDATED',
        entity_type='BUNK',
        entity_id=bunk.id,
        previous_state=prev,
        new_state=bunk.to_dict(),
        details=f"Updated station configuration: {bunk.name}"
    )

    return jsonify({'message': 'Station configuration updated.', 'bunk': bunk.to_dict()}), 200

@bunk_bp.route('/<int:bunk_id>', methods=['DELETE'])
@jwt_required()
@role_required('ADMIN')
def delete_bunk(bunk_id):
    """Admin deactivation of an approved bunk."""
    admin_actor = get_current_authenticated_user()
    bunk = ApprovedPetrolBunk.query.get_or_404(bunk_id)
    bunk.is_active = False
    db.session.commit()

    log_audit_action(
        actor_user=admin_actor,
        action='BUNK_DEACTIVATED',
        entity_type='BUNK',
        entity_id=bunk.id,
        details=f"Deactivated fuel station {bunk.name}"
    )

    return jsonify({'message': f'Fuel station {bunk.name} deactivated.'}), 200
