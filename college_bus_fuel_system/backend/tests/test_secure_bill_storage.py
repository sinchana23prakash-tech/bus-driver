import os
from config import Config
from app.models.fuel_record import FuelRecord
from app.extensions import db

def test_secure_bill_storage_and_authorized_access(client, app, test_users, sample_bus):
    admin_token = test_users['tokens']['admin']
    driver1_token = test_users['tokens']['driver1']
    driver2_token = test_users['tokens']['driver2']

    # Create dummy bill file on disk in upload folder
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    test_bill_filename = "bill_driver1_private_doc.jpg"
    test_file_path = os.path.join(Config.UPLOAD_FOLDER, test_bill_filename)
    with open(test_file_path, "wb") as f:
        f.write(b"SAMPLE RECEIPT BYTES")

    # Associate with Driver 1
    with app.app_context():
        rec = FuelRecord(
            reference_code="FL-TEST-SEC01",
            bus_id=sample_bus.id,
            driver_id=test_users['driver1'].id,
            fuel_litres=30.0,
            rate_per_litre=95.0,
            total_cost=2850.0,
            odometer_reading=14000.0,
            fuel_station_name="Campus Station",
            bill_image_filename=test_bill_filename,
            status="PENDING"
        )
        db.session.add(rec)
        db.session.commit()

    try:
        # 1. Unauthenticated request -> 401
        res_unauth = client.get(f'/api/bills/{test_bill_filename}')
        assert res_unauth.status_code == 401

        # 2. Path traversal attack attempt -> blocked with 400 or 404
        res_traversal = client.get('/api/bills/..%2f..%2fconfig.py', headers={'Authorization': f'Bearer {admin_token}'})
        assert res_traversal.status_code in (400, 404)

        # 3. Driver 2 trying to view Driver 1's bill -> 403 Forbidden
        res_other_driver = client.get(f'/api/bills/{test_bill_filename}', headers={'Authorization': f'Bearer {driver2_token}'})
        assert res_other_driver.status_code == 403

        # 4. Driver 1 viewing their own bill -> 200 OK
        res_owner = client.get(f'/api/bills/{test_bill_filename}', headers={'Authorization': f'Bearer {driver1_token}'})
        assert res_owner.status_code == 200
        assert res_owner.data == b"SAMPLE RECEIPT BYTES"
        res_owner.close()

        # 5. Admin viewing the bill -> 200 OK
        res_admin = client.get(f'/api/bills/{test_bill_filename}', headers={'Authorization': f'Bearer {admin_token}'})
        assert res_admin.status_code == 200
        res_admin.close()

    finally:
        try:
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
        except Exception:
            pass
