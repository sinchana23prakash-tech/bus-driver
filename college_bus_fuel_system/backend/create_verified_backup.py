import os
import sys
import shutil
import hashlib
import uuid
from datetime import datetime
from pathlib import Path

backend_dir = Path(r"C:\Users\PC\.gemini\antigravity\scratch\college_bus_fuel_system\backend")
sys.path.insert(0, str(backend_dir))

from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()

def run_backup_and_verification():
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    print(f"=== STEP 1: CODE & IMAGE MANIFEST BACKUP ({ts}) ===")

    # 1. Code backup
    code_backup_dir = backend_dir / f"code_backup_{ts}"
    code_backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy backend app folder
    shutil.copytree(str(backend_dir / "app"), str(code_backup_dir / "backend_app"), dirs_exist_ok=True)
    
    # Copy frontend src folder
    frontend_src = backend_dir.parent / "frontend" / "src"
    if frontend_src.exists():
        shutil.copytree(str(frontend_src), str(code_backup_dir / "frontend_src"), dirs_exist_ok=True)
    print(f"[OK] Source code backed up to: {code_backup_dir.name}")

    # 2. Bill Images SHA-256 Manifest
    bills_dir = backend_dir / "uploads" / "bills"
    manifest_file = backend_dir / f"bill_images_manifest_{ts}.json"
    manifest_data = {}
    if bills_dir.exists():
        for img_path in sorted(bills_dir.glob("*")):
            if img_path.is_file():
                h = hashlib.sha256(img_path.read_bytes()).hexdigest()
                manifest_data[img_path.name] = {
                    "size_bytes": img_path.stat().st_size,
                    "sha256": h
                }
    import json
    with open(manifest_file, "w", encoding="utf-8") as mf:
        json.dump(manifest_data, mf, indent=2)
    print(f"[OK] Bill images manifest generated: {len(manifest_data)} files recorded in {manifest_file.name}")
    assert len(manifest_data) == 10, f"Expected 10 bill images, found {len(manifest_data)}!"

    # 3. MySQL Database Dump
    print(f"\n=== STEP 2: MYSQL DATABASE BACKUP ({ts}) ===")
    backup_file = backend_dir / f"backup_realignment_{ts}.sql"
    tables = ['users', 'buses', 'approved_petrol_bunks', 'fuel_records', 'mileage_computations', 'audit_logs']

    with app.app_context():
        # Verify active database
        active_db = db.session.execute(text("SELECT DATABASE()")).scalar()
        print(f"[VERIFY] Connected to MySQL active database: '{active_db}'")
        assert active_db == 'college_bus_fuel_db', f"Active DB mismatch! Expected 'college_bus_fuel_db', got '{active_db}'"

        # Record baseline row counts
        baseline_counts = {}
        for t in tables:
            cnt = db.session.execute(text(f"SELECT COUNT(*) FROM `{t}`")).scalar()
            baseline_counts[t] = cnt
            print(f"  - Baseline table `{t}`: {cnt} rows")

        assert baseline_counts['users'] == 7, f"Expected 7 users, got {baseline_counts['users']}"
        assert baseline_counts['buses'] == 5, f"Expected 5 buses, got {baseline_counts['buses']}"
        assert baseline_counts['approved_petrol_bunks'] == 3, f"Expected 3 bunks, got {baseline_counts['approved_petrol_bunks']}"
        assert baseline_counts['fuel_records'] == 16, f"Expected 16 fuel records, got {baseline_counts['fuel_records']}"

        # Write clean SQL dump
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(f"-- College Bus Fuel DB Realignment Backup\n-- Date: {datetime.now().isoformat()}\n-- Database: college_bus_fuel_db\n\n")
            for t in tables:
                f.write(f"-- Table structure for `{t}`\n")
                f.write(f"DROP TABLE IF EXISTS `{t}`;\n")
                create_res = db.session.execute(text(f"SHOW CREATE TABLE `{t}`")).fetchone()
                f.write(f"{create_res[1]};\n\n")

                f.write(f"-- Table data for `{t}`\n")
                rows = db.session.execute(text(f"SELECT * FROM `{t}`")).fetchall()
                if rows:
                    col_names = [col[0] for col in db.session.execute(text(f"DESCRIBE `{t}`")).fetchall()]
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
                                escaped = str(v).replace("\\", "\\\\").replace("'", "\\'")
                                vals.append(f"'{escaped}'")
                        f.write(f"INSERT INTO `{t}` ({cols_str}) VALUES ({', '.join(vals)});\n")
                    f.write("\n")

        backup_size = backup_file.stat().st_size
        backup_sha = hashlib.sha256(backup_file.read_bytes()).hexdigest()
        print(f"[OK] Database backed up to: {backup_file.name} ({backup_size} bytes)")
        print(f"[OK] Backup SHA-256: {backup_sha}")

        # 4. Isolated Test Restore Verification
        print(f"\n=== STEP 3: ISOLATED RESTORE VERIFICATION IN TEMPORARY SANDBOX DB ===")
        rand_hex = uuid.uuid4().hex[:8]
        tmp_db_name = f"tmp_verify_{ts}_{rand_hex}"
        print(f"[CHECK] Checking if temporary database '{tmp_db_name}' already exists...")
        exists = db.session.execute(
            text("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = :db_name"),
            {"db_name": tmp_db_name}
        ).scalar()
        if exists:
            raise RuntimeError(f"FATAL: Database {tmp_db_name} already exists! Aborting verification.")

        print(f"[OK] Database '{tmp_db_name}' does not exist. Creating isolated test database...")
        db.session.execute(text(f"CREATE DATABASE `{tmp_db_name}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
        
        try:
            # Connect to isolated database
            engine_url = str(db.engine.url)
            # Create a direct connection to the new database
            from sqlalchemy import create_engine
            tmp_url = db.engine.url.set(database=tmp_db_name)
            tmp_engine = create_engine(tmp_url)
            
            with tmp_engine.connect() as tmp_conn:
                # Read SQL file statements
                sql_content = backup_file.read_text(encoding='utf-8')
                statements = []
                current_stmt = []
                for line in sql_content.splitlines():
                    if line.startswith('--') or not line.strip():
                        continue
                    current_stmt.append(line)
                    if line.strip().endswith(';'):
                        statements.append("\n".join(current_stmt))
                        current_stmt = []

                print(f"[INFO] Executing {len(statements)} statements in '{tmp_db_name}'...")
                # Temporarily disable foreign key checks for clean restore
                tmp_conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
                for stmt in statements:
                    tmp_conn.execute(text(stmt))
                tmp_conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))
                tmp_conn.commit()

                # Validate restored table row counts
                print("[VERIFY] Validating restored row counts in isolated database:")
                for t in tables:
                    restored_cnt = tmp_conn.execute(text(f"SELECT COUNT(*) FROM `{t}`")).scalar()
                    print(f"  - `{t}`: Restored {restored_cnt} rows (Expected {baseline_counts[t]})")
                    assert restored_cnt == baseline_counts[t], f"Row count mismatch for `{t}` in restored database!"
                
                # Validate foreign keys
                fk_valid = tmp_conn.execute(text("""
                    SELECT COUNT(*) FROM fuel_records fr
                    LEFT JOIN buses b ON fr.bus_id = b.id
                    WHERE b.id IS NULL
                """)).scalar()
                assert fk_valid == 0, "Found broken foreign key references in restored database!"
                print("[OK] Foreign-key relationships verified intact in restored database.")

            print(f"[SUCCESS] Isolated test restore passed 100% cleanly in '{tmp_db_name}'.")

        finally:
            print(f"[CLEANUP] Safely dropping ONLY the temporary test database '{tmp_db_name}'...")
            db.session.execute(text(f"DROP DATABASE IF EXISTS `{tmp_db_name}`"))
            print(f"[OK] Temporary database '{tmp_db_name}' safely removed. Live database untouched.")

    print("\n=== PHASE 1 VERIFICATION COMPLETED WITH ZERO ERRORS ===")

if __name__ == '__main__':
    run_backup_and_verification()
