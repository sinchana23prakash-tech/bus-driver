from app.models.fuel_record import FuelRecord
from app.models.bus import Bus
from app.models.audit_log import AuditLog
from app.extensions import db

def test_full_fuel_lifecycle_submission_correction_approval(client, app, test_users, sample_bus):
    admin_token = test_users['tokens']['admin']
    driver_token = test_users['tokens']['driver1']

    # Step 1: Driver submits fuel record
    sub_res = client.post('/api/fuel/submit', json={
        'bus_id': sample_bus.id,
        'fuel_litres': 45.0,
        'rate_per_litre': 100.0,
        'total_cost': 4500.0,
        'odometer_reading': 12700.0,
        'fuel_station_name': 'Indian Oil Express Highway',
        'bill_image_filename': 'bill_sample_receipt.jpg',
        'latitude': 12.9716,
        'longitude': 77.5946
    }, headers={'Authorization': f'Bearer {driver_token}'})

    assert sub_res.status_code == 201
    record = sub_res.get_json()['fuel_record']
    record_id = record['id']
    assert record['status'] == 'PENDING'
    assert record['fuel_litres'] == 45.0

    # Step 2: Admin requests correction (e.g. Odometer typo or blurry receipt)
    corr_res = client.post(f'/api/approvals/{record_id}/request-correction', json={
        'correction_notes': 'Please double check the odometer reading against meter photo.'
    }, headers={'Authorization': f'Bearer {admin_token}'})

    assert corr_res.status_code == 200
    assert corr_res.get_json()['fuel_record']['status'] == 'CORRECTION_REQUIRED'

    # Step 3: Driver resubmits corrected data
    resub_res = client.put(f'/api/fuel/records/{record_id}/correct', json={
        'odometer_reading': 12720.0
    }, headers={'Authorization': f'Bearer {driver_token}'})

    assert resub_res.status_code == 200
    updated_rec = resub_res.get_json()['fuel_record']
    assert updated_rec['status'] == 'PENDING'
    assert updated_rec['odometer_reading'] == 12720.0

    # Step 4: Admin approves the corrected submission
    app_res = client.post(f'/api/approvals/{record_id}/approve', json={
        'remarks': 'Verified odometer photo and approved.'
    }, headers={'Authorization': f'Bearer {admin_token}'})

    assert app_res.status_code == 200
    assert app_res.get_json()['fuel_record']['status'] == 'APPROVED'

    # Step 5: Verify Bus current odometer was automatically updated
    with app.app_context():
        bus = Bus.query.get(sample_bus.id)
        assert float(bus.current_odometer) == 12720.0

        # Verify audit logs exist
        logs = AuditLog.query.filter_by(entity_id=record_id).all()
        actions = [l.action for l in logs]
        assert 'FUEL_ENTRY_SUBMITTED' in actions
        assert 'RECORD_CORRECTION_REQUESTED' in actions
        assert 'RECORD_RESUBMITTED_AFTER_CORRECTION' in actions
        assert 'RECORD_APPROVED' in actions
