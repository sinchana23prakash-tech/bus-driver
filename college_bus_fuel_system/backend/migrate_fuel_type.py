import os
import sys
import shutil
from datetime import datetime
from pathlib import Path

# Add backend to sys.path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()

def backup_and_migrate():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    print(f"=== PHASE 1: BACKUP AND MIGRATION ({timestamp}) ===")

    # 1. Backup uploaded bills
    bills_src = backend_dir / "app" / "uploads" / "bills"
    bills_backup = backend_dir / f"bills_backup_{timestamp}"
    if bills_src.exists():
        shutil.copytree(str(bills_src), str(bills_backup))
        src_files = list(bills_src.glob('*'))
        dst_files = list(bills_backup.glob('*'))
        print(f"[OK] Bills backed up: {len(src_files)} files copied to {bills_backup.name}")
    else:
        print("[WARN] bills_src directory does not exist, creating it")
        bills_src.mkdir(parents=True, exist_ok=True)

    # 2. Database Backup (Native SQL dump via SQLAlchemy to ensure 100% reliable backup without depending on mysqldump path)
    backup_file = backend_dir / f"backup_pre_improvements_{timestamp}.sql"
    with app.app_context():
        tables = ['users', 'buses', 'approved_petrol_bunks', 'fuel_records', 'mileage_computations', 'audit_logs']
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(f"-- College Bus Fuel DB Pre-Improvements Backup\n-- Date: {datetime.now().isoformat()}\n\n")
            for t in tables:
                f.write(f"-- Table: {t}\n")
                # Structure
                create_res = db.session.execute(text(f"SHOW CREATE TABLE {t}")).fetchone()
                if create_res:
                    f.write(f"{create_res[1]};\n\n")
                # Rows
                rows = db.session.execute(text(f"SELECT * FROM {t}")).fetchall()
                if rows:
                    col_names = [col[0] for col in db.session.execute(text(f"DESCRIBE {t}")).fetchall()]
                    cols_str = ", ".join(f"`{c}`" for c in col_names)
                    for r in rows:
                        vals = []
                        for v in r:
                            if v is None:
                                vals.append("NULL")
                            elif isinstance(v, (int, float)):
                                vals.append(str(v))
                            elif isinstance(v, bool):
                                vals.append("1" if v else "0")
                            else:
                                escaped = str(v).replace("'", "''").replace("\\", "\\\\")
                                vals.append(f"'{escaped}'")
                        f.write(f"INSERT INTO `{t}` ({cols_str}) VALUES ({', '.join(vals)});\n")
                    f.write("\n")
        
        backup_size = backup_file.stat().st_size
        print(f"[OK] Database backed up to {backup_file.name} ({backup_size} bytes)")
        assert backup_size > 5000, "Backup file size too small!"

        # 3. Check existing columns in fuel_records
        cols = [c[0] for c in db.session.execute(text("DESCRIBE fuel_records")).fetchall()]
        if 'fuel_type' not in cols:
            print("[INFO] Adding column `fuel_type` to fuel_records...")
            db.session.execute(text("ALTER TABLE fuel_records ADD COLUMN fuel_type VARCHAR(20) NOT NULL DEFAULT 'DIESEL'"))
            db.session.commit()
            print("[OK] Column `fuel_type` added successfully.")
        else:
            print("[INFO] Column `fuel_type` already exists in fuel_records.")

        # 4. Backfill from buses
        print("[INFO] Backfilling fuel_type from buses table...")
        update_res = db.session.execute(text("""
            UPDATE fuel_records fr
            JOIN buses b ON fr.bus_id = b.id
            SET fr.fuel_type = b.fuel_type
        """))
        db.session.commit()
        print(f"[OK] Backfilled fuel_type from buses.")

        # 5. Verification
        total_records = db.session.execute(text("SELECT COUNT(*) FROM fuel_records")).scalar()
        null_records = db.session.execute(text("SELECT COUNT(*) FROM fuel_records WHERE fuel_type IS NULL OR fuel_type = ''")).scalar()
        distribution = db.session.execute(text("SELECT fuel_type, COUNT(*) FROM fuel_records GROUP BY fuel_type")).fetchall()
        
        print("\n=== VERIFICATION ===")
        print(f"Total fuel_records: {total_records}")
        print(f"Records with NULL/empty fuel_type: {null_records}")
        assert null_records == 0, "Found records with NULL fuel_type!"
        print("Fuel type distribution in fuel_records:")
        for ft, cnt in distribution:
            print(f"  - {ft}: {cnt}")
        
        # Check consistency with buses
        mismatches = db.session.execute(text("""
            SELECT fr.id, fr.reference_code, b.bus_number, b.fuel_type AS bus_fuel, fr.fuel_type AS rec_fuel
            FROM fuel_records fr
            JOIN buses b ON fr.bus_id = b.id
            WHERE fr.fuel_type != b.fuel_type
        """)).fetchall()
        print(f"Mismatches with bus configuration: {len(mismatches)}")
        assert len(mismatches) == 0, f"Found {len(mismatches)} mismatches!"

        print("\n[SUCCESS] Phase 1 Backup & Migration completed cleanly.\n")

if __name__ == '__main__':
    backup_and_migrate()
