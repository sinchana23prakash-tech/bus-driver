import os
import sys
from pathlib import Path

# Ensure backend root is on path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from dotenv import load_dotenv
load_dotenv(BASE_DIR.parent / '.env')

from sqlalchemy import create_engine, text, inspect
from app.extensions import db
from app.models.user import User
from app.models.bus import Bus
from app.models.petrol_bunk import ApprovedPetrolBunk
from app.models.fuel_record import FuelRecord
from app.models.mileage import MileageComputation
from app.models.audit_log import AuditLog
from config import Config

def migrate(mysql_password=None, mysql_user=None, mysql_host=None, mysql_port=None, mysql_db=None):
    sqlite_path = Config.SQLITE_PATH
    if not os.path.exists(sqlite_path):
        print(f"[ERROR] Source SQLite database not found at {sqlite_path}")
        return False

    host = mysql_host or Config.MYSQL_HOST
    port = mysql_port or Config.MYSQL_PORT
    user = mysql_user or Config.MYSQL_USER
    pwd = mysql_password or Config.MYSQL_PASSWORD
    dbname = mysql_db or Config.MYSQL_DATABASE

    print("=======================================================")
    print(" SQLite -> MySQL Data Migration Tool")
    print("=======================================================")
    print(f"Source SQLite DB : {sqlite_path}")
    print(f"Target MySQL Host: {host}:{port}")
    print(f"Target Database  : {dbname}")
    print(f"MySQL User       : {user}")

    # 1. Connect to MySQL server (first without db to ensure db exists)
    server_uri = f"mysql+pymysql://{user}:{pwd}@{host}:{port}/?charset=utf8mb4"
    try:
        server_engine = create_engine(server_uri, connect_args={'connect_timeout': 5})
        with server_engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{dbname}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))
            conn.commit()
        print(f"[OK] Database `{dbname}` verified/created on MySQL server.")
    except Exception as e:
        print(f"[ERROR] Failed to connect to MySQL server: {e}")
        return False

    # 2. Connect to target MySQL database and SQLite
    mysql_uri = f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{dbname}?charset=utf8mb4"
    mysql_engine = create_engine(mysql_uri)
    sqlite_engine = create_engine(f"sqlite:///{sqlite_path}")

    # 3. Create tables on MySQL using app models
    from app import create_app
    app = create_app(Config)
    with app.app_context():
        # Temporarily point app engine to MySQL
        app.config['SQLALCHEMY_DATABASE_URI'] = mysql_uri
        db.metadata.create_all(bind=mysql_engine)
        print("[OK] MySQL schema and tables created/verified.")

    # 4. Migrate tables in topological order
    tables_to_migrate = [
        'users',
        'approved_petrol_bunks',
        'buses',
        'fuel_records',
        'mileage_computations',
        'audit_logs'
    ]

    sqlite_inspector = inspect(sqlite_engine)
    available_sqlite_tables = sqlite_inspector.get_table_names()

    with mysql_engine.connect() as mysql_conn, sqlite_engine.connect() as sqlite_conn:
        mysql_conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        mysql_conn.commit()

        for tbl in tables_to_migrate:
            if tbl not in available_sqlite_tables:
                print(f"[SKIP] Table `{tbl}` does not exist in SQLite.")
                continue

            rows = sqlite_conn.execute(text(f"SELECT * FROM `{tbl}`")).mappings().all()
            if not rows:
                print(f"Table `{tbl}`: 0 rows in SQLite.")
                continue

            # Fetch existing IDs in MySQL to avoid duplicates
            existing_ids = set()
            try:
                res = mysql_conn.execute(text(f"SELECT id FROM `{tbl}`")).fetchall()
                existing_ids = {r[0] for r in res}
            except Exception:
                pass

            inserted_count = 0
            for row in rows:
                row_dict = dict(row)
                if row_dict.get('id') in existing_ids:
                    continue

                cols = list(row_dict.keys())
                col_names = ", ".join([f"`{c}`" for c in cols])
                param_names = ", ".join([f":{c}" for c in cols])
                insert_stmt = text(f"INSERT INTO `{tbl}` ({col_names}) VALUES ({param_names})")
                mysql_conn.execute(insert_stmt, row_dict)
                inserted_count += 1

            mysql_conn.commit()
            print(f"[OK] Table `{tbl}`: {len(rows)} source rows -> {inserted_count} new inserted (existing: {len(existing_ids)}).")

        mysql_conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        mysql_conn.commit()

    print("=======================================================")
    print(" Migration completed successfully!")
    print("=======================================================")
    return True

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Migrate College Bus Fuel SQLite data to MySQL")
    parser.add_argument("--password", help="MySQL password")
    parser.add_argument("--user", help="MySQL user", default=None)
    args = parser.parse_args()

    success = migrate(mysql_password=args.password, mysql_user=args.user)
    sys.exit(0 if success else 1)
