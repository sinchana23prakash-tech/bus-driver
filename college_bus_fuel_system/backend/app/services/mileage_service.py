from app.extensions import db
from app.models.fuel_record import FuelRecord
from app.models.mileage import MileageComputation

def calculate_record_mileage(fuel_record: FuelRecord) -> MileageComputation:
    """
    Computes distance travelled and fuel efficiency (km/L).
    Flags as statistically reliable only when valid sequential odometer data exists.
    Strict Baseline Rules:
      - Only APPROVED DIESEL records can serve as baseline.
      - Unapproved, pending, or non-diesel records are NEVER used as baseline.
      - Odometer reading must be strictly increasing.
      - Normal heavy college bus economy window: 2.0 - 9.0 km/L.
      - Values outside 2-9 km/L are flagged as unreliable without rejecting transaction.
    """
    existing_computation = MileageComputation.query.filter_by(fuel_record_id=fuel_record.id).first()
    if not existing_computation:
        existing_computation = MileageComputation(
            bus_id=fuel_record.bus_id,
            fuel_record_id=fuel_record.id
        )

    # 1. Do not calculate Diesel mileage for non-Diesel records (e.g. historical CNG)
    if (fuel_record.fuel_type or '').upper() != 'DIESEL':
        existing_computation.previous_fuel_record_id = None
        existing_computation.distance_travelled_km = None
        existing_computation.calculated_kmpl = None
        existing_computation.is_statistically_reliable = False
        db.session.add(existing_computation)
        return existing_computation

    # 2. Find chronological previous APPROVED DIESEL fuel record for this specific bus
    prev_record = FuelRecord.query.filter(
        FuelRecord.bus_id == fuel_record.bus_id,
        FuelRecord.id != fuel_record.id,
        FuelRecord.status == 'APPROVED',
        FuelRecord.fuel_type == 'DIESEL',
        FuelRecord.bill_date <= fuel_record.bill_date
    ).order_by(FuelRecord.bill_date.desc(), FuelRecord.id.desc()).first()

    if prev_record and prev_record.odometer_reading is not None and fuel_record.odometer_reading is not None:
        prev_odo = float(prev_record.odometer_reading)
        curr_odo = float(fuel_record.odometer_reading)
        fuel_qty = float(fuel_record.fuel_litres) if fuel_record.fuel_litres else 0.0

        distance = curr_odo - prev_odo

        # Require strictly increasing odometer reading
        if distance > 0 and fuel_qty > 0:
            kmpl = round(distance / fuel_qty, 2)
            existing_computation.previous_fuel_record_id = prev_record.id
            existing_computation.distance_travelled_km = distance
            existing_computation.calculated_kmpl = kmpl
            
            # Normal college bus economy window: 2.0 - 9.0 km/L
            is_sound_range = (2.0 <= kmpl <= 9.0)
            existing_computation.is_statistically_reliable = is_sound_range
        else:
            # Odometer regression or zero increment: flag anomaly without rejecting transaction
            existing_computation.previous_fuel_record_id = prev_record.id
            existing_computation.distance_travelled_km = max(0.0, distance)
            existing_computation.calculated_kmpl = None
            existing_computation.is_statistically_reliable = False
    else:
        # First entry or awaiting prior approved Diesel record: insufficient baseline
        existing_computation.previous_fuel_record_id = None
        existing_computation.distance_travelled_km = None
        existing_computation.calculated_kmpl = None
        existing_computation.is_statistically_reliable = False

    db.session.add(existing_computation)
    return existing_computation
