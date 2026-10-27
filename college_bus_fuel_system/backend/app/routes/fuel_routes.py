import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.fuel_record import FuelRecord
from app.models.bus import Bus
from app.extensions import db
from app.services.file_storage_service import save_uploaded_bill
from app.services.ocr_service import scan_receipt_image
from app.services.duplicate_detector import check_duplicate_submission
from app.services.gps_service import verify_gps_location
from app.services.mileage_service import calculate_record_mileage
from app.utils.auth_helpers import get_current_authenticated_user, role_required, log_audit_action
from app.utils.validators import validate_fuel_submission_data, check_odometer_warnings

fuel_bp = Blueprint('fuel', __name__, url_prefix='/api/fuel')

@fuel_bp.route('/scan-receipt', methods=['POST'])
@jwt_required()
@role_required('DRIVER', 'ADMIN')
def scan_receipt():
    """
    Step 1: Driver uploads receipt image.
    Performs OCR/AI scanning and returns parsed fields with confidence score.
    Allows driver to preview and manually correct details before final submission.
    """
    if 'bill_image' not in request.files:
        return jsonify({'error': 'No bill_image file uploaded.'}), 400

    file = request.files['bill_image']
    try:
        saved_file = save_uploaded_bill(file)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    ocr_result = scan_receipt_image(saved_file['filepath'])

    return jsonify({
        'message': 'Receipt uploaded and scanned.',
        'bill_image_filename': saved_file['filename'],
        'bill_image_hash': saved_file['image_hash'],
        'ocr_extracted_data': ocr_result.get('extracted_data', {}),
        'ocr_confidence_score': ocr_result.get('confidence_score', 0.0),
        'ocr_status': ocr_result.get('ocr_status', 'MANUAL_FALLBACK'),
        'ocr_message': ocr_result.get('message', '')
    }), 200

