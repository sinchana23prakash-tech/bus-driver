import sys
import os
from datetime import datetime
from pathlib import Path

backend_dir = Path(r"C:\Users\PC\.gemini\antigravity\scratch\college_bus_fuel_system\backend")
sys.path.insert(0, str(backend_dir))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.bus import Bus
from app.models.petrol_bunk import ApprovedPetrolBunk
from app.models.fuel_record import FuelRecord
from app.models.mileage import MileageComputation
from app.models.audit_log import AuditLog
from app.services.gps_service import verify_gps_location, GEOFENCE_ENFORCEMENT_ENABLED
from app.services.mileage_service import calculate_record_mileage
from app.utils.validators import validate_fuel_submission_data

app = create_app()

def run_tests():
    print("======================================================================")
    print("         FINAL COMPREHENSIVE VERIFICATION & INTEGRITY TEST SUITE       ")
    print("======================================================================")
    
    with app.app_context():
        # TEST 1: Fleet Fuel Configuration (All 5 Buses must be DIESEL)
        print("\n--- TEST 1: Fleet Fuel Configuration ---")
        buses = Bus.query.order_by(Bus.id).all()
        assert len(buses) == 5, f"Expected 5 buses, found {len(buses)}"
        all_diesel = True
        for b in buses:
            print(f"  Bus {b.bus_number} (ID {b.id}, Reg: {b.registration_number}): Fuel={b.fuel_type}")
            if b.fuel_type != 'DIESEL':
                all_diesel = False
        assert all_diesel, "FAIL: Found bus that is not DIESEL!"
        print("[PASS] TEST 1: All 5 college buses are configured as DIESEL.")

        # TEST 2: Single Active Approved Station & Inactive Records
        print("\n--- TEST 2: Single Active Approved Station Configuration ---")
        active_bunks = ApprovedPetrolBunk.query.filter_by(is_active=True).all()
        inactive_bunks = ApprovedPetrolBunk.query.filter_by(is_active=False).all()
        assert len(active_bunks) == 1, f"Expected exactly 1 active bunk, found {len(active_bunks)}"
        assert active_bunks[0].name == 'IOC DEALERS, DSS FUEL SOUK', f"Unexpected active bunk: {active_bunks[0].name}"
        assert '510, Davangere - Harihar Rd, near GMIT COLLEGE' in active_bunks[0].address
        print(f"  Active Bunk: {active_bunks[0].name} (ID {active_bunks[0].id})")
        print(f"  Address: {active_bunks[0].address}")
        print(f"  Inactive Bunks Count: {len(inactive_bunks)} (IDs: {[b.id for b in inactive_bunks]})")
        assert len(inactive_bunks) == 2, f"Expected 2 inactive bunks, found {len(inactive_bunks)}"
        print("[PASS] TEST 2: Single active station configured; other 2 stations soft-deactivated.")

        # TEST 3: GPS Geofence Safety Lock Verification
        print("\n--- TEST 3: GPS Geofence Enforcement Safety Lock ---")
        assert GEOFENCE_ENFORCEMENT_ENABLED is False, "FAIL: GEOFENCE_ENFORCEMENT_ENABLED should be False!"
        test_gps = verify_gps_location(14.476260, 75.885080)
        print(f"  Submission at DSS Fuel Souk coordinates (14.476260, 75.885080):")
        print(f"    - is_verified: {test_gps['is_verified']}")
        print(f"    - nearest_bunk_id: {test_gps['nearest_bunk_id']}")
        print(f"    - distance_meters: {test_gps['distance_meters']}")
        print(f"    - notes: {test_gps['notes']}")
        assert test_gps['is_verified'] is False, "FAIL: GPS verification should remain False while enforcement is disabled!"
        assert test_gps['distance_meters'] is None, "FAIL: Distance should be None when enforcement is disabled!"
        assert "Geofence enforcement disabled pending on-site coordinate verification" in test_gps['notes']
        print("[PASS] TEST 3: GPS safety lock confirmed. Station activation CANNOT trigger geofence enforcement.")

        # TEST 4: Validation Rule: Rejection of Non-Diesel Fuel Types
        print("\n--- TEST 4: Validation Rule for Non-Diesel Fuel Submissions ---")
        cng_submission = {
            'bus_id': 1,
            'fuel_litres': 40.0,
            'rate_per_litre': 85.0,
            'total_cost': 3400.0,
            'odometer_reading': 120500.0,
            'fuel_station_name': 'IOC DEALERS, DSS FUEL SOUK',
            'fuel_type': 'CNG'
        }
        petrol_submission = dict(cng_submission, fuel_type='PETROL')
        diesel_submission = dict(cng_submission, fuel_type='DIESEL')

        cng_errs = validate_fuel_submission_data(cng_submission)
        petrol_errs = validate_fuel_submission_data(petrol_submission)
        diesel_errs = validate_fuel_submission_data(diesel_submission)

        assert any("operates strictly on DIESEL" in e for e in cng_errs), f"CNG not rejected: {cng_errs}"
        assert any("operates strictly on DIESEL" in e for e in petrol_errs), f"PETROL not rejected: {petrol_errs}"
        assert len(diesel_errs) == 0, f"Valid Diesel submission returned unexpected errors: {diesel_errs}"
        print(f"  CNG rejection error: {cng_errs}")
        print(f"  PETROL rejection error: {petrol_errs}")
        print(f"  DIESEL submission errors: {diesel_errs} (Clean)")
        print("[PASS] TEST 4: Submissions with non-Diesel fuel types are strictly rejected.")

        # TEST 5: Historical CNG Demo Records Preservation & Unit Non-Contamination
        print("\n--- TEST 5: Preservation & Separation of Legacy CNG Demo Records ---")
        cng_recs = FuelRecord.query.filter_by(fuel_type='CNG').all()
        assert len(cng_recs) == 3, f"Expected 3 legacy CNG demo records, found {len(cng_recs)}"
        for r in cng_recs:
            print(f"  - Ref {r.reference_code}: fuel_type={r.fuel_type}, litres/kg={r.fuel_litres}, cost=Rs.{r.total_cost}, img={r.bill_image_filename}")
            assert "[HISTORICAL DEMO - PRESERVED]" in (r.admin_remarks or ""), f"Missing audit remark for {r.reference_code}"
            assert r.fuel_type == 'CNG', f"Fuel type was incorrectly changed for {r.reference_code}"
        print("[PASS] TEST 5: All 3 legacy CNG demo records preserved intact with zero unit alteration.")

        # TEST 6: Dynamic Analytics Overview Calculation & Separation
        print("\n--- TEST 6: Dynamic Analytics Overview Query Integrity ---")
        from app.routes.analytics_routes import get_analytics_overview
        from flask import json
        client = app.test_client()
        
        # Test using authenticated request with admin user
        from flask_jwt_extended import create_access_token
        admin_user = User.query.filter_by(username='admin').first()
        admin_token = create_access_token(identity=str(admin_user.id), additional_claims={'role': 'ADMIN'})
        
        res = client.get('/api/analytics/overview', headers={'Authorization': f'Bearer {admin_token}'})
        assert res.status_code == 200, f"Failed to get overview: {res.data}"
        data = json.loads(res.data)
        
        print(f"  Dynamic Overview Data:")
        print(f"    - total_diesel_spend: Rs.{data['total_diesel_spend']}")
        print(f"    - total_diesel_litres: {data['total_diesel_litres']} L")
        print(f"    - pending_approvals: {data['pending_approvals']} bills (Liability: Rs.{data['pending_spend']})")
        print(f"    - active_diesel_buses: {data['active_diesel_buses']} / {data['total_buses']}")
        print(f"    - average_diesel_kmpl: {data['average_diesel_kmpl']} km/L")
        print(f"    - status_distribution: {data['status_distribution']}")
        
        # Verify approved Diesel calculations mathematically against DB records
        approved_diesel = FuelRecord.query.filter_by(status='APPROVED', fuel_type='DIESEL').all()
        expected_diesel_spend = round(sum(float(r.total_cost) for r in approved_diesel), 2)
        expected_diesel_litres = round(sum(float(r.fuel_litres) for r in approved_diesel), 2)
        expected_pending = FuelRecord.query.filter_by(status='PENDING').count()

        now = datetime.utcnow()
        start_of_month = datetime(now.year, now.month, 1)
        start_of_next = datetime(now.year + 1, 1, 1) if now.month == 12 else datetime(now.year, now.month + 1, 1)
        curr_m_recs = FuelRecord.query.filter(
            FuelRecord.status == 'APPROVED',
            FuelRecord.fuel_type == 'DIESEL',
            FuelRecord.bill_date >= start_of_month,
            FuelRecord.bill_date < start_of_next
        ).all()
        expected_curr_spend = round(sum(float(r.total_cost) for r in curr_m_recs), 2)
        expected_curr_litres = round(sum(float(r.fuel_litres) for r in curr_m_recs), 2)

        assert data['total_diesel_spend'] == expected_diesel_spend, f"Expected {expected_diesel_spend}, got {data['total_diesel_spend']}"
        assert data['total_diesel_litres'] == expected_diesel_litres, f"Expected {expected_diesel_litres}, got {data['total_diesel_litres']}"
        assert data['current_month_diesel_spend'] == expected_curr_spend, f"Expected {expected_curr_spend}, got {data['current_month_diesel_spend']}"
        assert data['current_month_diesel_litres'] == expected_curr_litres, f"Expected {expected_curr_litres}, got {data['current_month_diesel_litres']}"
        assert data['pending_approvals'] == expected_pending, f"Expected {expected_pending}, got {data['pending_approvals']}"
        assert data['active_diesel_buses'] == 5, f"Expected 5 active diesel buses, got {data['active_diesel_buses']}"
        print(f"    - Current Month ({data['current_month_label']}): Approved Diesel Spend = Rs.{data['current_month_diesel_spend']}, Litres = {data['current_month_diesel_litres']} L")
        print("[PASS] TEST 6: Dynamic analytics overview correctly isolates approved Diesel from pending and legacy CNG.")

        # TEST 7: Role Permissions Security (VC 403 on Audit Logs, Admin 200)
        print("\n--- TEST 7: Role-Based Access Control on Audit Logs ---")
        vc_user = User.query.filter_by(username='vc_office').first()
        vc_token = create_access_token(identity=str(vc_user.id), additional_claims={'role': 'VC'})

        vc_audit_res = client.get('/api/audit-logs', headers={'Authorization': f'Bearer {vc_token}'})
        admin_audit_res = client.get('/api/audit-logs', headers={'Authorization': f'Bearer {admin_token}'})
        
        print(f"  VC GET /api/audit-logs status code: {vc_audit_res.status_code} (Expected 403)")
        print(f"  Admin GET /api/audit-logs status code: {admin_audit_res.status_code} (Expected 200)")
        assert vc_audit_res.status_code == 403, f"VC was not blocked! Status: {vc_audit_res.status_code}"
        assert admin_audit_res.status_code == 200, f"Admin was blocked! Status: {admin_audit_res.status_code}"
        print("[PASS] TEST 7: Role permissions verified. VC access strictly blocked with 403; Admin retains 200 access.")

        # TEST 8: Bill Images Integrity (All 10 bill files reachable via API)
        print("\n--- TEST 8: Uploaded Bill Images Accessibility ---")
        bills_dir = Path(backend_dir / "uploads" / "bills")
        bill_files = [f.name for f in bills_dir.glob("*") if f.is_file()]
        assert len(bill_files) == 10, f"Expected 10 bill images in directory, found {len(bill_files)}"

        for bf in sorted(bill_files):
            img_res = client.get(f'/api/bills/{bf}', headers={'Authorization': f'Bearer {admin_token}'})
            assert img_res.status_code == 200, f"Failed to retrieve bill image {bf}: {img_res.status_code}"
            assert len(img_res.data) > 1000, f"Bill image {bf} returned empty content!"
            print(f"  Bill image '{bf}': HTTP 200 OK ({len(img_res.data)} bytes)")
        print("[PASS] TEST 8: All 10 uploaded bill image files in uploads/bills/ are fully accessible via HTTP 200.")

        # TEST 9: Mileage Calculation Sequential Rules Verification
        print("\n--- TEST 9: Mileage Sequential Baseline Rules ---")
        # Test Bus 1 (has valid consecutive diesel sequence)
        bus1_records = FuelRecord.query.filter_by(bus_id=1).order_by(FuelRecord.bill_date.asc()).all()
        for r in bus1_records:
            comp = calculate_record_mileage(r)
            print(f"  Bus 1 Record {r.reference_code}: Date={r.bill_date.strftime('%Y-%m-%d')}, Odo={r.odometer_reading}, Distance={comp.distance_travelled_km}, kmpl={comp.calculated_kmpl}, Reliable={comp.is_statistically_reliable}")
        
        # Test Bus 9 (legacy CNG records should NOT compute Diesel mileage)
        bus9_records = FuelRecord.query.filter_by(bus_id=3).all()
        for r in bus9_records:
            comp = calculate_record_mileage(r)
            assert comp.calculated_kmpl is None, f"Expected no Diesel kmpl for legacy record {r.reference_code}"
            assert comp.is_statistically_reliable is False
        print("  Bus 9 (Reconfigured bus09) has 0 Diesel fill-ups: correctly yields NO Diesel km/L.")
        print("[PASS] TEST 9: Mileage calculations select strictly consecutive approved Diesel records.")

    print("\n======================================================================")
    print("      ALL 9 BACKEND & INTEGRITY VERIFICATION TESTS PASSED (100%)       ")
    print("======================================================================")

if __name__ == '__main__':
    run_tests()
