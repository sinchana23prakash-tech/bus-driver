import sys
from pathlib import Path
from datetime import datetime

backend_dir = Path(r"C:\Users\PC\.gemini\antigravity\scratch\college_bus_fuel_system\backend")
sys.path.insert(0, str(backend_dir))

from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()

def run_migration():
    print("=== EXECUTING DATABASE MIGRATION ===")
    with app.app_context():
        # Verify active database
        active_db = db.session.execute(text("SELECT DATABASE()")).scalar()
        print(f"[VERIFY] Connected to MySQL active database: '{active_db}'")
        assert active_db == 'college_bus_fuel_db', f"Active DB mismatch! Expected 'college_bus_fuel_db', got '{active_db}'"

        # 1. Update bus09 to DIESEL
        print("\n[STEP 1] Reconfiguring bus09 (id=3) to DIESEL...")
        db.session.execute(text("""
            UPDATE buses 
            SET fuel_type = 'DIESEL', updated_at = NOW() 
            WHERE id = 3 AND bus_number = 'bus09'
        """))
        
        # Verify all 5 buses are DIESEL
        buses = db.session.execute(text("SELECT id, bus_number, fuel_type FROM buses")).fetchall()
        print("Fleet fuel configurations:")
        for b_id, b_num, f_type in buses:
            print(f"  - Bus {b_num} (ID {b_id}): {f_type}")
            assert f_type == 'DIESEL', f"Bus {b_num} is not DIESEL!"
        print("[OK] All 5 college buses are configured as DIESEL.")

        # 2. Annotate historical CNG demo records for traceability
        print("\n[STEP 2] Preserving & annotating historical CNG demo records (DEMO-FL-D301, D302, D303)...")
        cng_remark_note = " [HISTORICAL DEMO - PRESERVED]: Seeded synthetic CNG test record (originally recorded in kilograms). Preserved intact for audit traceability; strictly excluded from institutional Diesel volume (Litres) and Diesel km/L fleet calculations."
        
        for ref in ['DEMO-FL-D301', 'DEMO-FL-D302', 'DEMO-FL-D303']:
            row = db.session.execute(text("SELECT id, reference_code, fuel_type, fuel_litres, admin_remarks FROM fuel_records WHERE reference_code = :ref"), {"ref": ref}).fetchone()
            assert row is not None, f"Record {ref} not found!"
            current_remark = row[4] or ""
            if "[HISTORICAL DEMO - PRESERVED]" not in current_remark:
                new_remark = (current_remark + cng_remark_note).strip()
                db.session.execute(text("""
                    UPDATE fuel_records 
                    SET admin_remarks = :rmk, updated_at = NOW() 
                    WHERE reference_code = :ref
                """), {"rmk": new_remark, "ref": ref})
            print(f"  - Verified {ref}: fuel_type={row[2]} ({row[3]} kg), annotated in admin_remarks.")
        print("[OK] Historical CNG demo records preserved intact with audit annotations.")

        # 3. Configure single active station and deactivate bunks 2 and 3
        print("\n[STEP 3] Updating approved fuel stations configuration...")
        # Bunk 1: IOC DEALERS, DSS FUEL SOUK
        db.session.execute(text("""
            UPDATE approved_petrol_bunks 
            SET name = 'IOC DEALERS, DSS FUEL SOUK',
                address = '510, Davangere - Harihar Rd, near GMIT COLLEGE, Doddabathi, Karnataka 577006',
                latitude = 14.47626000,
                longitude = 75.88508000,
                geofence_radius_meters = 500,
                is_active = 1,
                updated_at = NOW()
            WHERE id = 1
        """))

        # Bunk 2: Deactivate BPCL
        db.session.execute(text("""
            UPDATE approved_petrol_bunks 
            SET name = '[INACTIVE] BPCL Highway Station',
                is_active = 0,
                updated_at = NOW()
            WHERE id = 2
        """))

        # Bunk 3: Deactivate HPCL
        db.session.execute(text("""
            UPDATE approved_petrol_bunks 
            SET name = '[INACTIVE] HPCL Tech Park Point',
                is_active = 0,
                updated_at = NOW()
            WHERE id = 3
        """))

        # Verify active station count
        active_bunks = db.session.execute(text("SELECT id, name, is_active FROM approved_petrol_bunks WHERE is_active = 1")).fetchall()
        inactive_bunks = db.session.execute(text("SELECT id, name, is_active FROM approved_petrol_bunks WHERE is_active = 0")).fetchall()
        
        print(f"Active stations ({len(active_bunks)}):")
        for b_id, b_name, b_act in active_bunks:
            print(f"  - ID {b_id}: {b_name} (Active={b_act})")
        assert len(active_bunks) == 1, f"Expected 1 active bunk, got {len(active_bunks)}"
        assert active_bunks[0][0] == 1, f"Expected Bunk 1 to be active, got {active_bunks[0][0]}"

        print(f"Inactive stations ({len(inactive_bunks)}):")
        for b_id, b_name, b_act in inactive_bunks:
            print(f"  - ID {b_id}: {b_name} (Active={b_act})")
        assert len(inactive_bunks) == 2, f"Expected 2 inactive bunks, got {len(inactive_bunks)}"

        # 4. Insert Audit Log Entries
        print("\n[STEP 4] Logging realignment audit entries...")
        db.session.execute(text("""
            INSERT INTO audit_logs (actor_id, actor_role, action, entity_type, entity_id, details, created_at)
            VALUES 
            (1, 'ADMIN', 'REALIGNMENT_BUS_FUEL', 'BUS', 3, 'Reconfigured bus09 fuel type to DIESEL for institutional standardization', NOW()),
            (1, 'ADMIN', 'REALIGNMENT_BUNK_CONFIG', 'APPROVED_PETROL_BUNK', 1, 'Configured single approved fuel station: IOC DEALERS, DSS FUEL SOUK. Deactivated bunks 2 and 3.', NOW())
        """))

        db.session.commit()
        print("[OK] Database transaction committed successfully.")

        # 5. Verify Foreign Key References
        orphan_refs = db.session.execute(text("""
            SELECT COUNT(*) FROM fuel_records fr
            LEFT JOIN approved_petrol_bunks apb ON fr.gps_nearest_bunk_id = apb.id
            WHERE fr.gps_nearest_bunk_id IS NOT NULL AND apb.id IS NULL
        """)).scalar()
        assert orphan_refs == 0, f"Found {orphan_refs} orphan foreign key references!"
        print(f"[OK] Foreign-key references verified: 0 broken links.")

        print("\n=== DATABASE MIGRATION COMPLETED SUCCESSFULLY ===")

if __name__ == '__main__':
    run_migration()
