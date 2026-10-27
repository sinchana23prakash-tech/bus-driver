from datetime import datetime, timedelta
import imagehash
from app.models.fuel_record import FuelRecord
from config import Config

def check_duplicate_submission(bus_id: int, total_cost: float, odometer_reading: float, bill_image_hash: str, bill_date: datetime, current_record_id: int = None) -> dict:
    """
    Screens for potential duplicate bills or repeated submissions.
    Returns non-accusatory warnings rather than automatic fraud claims.
    """
    warning_reasons = []
    matched_id = None

    query = FuelRecord.query
    if current_record_id:
        query = query.filter(FuelRecord.id != current_record_id)
        
    all_records = query.order_by(FuelRecord.created_at.desc()).limit(200).all()

    # 1. Image Perceptual Hash Check
    if bill_image_hash:
        try:
            current_ihash = imagehash.hex_to_hash(bill_image_hash)
            threshold = Config.IMAGE_HASH_HAMMING_THRESHOLD
            for rec in all_records:
                if rec.bill_image_hash:
                    try:
                        past_ihash = imagehash.hex_to_hash(rec.bill_image_hash)
                        distance = current_ihash - past_ihash
                        if distance <= threshold:
                            warning_reasons.append(
                                f"Perceptual receipt match: Image visual difference is {distance} (threshold <={threshold}) with existing submission #{rec.reference_code}."
                            )
                            matched_id = rec.id
                            break
                    except Exception:
                        continue
        except Exception:
            pass

    # 2. Metadata Screening: Identical amount and odometer reading within 48 hours
    if bill_date:
        start_win = bill_date - timedelta(days=2)
        end_win = bill_date + timedelta(days=2)
        meta_match = FuelRecord.query.filter(
            FuelRecord.id != (current_record_id or 0),
            FuelRecord.bus_id == bus_id,
            FuelRecord.total_cost == total_cost,
            FuelRecord.odometer_reading == odometer_reading,
            FuelRecord.bill_date.between(start_win, end_win)
        ).first()

        if meta_match:
            warning_reasons.append(
                f"Metadata similarity: Bus #{meta_match.bus.bus_number} has an existing record #{meta_match.reference_code} with identical cost (₹{total_cost}) and odometer ({odometer_reading} km) within 48 hours."
            )
            if not matched_id:
                matched_id = meta_match.id

    if warning_reasons:
        return {
            'is_duplicate_suspected': True,
            'matched_record_id': matched_id,
            'warning_details': " | ".join(warning_reasons)
        }

    return {
        'is_duplicate_suspected': False,
        'matched_record_id': None,
        'warning_details': None
    }
