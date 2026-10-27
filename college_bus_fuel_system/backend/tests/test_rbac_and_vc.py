from app.models.fuel_record import FuelRecord
from app.extensions import db

def test_rbac_access_restrictions(client, test_users, sample_bus):
    admin_token = test_users['tokens']['admin']
    driver_token = test_users['tokens']['driver1']

    # 1. Driver trying to create a user -> 403 Forbidden
    res = client.post('/api/users', json={
        'username': 'sneakyuser',
        'email': 'sneaky@college.edu',
        'full_name': 'Sneaky User',
        'role': 'DRIVER',
        'password': 'Password@123'
    }, headers={'Authorization': f'Bearer {driver_token}'})
    assert res.status_code == 403

    # 2. Admin successfully creates a driver user
    res_admin = client.post('/api/users', json={
        'username': 'newdriver3',
        'email': 'driver3@college.edu',
        'full_name': 'Kavita Sharma',
        'role': 'DRIVER',
        'password': 'Password@123'
    }, headers={'Authorization': f'Bearer {admin_token}'})
    assert res_admin.status_code == 201

def test_vc_configurable_approval_enforcement(client, app, test_users, sample_bus):
    vc_token = test_users['tokens']['vc']
    admin_token = test_users['tokens']['admin']

    # Create a pending fuel record
    with app.app_context():
        rec = FuelRecord(
            reference_code="FL-TEST-VC01",
            bus_id=sample_bus.id,
            driver_id=test_users['driver1'].id,
            fuel_litres=50.0,
            rate_per_litre=98.0,
            total_cost=4900.0,
            odometer_reading=12600.0,
            fuel_station_name="HPCL Station",
            bill_image_filename="test_bill.jpg",
            status="PENDING"
        )
        db.session.add(rec)
        db.session.commit()
        record_id = rec.id

    # Scenario A: VC_CAN_APPROVE is False (Audit-Only mode default)
    app.config['VC_CAN_APPROVE'] = False
    res_vc_blocked = client.post(
        f'/api/approvals/{record_id}/approve',
        json={'remarks': 'VC attempting approval'},
        headers={'Authorization': f'Bearer {vc_token}'}
    )
    assert res_vc_blocked.status_code == 403
    assert 'Audit-Only Mode' in res_vc_blocked.get_json()['error']

    # Scenario B: VC_CAN_APPROVE is True (Configured to allow VC approvals)
    app.config['VC_CAN_APPROVE'] = True
    res_vc_allowed = client.post(
        f'/api/approvals/{record_id}/approve',
        json={'remarks': 'VC authorized audit signoff'},
        headers={'Authorization': f'Bearer {vc_token}'}
    )
    assert res_vc_allowed.status_code == 200
    assert res_vc_allowed.get_json()['fuel_record']['status'] == 'APPROVED'

    # Admin can always approve regardless of VC flag
    with app.app_context():
        rec2 = FuelRecord(
            reference_code="FL-TEST-ADM01",
            bus_id=sample_bus.id,
            driver_id=test_users['driver1'].id,
            fuel_litres=40.0,
            rate_per_litre=98.0,
            total_cost=3920.0,
            odometer_reading=12750.0,
            fuel_station_name="HPCL Station",
            bill_image_filename="test_bill2.jpg",
            status="PENDING"
        )
        db.session.add(rec2)
        db.session.commit()
        rec2_id = rec2.id

    res_admin = client.post(
        f'/api/approvals/{rec2_id}/approve',
        json={'remarks': 'Approved by Fleet Admin'},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert res_admin.status_code == 200
    assert res_admin.get_json()['fuel_record']['status'] == 'APPROVED'