@fuel_bp.route('/submit', methods=['POST'])
@jwt_required()
@role_required('DRIVER')
def submit_fuel_entry():
    """
    Step 2: Submits verified fuel entry.
    Runs GPS verification, duplicate screening, fuel-type matching, and mileage calculation.
    """
    driver = get_current_authenticated_user()
    data = request.get_json() or {}

    # Validate inputs
    val_errors = validate_fuel_submission_data(data)
    if val_errors:
        return jsonify({'error': 'Validation failed', 'details': val_errors}), 400

    bus_id = int(data['bus_id'])
    bus = Bus.query.get(bus_id)
    if not bus:
        return jsonify({'error': f'Bus with ID {bus_id} not found.'}), 404

    # Ensure bill image filename was provided
    bill_image_filename = data.get('bill_image_filename', '').strip()
    if not bill_image_filename:
        return jsonify({'error': 'bill_image_filename is required. Please upload bill receipt first.'}), 400

    fuel_litres = float(data['fuel_litres'])
    rate_per_litre = float(data['rate_per_litre'])
    total_cost = float(data['total_cost'])
    odometer_reading = float(data['odometer_reading'])
    fuel_station_name = data['fuel_station_name'].strip()
    bill_image_hash = data.get('bill_image_hash')

    # Fuel type handling: respect bus's configured fuel type
    submitted_fuel_type = data.get('fuel_type')
    fuel_type = (submitted_fuel_type or bus.fuel_type or 'DIESEL').upper()

    # Date parsing
    bill_date_raw = data.get('bill_date')
    if bill_date_raw:
        try:
            bill_date = datetime.fromisoformat(bill_date_raw.replace('Z', '+00:00')).replace(tzinfo=None)
        except Exception:
            bill_date = datetime.utcnow()
    else:
        bill_date = datetime.utcnow()

    # Privacy-conscious GPS validation
    lat = float(data['latitude']) if data.get('latitude') is not None else None
    lon = float(data['longitude']) if data.get('longitude') is not None else None
    gps_result = verify_gps_location(lat, lon)

    # Multi-factor duplicate screening
    dup_result = check_duplicate_submission(
        bus_id=bus_id,
        total_cost=total_cost,
        odometer_reading=odometer_reading,
        bill_image_hash=bill_image_hash,
        bill_date=bill_date
    )

    # Check for odometer regression warnings
    odo_warnings = check_odometer_warnings(bus, odometer_reading)
    combined_warnings = []
    if dup_result.get('warning_details'):
        combined_warnings.append(dup_result['warning_details'])
    if odo_warnings:
        combined_warnings.extend(odo_warnings)

    is_flagged = dup_result.get('is_duplicate_suspected', False) or bool(odo_warnings)
    warning_text = " | ".join(combined_warnings) if combined_warnings else None

    # Create fuel record
    ref_code = f"FL-{datetime.utcnow().year}-{uuid.uuid4().hex[:6].upper()}"
    new_record = FuelRecord(
        reference_code=ref_code,
        bus_id=bus_id,
        driver_id=driver.id,
        fuel_litres=fuel_litres,
        rate_per_litre=rate_per_litre,
        total_cost=total_cost,
        odometer_reading=odometer_reading,
        fuel_station_name=fuel_station_name,
        fuel_type=fuel_type,
        bill_date=bill_date,
        bill_image_filename=bill_image_filename,
        bill_image_hash=bill_image_hash,
        ocr_extracted_data=data.get('ocr_extracted_data'),
        ocr_confidence_score=float(data.get('ocr_confidence_score', 0.0)),
        ocr_status=data.get('ocr_status', 'MANUAL_FALLBACK'),
        submission_latitude=lat,
        submission_longitude=lon,
        gps_nearest_bunk_id=gps_result.get('nearest_bunk_id'),
        gps_distance_meters=gps_result.get('distance_meters'),
        is_gps_verified=gps_result.get('is_verified', False),
        duplicate_flag=is_flagged,
        duplicate_warning_details=warning_text,
        duplicate_matched_id=dup_result.get('matched_record_id'),
        status='PENDING'
    )
    db.session.add(new_record)
    db.session.commit()

    # Compute sequential mileage
    calculate_record_mileage(new_record)
    db.session.commit()

    log_audit_action(
        actor_user=driver,
        action='FUEL_ENTRY_SUBMITTED',
        entity_type='FUEL_RECORD',
        entity_id=new_record.id,
        new_state=new_record.to_dict(),
        details=f"Driver {driver.full_name} submitted fuel record {ref_code} for Bus #{bus.bus_number} ({fuel_litres}L, ₹{total_cost})."
    )

    return jsonify({
        'message': 'Fuel entry submitted successfully and queued for approval.',
        'fuel_record': new_record.to_dict()
    }), 201

@fuel_bp.route('/records', methods=['GET'])
@jwt_required()
def list_fuel_records():
    """Lists fuel records (Admin/VC see all; Driver sees only their own). Filterable by driver_id for Admin/VC."""
    current_user = get_current_authenticated_user()
    if not current_user:
        return jsonify({'error': 'Unauthorized'}), 401

    query = FuelRecord.query
    if current_user.role == 'DRIVER':
        query = query.filter_by(driver_id=current_user.id)
    else:
        # Admin or VC can filter by specific driver
        driver_id = request.args.get('driver_id')
        if driver_id:
            query = query.filter_by(driver_id=int(driver_id))

    status_filter = request.args.get('status')
    if status_filter:
        query = query.filter_by(status=status_filter.upper())

    bus_id = request.args.get('bus_id')
    if bus_id:
        query = query.filter_by(bus_id=int(bus_id))

    fuel_type_filter = request.args.get('fuel_type')
    if fuel_type_filter:
        query = query.filter_by(fuel_type=fuel_type_filter.upper())

    duplicates_only = request.args.get('duplicates_only')
    if duplicates_only and duplicates_only.lower() in ('true', '1'):
        query = query.filter_by(duplicate_flag=True)

    records = query.order_by(FuelRecord.created_at.desc()).all()
    return jsonify({'records': [r.to_dict() for r in records]}), 200

