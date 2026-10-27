import math
from app.models.petrol_bunk import ApprovedPetrolBunk

# GLOBAL SAFETY LOCK: Enforcement disabled until coordinates are physically verified and approved
GEOFENCE_ENFORCEMENT_ENABLED = False

def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two GPS coordinates in meters."""
    R = 6371000.0  # Earth's radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0)**2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return R * c

def verify_gps_location(latitude: float, longitude: float) -> dict:
    """
    Verifies driver submission coordinates against configured approved bunks.
    Guaranteed Safety Lock: When GEOFENCE_ENFORCEMENT_ENABLED is False, enforcement
    is bypassed, returning neutral non-enforced status without penalizing drivers.
    """
    # 1. Enforcement Safety Lock Check
    if not GEOFENCE_ENFORCEMENT_ENABLED:
        active_bunk = ApprovedPetrolBunk.query.filter_by(is_active=True).first()
        return {
            'is_verified': False,
            'nearest_bunk_id': active_bunk.id if active_bunk else None,
            'distance_meters': None,
            'notes': 'Geofence enforcement disabled pending on-site coordinate verification for IOC DEALERS, DSS FUEL SOUK.'
        }

    if latitude is None or longitude is None:
        return {
            'is_verified': False,
            'nearest_bunk_id': None,
            'distance_meters': None,
            'notes': 'Location coordinates were not provided by the device.'
        }

    active_bunks = ApprovedPetrolBunk.query.filter_by(is_active=True).all()
    if not active_bunks:
        return {
            'is_verified': False,
            'nearest_bunk_id': None,
            'distance_meters': None,
            'notes': 'No approved petrol stations configured in the system yet. Requires admin setup.'
        }

    nearest_bunk = None
    min_distance = float('inf')

    for bunk in active_bunks:
        dist = haversine_distance_meters(
            latitude, longitude,
            float(bunk.latitude), float(bunk.longitude)
        )
        if dist < min_distance:
            min_distance = dist
            nearest_bunk = bunk

    if nearest_bunk:
        distance_rounded = round(min_distance, 1)
        allowed_radius = nearest_bunk.geofence_radius_meters
        is_within_geofence = distance_rounded <= allowed_radius

        if is_within_geofence:
            notes = f"Verified: Located within {allowed_radius}m geofence of {nearest_bunk.name} (Distance: {distance_rounded}m)."
        else:
            notes = f"Notice: Located {distance_rounded}m away from closest station ({nearest_bunk.name}), outside authorized {allowed_radius}m geofence."

        return {
            'is_verified': is_within_geofence,
            'nearest_bunk_id': nearest_bunk.id,
            'distance_meters': distance_rounded,
            'notes': notes
        }

    return {
        'is_verified': False,
        'nearest_bunk_id': None,
        'distance_meters': None,
        'notes': 'Unable to calculate distance to fuel bunks.'
    }