@fuel_bp.route('/records/<int:record_id>', methods=['GET'])
@jwt_required()
def get_fuel_record(record_id):
    """Retrieves full details of a specific fuel record."""
    current_user = get_current_authenticated_user()
    record = FuelRecord.query.get_or_404(record_id)

    # Driver can only view their own record
    if current_user.role == 'DRIVER' and record.driver_id != current_user.id:
        return jsonify({'error': 'Forbidden: You cannot view fuel records submitted by other drivers.'}), 403

    return jsonify({'fuel_record': record.to_dict()}), 200

@fuel_bp.route('/records/<int:record_id>/correct', methods=['PUT'])
@jwt_required()
@role_required('DRIVER')
def resubmit_corrected_record(record_id):
    """
    Driver resubmission after CORRECTION_REQUIRED.
    Updates corrected fields, recalculates duplicate warnings and mileage, and restores status to PENDING.
    """
    driver = get_current_authenticated_user()
    record = FuelRecord.query.get_or_404(record_id)

    if record.driver_id != driver.id:
        return jsonify({'error': 'Forbidden: You can only edit your own submissions.'}), 403

    if record.status != 'CORRECTION_REQUIRED':
        return jsonify({'error': f'Record is in {record.status} state. Corrections can only be made when CORRECTION_REQUIRED.'}), 400

    data = request.get_json() or {}
    prev_state = record.to_dict()

    if 'fuel_litres' in data:
        record.fuel_litres = float(data['fuel_litres'])
    if 'rate_per_litre' in data:
        record.rate_per_litre = float(data['rate_per_litre'])
    if 'total_cost' in data:
        record.total_cost = float(data['total_cost'])
    if 'odometer_reading' in data:
        record.odometer_reading = float(data['odometer_reading'])
    if 'fuel_station_name' in data:
        record.fuel_station_name = data['fuel_station_name'].strip()
    if 'fuel_type' in data:
        record.fuel_type = data['fuel_type'].strip().upper()
    if 'bill_image_filename' in data:
        record.bill_image_filename = data['bill_image_filename'].strip()
    if 'bill_image_hash' in data:
        record.bill_image_hash = data['bill_image_hash']

    # Reset status back to PENDING for review
    record.status = 'PENDING'
    record.correction_notes = f"Resubmitted by driver on {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"

    # Re-evaluate duplicate screening
    dup_res = check_duplicate_submission(
        bus_id=record.bus_id,
        total_cost=float(record.total_cost),
        odometer_reading=float(record.odometer_reading),
        bill_image_hash=record.bill_image_hash,
        bill_date=record.bill_date,
        current_record_id=record.id
    )
    bus = Bus.query.get(record.bus_id)
    odo_warnings = check_odometer_warnings(bus, float(record.odometer_reading))
    warnings = []
    if dup_res.get('warning_details'):
        warnings.append(dup_res['warning_details'])
    if odo_warnings:
        warnings.extend(odo_warnings)

    record.duplicate_flag = dup_res['is_duplicate_suspected'] or bool(odo_warnings)
    record.duplicate_warning_details = " | ".join(warnings) if warnings else None
    record.duplicate_matched_id = dup_res.get('matched_record_id')

    db.session.commit()

    # Re-evaluate mileage
    calculate_record_mileage(record)
    db.session.commit()

    log_audit_action(
        actor_user=driver,
        action='RECORD_RESUBMITTED_AFTER_CORRECTION',
        entity_type='FUEL_RECORD',
        entity_id=record.id,
        previous_state=prev_state,
        new_state=record.to_dict(),
        details=f"Driver {driver.full_name} resubmitted corrected record #{record.reference_code}"
    )

    return jsonify({
        'message': 'Corrected fuel record successfully resubmitted for approval.',
        'fuel_record': record.to_dict()
    }), 200
