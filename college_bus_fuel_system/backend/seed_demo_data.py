import os
import sys
import subprocess
from datetime import datetime
from decimal import Decimal
from pathlib import Path

# Ensure backend directory is in python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from dotenv import load_dotenv
load_dotenv(BASE_DIR.parent / '.env')

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.bus import Bus
from app.models.petrol_bunk import ApprovedPetrolBunk
from app.models.fuel_record import FuelRecord
from app.models.mileage import MileageComputation
from app.models.audit_log import AuditLog
from config import Config

def backup_database():
    """
    Backs up the MySQL database before performing any seeding.
    Terminates if backup fails or file is empty.
    """
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    backup_file = BASE_DIR / f"backup_college_bus_fuel_db_{timestamp}.sql"
    
    print("=" * 65)
    print(" STEP 1: BACKING UP DATABASE BEFORE ANY MODIFICATIONS")
    print("=" * 65)
    print(f"Target backup file: {backup_file}")

    # Check for mysqldump executable
    mysqldump_candidates = [
        r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe",
        r"C:\Program Files\MySQL\MySQL Workbench 8.0\mysqldump.exe",
        "mysqldump"
    ]
    dump_bin = None
    for cand in mysqldump_candidates:
        if os.path.isabs(cand) and os.path.exists(cand):
            dump_bin = cand
            break
        elif not os.path.isabs(cand):
            # Check PATH
            from shutil import which
            if which(cand):
                dump_bin = cand
                break

    success = False
    if dump_bin:
        cmd = [
            dump_bin,
            "-h", Config.MYSQL_HOST,
            "-P", str(Config.MYSQL_PORT),
            "-u", Config.MYSQL_USER,
            f"--password={Config.MYSQL_PASSWORD}",
            "--databases", Config.MYSQL_DATABASE,
            "--routines",
            "--triggers",
            "--result-file=" + str(backup_file)
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if res.returncode == 0 and backup_file.exists() and backup_file.stat().st_size > 0:
                print(f"[OK] mysqldump completed successfully: {backup_file.stat().st_size} bytes written.")
                success = True
            else:
                print(f"[!] mysqldump exited with returncode {res.returncode}. Error: {res.stderr[:200]}")
        except Exception as e:
            print(f"[!] mysqldump execution failed: {e}")

    # If mysqldump wasn't available or failed, run python-native table DDL and data backup
    if not success:
        print("[*] Performing Python-native SQL table and data dump...")
        try:
            from sqlalchemy import create_engine, text, inspect
            eng = create_engine(Config.get_database_uri())
            insp = inspect(eng)
            tables = insp.get_table_names()

            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(f"-- College Bus Fuel Management System SQL Dump\n")
                f.write(f"-- Generated on: {datetime.utcnow().isoformat()} UTC\n")
                f.write(f"-- Database: {Config.MYSQL_DATABASE}\n\n")
                f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")

                with eng.connect() as conn:
                    for tbl in tables:
                        f.write(f"-- Table structure for table `{tbl}`\n")
                        show_create = conn.execute(text(f"SHOW CREATE TABLE `{tbl}`")).fetchone()
                        if show_create and len(show_create) > 1:
                            f.write(f"{show_create[1]};\n\n")

                        f.write(f"-- Dumping data for table `{tbl}`\n")
                        rows = conn.execute(text(f"SELECT * FROM `{tbl}`")).mappings().all()
                        for r in rows:
                            cols = [f"`{k}`" for k in r.keys()]
                            vals = []
                            for v in r.values():
                                if v is None:
                                    vals.append("NULL")
                                elif isinstance(v, (int, float, Decimal)):
                                    vals.append(str(v))
                                elif isinstance(v, datetime):
                                    vals.append(f"'{v.strftime('%Y-%m-%d %H:%M:%S')}'")
                                else:
                                    escaped = str(v).replace("\\", "\\\\").replace("'", "\\'")
                                    vals.append(f"'{escaped}'")
                            f.write(f"INSERT INTO `{tbl}` ({', '.join(cols)}) VALUES ({', '.join(vals)});\n")
                        f.write("\n")

                    f.write("SET FOREIGN_KEY_CHECKS = 1;\n")

            if backup_file.exists() and backup_file.stat().st_size > 0:
                print(f"[OK] Python-native SQL dump completed: {backup_file.stat().st_size} bytes written.")
                success = True
        except Exception as e:
            print(f"[ERROR] Native dump failed: {e}")
            success = False

    if not success or not backup_file.exists() or backup_file.stat().st_size == 0:
        print("[FATAL] Backup could not be verified. Aborting execution without making any database changes.")
        sys.exit(1)

    print(f"[SUCCESS] Verified valid backup at: {backup_file} ({backup_file.stat().st_size} bytes)")
    return backup_file

def seed_demo_data():
    app = create_app()

    with app.app_context():
        # Ensure database is reachable
        try:
            admin_user = User.query.filter_by(role='ADMIN').first()
            if not admin_user:
                print("[FATAL] No administrator user found in database. Cannot associate audit logs.")
                sys.exit(1)
        except Exception as e:
            print(f"[FATAL] Cannot connect to MySQL: {e}")
            sys.exit(1)

        print("\n" + "=" * 65)
        print(" STEP 2: IDEMPOTENT DEMO DATA SEEDING")
        print("=" * 65)

        stats = {
            'users_added': 0, 'users_skipped': 0,
            'buses_added': 0, 'buses_skipped': 0,
            'bunks_added': 0, 'bunks_skipped': 0,
            'records_added': 0, 'records_skipped': 0,
            'mileage_added': 0, 'audits_added': 0
        }

        # ------------------------------------------------------------------
        # 1. APPROVED PETROL BUNKS (DEMO / TEST LOCATIONS ONLY)
        # ------------------------------------------------------------------
        demo_bunks_data = [
            {
                'name': '[DEMO] IOCL Campus Auto Care (Demo Only)',
                'address': 'Gate 2 College Road, Bangalore (Demo Test Location)',
                'latitude': Decimal('12.97160000'),
                'longitude': Decimal('77.59460000'),
                'geofence_radius_meters': 500,
                'is_active': True
            },
            {
                'name': '[DEMO] BPCL Highway Station (Demo Only)',
                'address': 'Outer Ring Road Exit 4, Bangalore (Demo Test Location)',
                'latitude': Decimal('12.93520000'),
                'longitude': Decimal('77.62450000'),
                'geofence_radius_meters': 600,
                'is_active': True
            },
            {
                'name': '[DEMO] HPCL Tech Park Point (Demo Only)',
                'address': 'Campus North Extension, Bangalore (Demo Test Location)',
                'latitude': Decimal('13.03580000'),
                'longitude': Decimal('77.59700000'),
                'geofence_radius_meters': 500,
                'is_active': True
            }
        ]

        bunks_map = {}
        for b_data in demo_bunks_data:
            existing = ApprovedPetrolBunk.query.filter_by(name=b_data['name']).first()
            if existing:
                bunks_map[b_data['name']] = existing
                stats['bunks_skipped'] += 1
            else:
                new_bunk = ApprovedPetrolBunk(**b_data)
                db.session.add(new_bunk)
                db.session.flush()
                bunks_map[b_data['name']] = new_bunk
                stats['bunks_added'] += 1

                # Audit log
                db.session.add(AuditLog(
                    actor_id=admin_user.id,
                    actor_role='ADMIN',
                    action='BUNK_CONFIGURED',
                    entity_type='BUNK',
                    entity_id=new_bunk.id,
                    new_state=new_bunk.to_dict(),
                    details=f"[DEMO SETUP] Configured demo fuel station: {new_bunk.name}"
                ))
                stats['audits_added'] += 1

        db.session.commit()
        print(f"[Bunks] Added: {stats['bunks_added']}, Existing/Skipped: {stats['bunks_skipped']}")

        # ------------------------------------------------------------------
        # 2. DEMO USERS (DRIVERS & VC)
        # ------------------------------------------------------------------
        demo_users_data = [
            {
                'username': 'driver2',
                'email': 'driver2@college.edu',
                'full_name': 'Rajesh Kumar',
                'phone_number': '+91 98450 11002',
                'role': 'DRIVER',
                'password': 'DemoDriver#2026'
            },
            {
                'username': 'driver3',
                'email': 'driver3@college.edu',
                'full_name': 'Suresh Nair',
                'phone_number': '+91 98450 11003',
                'role': 'DRIVER',
                'password': 'DemoDriver#2026'
            },
            {
                'username': 'driver4',
                'email': 'driver4@college.edu',
                'full_name': 'Anand Sharma',
                'phone_number': '+91 98450 11004',
                'role': 'DRIVER',
                'password': 'DemoDriver#2026'
            },
            {
                'username': 'driver5',
                'email': 'driver5@college.edu',
                'full_name': 'Vikram Patil',
                'phone_number': '+91 98450 11005',
                'role': 'DRIVER',
                'password': 'DemoDriver#2026'
            },
            {
                'username': 'vc_office',
                'email': 'vc@college.edu',
                'full_name': 'Prof. K. R. Sharma (Vice-Chancellor)',
                'phone_number': '+91 98450 10001',
                'role': 'VC',
                'password': 'DemoAuditor#2026'
            }
        ]

        users_map = {}
        # Also map existing driver1 and admin
        for u in User.query.all():
            users_map[u.username] = u

        for u_data in demo_users_data:
            existing = User.query.filter(
                (User.username == u_data['username']) | (User.email == u_data['email'])
            ).first()
            if existing:
                users_map[existing.username] = existing
                stats['users_skipped'] += 1
            else:
                new_user = User(
                    username=u_data['username'],
                    email=u_data['email'],
                    full_name=u_data['full_name'],
                    phone_number=u_data['phone_number'],
                    role=u_data['role'],
                    is_active=True
                )
                new_user.set_password(u_data['password'])
                db.session.add(new_user)
                db.session.flush()
                users_map[new_user.username] = new_user
                stats['users_added'] += 1

                db.session.add(AuditLog(
                    actor_id=admin_user.id,
                    actor_role='ADMIN',
                    action='USER_CREATED',
                    entity_type='USER',
                    entity_id=new_user.id,
                    new_state=new_user.to_dict(),
                    details=f"[DEMO SETUP] Created {new_user.role} account: {new_user.username} ({new_user.full_name})"
                ))
                stats['audits_added'] += 1

        db.session.commit()
        print(f"[Users] Added: {stats['users_added']}, Existing/Skipped: {stats['users_skipped']}")

        # ------------------------------------------------------------------
        # 3. BUSES & DRIVER ASSIGNMENTS
        # ------------------------------------------------------------------
        demo_buses_data = [
            {
                'bus_number': 'bus04',
                'registration_number': 'KA-01-BK1044',
                'model_name': 'Ashok Leyland Viking',
                'fuel_tank_capacity': Decimal('160.00'),
                'fuel_type': 'DIESEL',
                'current_odometer': Decimal('84740.00'),
                'status': 'ACTIVE',
                'driver_username': 'driver2'
            },
            {
                'bus_number': 'bus09',
                'registration_number': 'KA-01-CK2009',
                'model_name': 'Eicher Skyline Pro',
                'fuel_tank_capacity': Decimal('140.00'),
                'fuel_type': 'CNG',
                'current_odometer': Decimal('62705.00'),
                'status': 'ACTIVE',
                'driver_username': 'driver3'
            },
            {
                'bus_number': 'bus14',
                'registration_number': 'KA-01-DK3014',
                'model_name': 'BharatBenz 1017',
                'fuel_tank_capacity': Decimal('180.00'),
                'fuel_type': 'DIESEL',
                'current_odometer': Decimal('47780.00'),
                'status': 'ACTIVE',
                'driver_username': 'driver4'
            },
            {
                'bus_number': 'bus27',
                'registration_number': 'KA-01-EK4027',
                'model_name': 'Force Traveller',
                'fuel_tank_capacity': Decimal('90.00'),
                'fuel_type': 'DIESEL',
                'current_odometer': Decimal('31380.00'),
                'status': 'ACTIVE',
                'driver_username': 'driver5'
            }
        ]

        buses_map = {}
        for b in Bus.query.all():
            buses_map[b.bus_number] = b

        for b_data in demo_buses_data:
            existing = Bus.query.filter(
                (Bus.bus_number == b_data['bus_number']) |
                (Bus.registration_number == b_data['registration_number'])
            ).first()
            driver = users_map.get(b_data['driver_username'])
            driver_id = driver.id if driver else None

            if existing:
                if existing.assigned_driver_id != driver_id:
                    existing.assigned_driver_id = driver_id
                buses_map[existing.bus_number] = existing
                stats['buses_skipped'] += 1
            else:
                new_bus = Bus(
                    bus_number=b_data['bus_number'],
                    registration_number=b_data['registration_number'],
                    model_name=b_data['model_name'],
                    fuel_tank_capacity=b_data['fuel_tank_capacity'],
                    fuel_type=b_data['fuel_type'],
                    current_odometer=b_data['current_odometer'],
                    status=b_data['status'],
                    assigned_driver_id=driver_id
                )
                db.session.add(new_bus)
                db.session.flush()
                buses_map[new_bus.bus_number] = new_bus
                stats['buses_added'] += 1

                db.session.add(AuditLog(
                    actor_id=admin_user.id,
                    actor_role='ADMIN',
                    action='BUS_CREATED',
                    entity_type='BUS',
                    entity_id=new_bus.id,
                    new_state=new_bus.to_dict(),
                    details=f"[DEMO SETUP] Registered fleet bus {new_bus.bus_number} ({new_bus.registration_number}) assigned to {b_data['driver_username']}"
                ))
                stats['audits_added'] += 1

        db.session.commit()
        print(f"[Buses] Added: {stats['buses_added']}, Existing/Skipped: {stats['buses_skipped']}")

        # ------------------------------------------------------------------
        # 4. DEMO FUEL RECORDS
        # ------------------------------------------------------------------
        # Re-check bunks and users
        bunk_iocl = bunks_map.get('[DEMO] IOCL Campus Auto Care (Demo Only)')
        bunk_bpcl = bunks_map.get('[DEMO] BPCL Highway Station (Demo Only)')
        bunk_hpcl = bunks_map.get('[DEMO] HPCL Tech Park Point (Demo Only)')

        bus20 = buses_map.get('bus20')
        bus04 = buses_map.get('bus04')
        bus09 = buses_map.get('bus09')
        bus14 = buses_map.get('bus14')
        bus27 = buses_map.get('bus27')

        d1 = users_map.get('driver1')
        d2 = users_map.get('driver2')
        d3 = users_map.get('driver3')
        d4 = users_map.get('driver4')
        d5 = users_map.get('driver5')

        # Map of planned demo records
        demo_records_data = [
            # ----------------- DRIVER 1 (bus20) -----------------
            # Safe additions for driver1 preserving existing records 1 and 2
            {
                'reference_code': 'DEMO-FL-D103',
                'bus_id': bus20.id,
                'driver_id': d1.id,
                'fuel_litres': Decimal('45.00'),
                'rate_per_litre': Decimal('89.50'),
                'total_cost': Decimal('4027.50'),
                'odometer_reading': Decimal('120225.00'),
                'fuel_station_name': '[DEMO] IOCL Campus Auto Care',
                'bill_date': datetime(2026, 10, 15, 8, 30, 0),
                'bill_image_filename': 'bill_5faaca738a7940cdbfa76f5b5c749a77.jpg',
                'bill_image_hash': 'f19c833e716116ab',
                'submission_latitude': Decimal('12.97180000'),
                'submission_longitude': Decimal('77.59470000'),
                'gps_nearest_bunk_id': bunk_iocl.id if bunk_iocl else None,
                'gps_distance_meters': Decimal('24.50'),
                'is_gps_verified': True,
                'status': 'APPROVED',
                'admin_remarks': '[DEMO] Verified against meter reading by fleet supervisor.',
                'reviewed_by': admin_user.id,
                'reviewed_at': datetime(2026, 10, 15, 10, 0, 0),
                'duplicate_flag': False,
                # Mileage: (120225 - 120000) / 45.00 = 225 / 45 = 5.00 km/L
                'distance_travelled_km': Decimal('225.00'),
                'calculated_kmpl': Decimal('5.00'),
                'is_reliable': True
            },
            {
                'reference_code': 'DEMO-FL-D104',
                'bus_id': bus20.id,
                'driver_id': d1.id,
                'fuel_litres': Decimal('38.00'),
                'rate_per_litre': Decimal('90.00'),
                'total_cost': Decimal('3420.00'),
                'odometer_reading': Decimal('120415.00'),
                'fuel_station_name': '[DEMO] IOCL Campus Auto Care',
                'bill_date': datetime(2026, 10, 16, 9, 15, 0),
                'bill_image_filename': 'bill_a41b5df1591148f896302a3eecda68e4.jpg',
                'bill_image_hash': 'f798873c7061968b',
                'submission_latitude': Decimal('12.97155000'),
                'submission_longitude': Decimal('77.59455000'),
                'gps_nearest_bunk_id': bunk_iocl.id if bunk_iocl else None,
                'gps_distance_meters': Decimal('8.20'),
                'is_gps_verified': True,
                'status': 'PENDING',
                'admin_remarks': None,
                'reviewed_by': None,
                'reviewed_at': None,
                'duplicate_flag': False,
                # Mileage: (120415 - 120225) / 38.00 = 190 / 38 = 5.00 km/L
                'distance_travelled_km': Decimal('190.00'),
                'calculated_kmpl': Decimal('5.00'),
                'is_reliable': True
            },

            # ----------------- DRIVER 2 (bus04) -----------------
            {
                'reference_code': 'DEMO-FL-D201',
                'bus_id': bus04.id,
                'driver_id': d2.id,
                'fuel_litres': Decimal('50.00'),
                'rate_per_litre': Decimal('89.00'),
                'total_cost': Decimal('4450.00'),
                'odometer_reading': Decimal('84250.00'),
                'fuel_station_name': '[DEMO] BPCL Highway Station',
                'bill_date': datetime(2026, 9, 28, 14, 20, 0),
                'bill_image_filename': 'bill_7c19c0c514d24c3990fe425c89fe4b41.png',
                'bill_image_hash': 'e54d656d65493139',
                'submission_latitude': Decimal('12.93530000'),
                'submission_longitude': Decimal('77.62460000'),
                'gps_nearest_bunk_id': bunk_bpcl.id if bunk_bpcl else None,
                'gps_distance_meters': Decimal('15.00'),
                'is_gps_verified': True,
                'status': 'APPROVED',
                'admin_remarks': '[DEMO] Initial fuel log verified.',
                'reviewed_by': admin_user.id,
                'reviewed_at': datetime(2026, 9, 28, 16, 0, 0),
                'duplicate_flag': False,
                'distance_travelled_km': None,
                'calculated_kmpl': None,
                'is_reliable': False
            },
            {
                'reference_code': 'DEMO-FL-D202',
                'bus_id': bus04.id,
                'driver_id': d2.id,
                'fuel_litres': Decimal('48.50'),
                'rate_per_litre': Decimal('89.20'),
                'total_cost': Decimal('4326.20'),
                'odometer_reading': Decimal('84485.00'),
                'fuel_station_name': '[DEMO] BPCL Highway Station',
                'bill_date': datetime(2026, 10, 5, 11, 40, 0),
                'bill_image_filename': 'bill_e1385dc306d24649817b81de4312c593.jpg',
                'bill_image_hash': 'f18c833e716196ab',
                'submission_latitude': Decimal('12.93510000'),
                'submission_longitude': Decimal('77.62440000'),
                'gps_nearest_bunk_id': bunk_bpcl.id if bunk_bpcl else None,
                'gps_distance_meters': Decimal('18.50'),
                'is_gps_verified': True,
                'status': 'APPROVED',
                'admin_remarks': '[DEMO] Approved. Valid fuel receipt.',
                'reviewed_by': admin_user.id,
                'reviewed_at': datetime(2026, 10, 5, 13, 0, 0),
                'duplicate_flag': False,
                # Mileage: (84485 - 84250) / 48.50 = 235 / 48.50 = 4.85 km/L
                'distance_travelled_km': Decimal('235.00'),
                'calculated_kmpl': Decimal('4.85'),
                'is_reliable': True
            },
            {
                'reference_code': 'DEMO-FL-D203',
                'bus_id': bus04.id,
                'driver_id': d2.id,
                'fuel_litres': Decimal('52.00'),
                'rate_per_litre': Decimal('89.50'),
                'total_cost': Decimal('4654.00'),
                'odometer_reading': Decimal('84740.00'),
                'fuel_station_name': '[DEMO] BPCL Highway Station',
                'bill_date': datetime(2026, 10, 14, 16, 10, 0),
                'bill_image_filename': 'bill_a9d35d37b1fe4ab3934d2ed10be974ae.png',
                'bill_image_hash': 'bb3f66643919c4c4',
                'submission_latitude': Decimal('12.93525000'),
                'submission_longitude': Decimal('77.62455000'),
                'gps_nearest_bunk_id': bunk_bpcl.id if bunk_bpcl else None,
                'gps_distance_meters': Decimal('8.00'),
                'is_gps_verified': True,
                'status': 'PENDING',
                'admin_remarks': None,
                'reviewed_by': None,
                'reviewed_at': None,
                'duplicate_flag': False,
                # Mileage: (84740 - 84485) / 52.00 = 255 / 52 = 4.90 km/L
                'distance_travelled_km': Decimal('255.00'),
                'calculated_kmpl': Decimal('4.90'),
                'is_reliable': True
            },

            # ----------------- DRIVER 3 (bus09 - CNG) -----------------
            {
                'reference_code': 'DEMO-FL-D301',
                'bus_id': bus09.id,
                'driver_id': d3.id,
                'fuel_litres': Decimal('30.00'),
                'rate_per_litre': Decimal('82.00'),
                'total_cost': Decimal('2460.00'),
                'odometer_reading': Decimal('62280.00'),
                'fuel_station_name': '[DEMO] BPCL Highway Station (CNG Point)',
                'bill_date': datetime(2026, 10, 3, 7, 50, 0),
                'bill_image_filename': 'bill_be3936e03164430b909ab003a9a7c1b3.png',
                'bill_image_hash': '856f7a90856f9c91',
                'submission_latitude': Decimal('12.93518000'),
                'submission_longitude': Decimal('77.62448000'),
                'gps_nearest_bunk_id': bunk_bpcl.id if bunk_bpcl else None,
                'gps_distance_meters': Decimal('5.00'),
                'is_gps_verified': True,
                'status': 'APPROVED',
                'admin_remarks': '[DEMO] CNG filling log verified.',
                'reviewed_by': admin_user.id,
                'reviewed_at': datetime(2026, 10, 3, 9, 0, 0),
                'duplicate_flag': False,
                'distance_travelled_km': None,
                'calculated_kmpl': None,
                'is_reliable': False
            },
            {
                'reference_code': 'DEMO-FL-D302',
                'bus_id': bus09.id,
                'driver_id': d3.id,
                'fuel_litres': Decimal('32.50'),
                'rate_per_litre': Decimal('82.00'),
                'total_cost': Decimal('2665.00'),
                'odometer_reading': Decimal('62495.00'),
                'fuel_station_name': '[DEMO] BPCL Highway Station (CNG Point)',
                'bill_date': datetime(2026, 10, 11, 8, 15, 0),
                'bill_image_filename': 'bill_286f9871b8814624a2551d6dc705bf4e.png',
                'bill_image_hash': '807371168fcbd8dc',
                'submission_latitude': Decimal('12.93522000'),
                'submission_longitude': Decimal('77.62452000'),
                'gps_nearest_bunk_id': bunk_bpcl.id if bunk_bpcl else None,
                'gps_distance_meters': Decimal('3.20'),
                'is_gps_verified': True,
                'status': 'APPROVED',
                'admin_remarks': '[DEMO] Approved by transport officer.',
                'reviewed_by': admin_user.id,
                'reviewed_at': datetime(2026, 10, 11, 9, 30, 0),
                'duplicate_flag': False,
                # Mileage: (62495 - 62280) / 32.50 = 215 / 32.50 = 6.62 km/kg
                'distance_travelled_km': Decimal('215.00'),
                'calculated_kmpl': Decimal('6.62'),
                'is_reliable': True
            },
            {
                'reference_code': 'DEMO-FL-D303',
                'bus_id': bus09.id,
                'driver_id': d3.id,
                'fuel_litres': Decimal('31.00'),
                'rate_per_litre': Decimal('82.50'),
                'total_cost': Decimal('2557.50'),
                'odometer_reading': Decimal('62705.00'),
                'fuel_station_name': '[DEMO] BPCL Highway Station (CNG Point)',
                'bill_date': datetime(2026, 10, 16, 7, 45, 0),
                'bill_image_filename': 'bill_797df178712044a186a89e0122759887.png',
                'bill_image_hash': '807371168fcbd8dc',
                'submission_latitude': Decimal('12.93519000'),
                'submission_longitude': Decimal('77.62449000'),
                'gps_nearest_bunk_id': bunk_bpcl.id if bunk_bpcl else None,
                'gps_distance_meters': Decimal('4.00'),
                'is_gps_verified': True,
                'status': 'CORRECTION_REQUIRED',
                'correction_notes': '[DEMO] Odometer counter in photo slightly obscured, please resubmit clear photo.',
                'admin_remarks': None,
                'reviewed_by': admin_user.id,
                'reviewed_at': datetime(2026, 10, 16, 9, 0, 0),
                'duplicate_flag': False,
                # Mileage: (62705 - 62495) / 31.00 = 210 / 31.00 = 6.77 km/kg
                'distance_travelled_km': Decimal('210.00'),
                'calculated_kmpl': Decimal('6.77'),
                'is_reliable': True
            },

            # ----------------- DRIVER 4 (bus14) -----------------
            {
                'reference_code': 'DEMO-FL-D401',
                'bus_id': bus14.id,
                'driver_id': d4.id,
                'fuel_litres': Decimal('60.00'),
                'rate_per_litre': Decimal('89.00'),
                'total_cost': Decimal('5340.00'),
                'odometer_reading': Decimal('47520.00'),
                'fuel_station_name': '[DEMO] HPCL Tech Park Point',
                'bill_date': datetime(2026, 10, 4, 15, 30, 0),
                'bill_image_filename': 'bill_5faaca738a7940cdbfa76f5b5c749a77.jpg',
                'bill_image_hash': 'f19c833e716116ab',
                'submission_latitude': Decimal('13.03590000'),
                'submission_longitude': Decimal('77.59710000'),
                'gps_nearest_bunk_id': bunk_hpcl.id if bunk_hpcl else None,
                'gps_distance_meters': Decimal('16.00'),
                'is_gps_verified': True,
                'status': 'APPROVED',
                'admin_remarks': '[DEMO] Approved heavy vehicle tank top-up.',
                'reviewed_by': admin_user.id,
                'reviewed_at': datetime(2026, 10, 4, 17, 0, 0),
                'duplicate_flag': False,
                'distance_travelled_km': None,
                'calculated_kmpl': None,
                'is_reliable': False
            },
            {
                'reference_code': 'DEMO-FL-D402',
                'bus_id': bus14.id,
                'driver_id': d4.id,
                'fuel_litres': Decimal('55.00'),
                'rate_per_litre': Decimal('89.20'),
                'total_cost': Decimal('4906.00'),
                'odometer_reading': Decimal('47780.00'),
                'fuel_station_name': '[DEMO] HPCL Tech Park Point',
                'bill_date': datetime(2026, 10, 10, 16, 0, 0),
                'bill_image_filename': 'bill_a41b5df1591148f896302a3eecda68e4.jpg',
                'bill_image_hash': 'f798873c7061968b',
                'submission_latitude': Decimal('13.03575000'),
                'submission_longitude': Decimal('77.59695000'),
                'gps_nearest_bunk_id': bunk_hpcl.id if bunk_hpcl else None,
                'gps_distance_meters': Decimal('7.80'),
                'is_gps_verified': True,
                'status': 'APPROVED',
                'admin_remarks': '[DEMO] Receipt matches dispenser meter.',
                'reviewed_by': admin_user.id,
                'reviewed_at': datetime(2026, 10, 10, 18, 0, 0),
                'duplicate_flag': False,
                # Mileage: (47780 - 47520) / 55.00 = 260 / 55 = 4.73 km/L
                'distance_travelled_km': Decimal('260.00'),
                'calculated_kmpl': Decimal('4.73'),
                'is_reliable': True
            },
            {
                'reference_code': 'DEMO-FL-D403',
                'bus_id': bus14.id,
                'driver_id': d4.id,
                'fuel_litres': Decimal('55.00'),
                'rate_per_litre': Decimal('89.20'),
                'total_cost': Decimal('4906.00'),
                'odometer_reading': Decimal('47780.00'),
                'fuel_station_name': '[DEMO] HPCL Tech Park Point',
                'bill_date': datetime(2026, 10, 11, 14, 0, 0),
                'bill_image_filename': 'bill_be7b6f5674ec4591910cbd603e2a3d89.png',
                'bill_image_hash': 'e54d656d65493139',
                'submission_latitude': Decimal('13.03578000'),
                'submission_longitude': Decimal('77.59698000'),
                'gps_nearest_bunk_id': bunk_hpcl.id if bunk_hpcl else None,
                'gps_distance_meters': Decimal('6.50'),
                'is_gps_verified': True,
                'status': 'PENDING',
                'admin_remarks': None,
                'reviewed_by': None,
                'reviewed_at': None,
                'duplicate_flag': True,
                'duplicate_warning_details': '[DEMO ADVISORY] Perceptual receipt similarity detected & identical billed cost (₹4,906.00) and odometer (47,780 km) within 48h of existing record DEMO-FL-D402.',
                'distance_travelled_km': Decimal('0.00'),
                'calculated_kmpl': None,
                'is_reliable': False
            },

            # ----------------- DRIVER 5 (bus27) -----------------
            {
                'reference_code': 'DEMO-FL-D501',
                'bus_id': bus27.id,
                'driver_id': d5.id,
                'fuel_litres': Decimal('28.00'),
                'rate_per_litre': Decimal('89.50'),
                'total_cost': Decimal('2506.00'),
                'odometer_reading': Decimal('31050.00'),
                'fuel_station_name': '[DEMO] IOCL Campus Auto Care',
                'bill_date': datetime(2026, 10, 2, 10, 30, 0),
                'bill_image_filename': 'bill_e1385dc306d24649817b81de4312c593.jpg',
                'bill_image_hash': 'f18c833e716196ab',
                'submission_latitude': Decimal('12.97162000'),
                'submission_longitude': Decimal('77.59462000'),
                'gps_nearest_bunk_id': bunk_iocl.id if bunk_iocl else None,
                'gps_distance_meters': Decimal('3.50'),
                'is_gps_verified': True,
                'status': 'APPROVED',
                'admin_remarks': '[DEMO] Mini-bus regular route refill approved.',
                'reviewed_by': admin_user.id,
                'reviewed_at': datetime(2026, 10, 2, 11, 45, 0),
                'duplicate_flag': False,
                'distance_travelled_km': None,
                'calculated_kmpl': None,
                'is_reliable': False
            },
            {
                'reference_code': 'DEMO-FL-D502',
                'bus_id': bus27.id,
                'driver_id': d5.id,
                'fuel_litres': Decimal('30.00'),
                'rate_per_litre': Decimal('89.50'),
                'total_cost': Decimal('2685.00'),
                'odometer_reading': Decimal('31230.00'),
                'fuel_station_name': '[DEMO] IOCL Campus Auto Care',
                'bill_date': datetime(2026, 10, 9, 11, 15, 0),
                'bill_image_filename': 'bill_7c19c0c514d24c3990fe425c89fe4b41.png',
                'bill_image_hash': 'e54d656d65493139',
                'submission_latitude': Decimal('12.97159000'),
                'submission_longitude': Decimal('77.59459000'),
                'gps_nearest_bunk_id': bunk_iocl.id if bunk_iocl else None,
                'gps_distance_meters': Decimal('2.00'),
                'is_gps_verified': True,
                'status': 'APPROVED',
                'admin_remarks': '[DEMO] Approved.',
                'reviewed_by': admin_user.id,
                'reviewed_at': datetime(2026, 10, 9, 12, 30, 0),
                'duplicate_flag': False,
                # Mileage: (31230 - 31050) / 30.00 = 180 / 30 = 6.00 km/L
                'distance_travelled_km': Decimal('180.00'),
                'calculated_kmpl': Decimal('6.00'),
                'is_reliable': True
            },
            {
                'reference_code': 'DEMO-FL-D503',
                'bus_id': bus27.id,
                'driver_id': d5.id,
                'fuel_litres': Decimal('35.00'),
                'rate_per_litre': Decimal('92.00'),
                'total_cost': Decimal('3220.00'),
                'odometer_reading': Decimal('31380.00'),
                'fuel_station_name': '[DEMO] Unauthorized Highway Outlet (Off-Route)',
                'bill_date': datetime(2026, 10, 13, 19, 0, 0),
                'bill_image_filename': 'bill_a9d35d37b1fe4ab3934d2ed10be974ae.png',
                'bill_image_hash': 'bb3f66643919c4c4',
                'submission_latitude': Decimal('12.85200000'),
                'submission_longitude': Decimal('77.65400000'),
                'gps_nearest_bunk_id': bunk_bpcl.id if bunk_bpcl else None,
                'gps_distance_meters': Decimal('8520.00'),
                'is_gps_verified': False,
                'status': 'REJECTED',
                'admin_remarks': '[DEMO REJECTION] Fuel purchased at unauthorized private retail outlet 8.5 km outside assigned route without prior transport office permit.',
                'reviewed_by': admin_user.id,
                'reviewed_at': datetime(2026, 10, 14, 9, 30, 0),
                'duplicate_flag': False,
                'distance_travelled_km': Decimal('150.00'),
                'calculated_kmpl': Decimal('4.29'),
                'is_reliable': True
            }
        ]

        # Insert records and handle duplicate_matched_id linkage
        records_map = {}
        for r in FuelRecord.query.all():
            records_map[r.reference_code] = r

        for r_data in demo_records_data:
            ref = r_data['reference_code']
            existing = FuelRecord.query.filter_by(reference_code=ref).first()
            if existing:
                records_map[ref] = existing
                stats['records_skipped'] += 1
            else:
                matched_id = None
                if ref == 'DEMO-FL-D403':
                    # Link to DEMO-FL-D402
                    target = records_map.get('DEMO-FL-D402')
                    if target:
                        matched_id = target.id

                new_rec = FuelRecord(
                    reference_code=ref,
                    bus_id=r_data['bus_id'],
                    driver_id=r_data['driver_id'],
                    fuel_litres=r_data['fuel_litres'],
                    rate_per_litre=r_data['rate_per_litre'],
                    total_cost=r_data['total_cost'],
                    odometer_reading=r_data['odometer_reading'],
                    fuel_station_name=r_data['fuel_station_name'],
                    bill_date=r_data['bill_date'],
                    bill_image_filename=r_data['bill_image_filename'],
                    bill_image_hash=r_data['bill_image_hash'],
                    submission_latitude=r_data['submission_latitude'],
                    submission_longitude=r_data['submission_longitude'],
                    gps_nearest_bunk_id=r_data['gps_nearest_bunk_id'],
                    gps_distance_meters=r_data['gps_distance_meters'],
                    is_gps_verified=r_data['is_gps_verified'],
                    duplicate_flag=r_data['duplicate_flag'],
                    duplicate_warning_details=r_data.get('duplicate_warning_details'),
                    duplicate_matched_id=matched_id,
                    status=r_data['status'],
                    admin_remarks=r_data.get('admin_remarks'),
                    correction_notes=r_data.get('correction_notes'),
                    reviewed_by=r_data.get('reviewed_by'),
                    reviewed_at=r_data.get('reviewed_at'),
                    created_at=r_data['bill_date'],
                    updated_at=r_data['bill_date']
                )
                db.session.add(new_rec)
                db.session.flush()
                records_map[ref] = new_rec
                stats['records_added'] += 1

                # Mileage computation
                mc_existing = MileageComputation.query.filter_by(fuel_record_id=new_rec.id).first()
                if not mc_existing:
                    mc = MileageComputation(
                        bus_id=new_rec.bus_id,
                        fuel_record_id=new_rec.id,
                        distance_travelled_km=r_data.get('distance_travelled_km'),
                        calculated_kmpl=r_data.get('calculated_kmpl'),
                        is_statistically_reliable=r_data.get('is_reliable', False),
                        created_at=new_rec.created_at
                    )
                    db.session.add(mc)
                    stats['mileage_added'] += 1

                # Audit log for submission
                db.session.add(AuditLog(
                    actor_id=new_rec.driver_id,
                    actor_role='DRIVER',
                    action='FUEL_ENTRY_SUBMITTED',
                    entity_type='FUEL_RECORD',
                    entity_id=new_rec.id,
                    new_state=new_rec.to_dict(),
                    details=f"[DEMO SETUP] Fuel submission {ref} for Bus #{new_rec.bus_id} ({new_rec.fuel_litres}L, ₹{new_rec.total_cost})",
                    created_at=new_rec.created_at
                ))
                stats['audits_added'] += 1

                # If reviewed, also log approval/rejection/correction
                if new_rec.status == 'APPROVED':
                    db.session.add(AuditLog(
                        actor_id=admin_user.id,
                        actor_role='ADMIN',
                        action='RECORD_APPROVED',
                        entity_type='FUEL_RECORD',
                        entity_id=new_rec.id,
                        new_state=new_rec.to_dict(),
                        details=f"[DEMO SETUP] Fuel record {ref} approved by Admin. Remarks: {new_rec.admin_remarks}",
                        created_at=new_rec.reviewed_at or new_rec.created_at
                    ))
                    stats['audits_added'] += 1
                elif new_rec.status == 'REJECTED':
                    db.session.add(AuditLog(
                        actor_id=admin_user.id,
                        actor_role='ADMIN',
                        action='RECORD_REJECTED',
                        entity_type='FUEL_RECORD',
                        entity_id=new_rec.id,
                        new_state=new_rec.to_dict(),
                        details=f"[DEMO SETUP] Fuel record {ref} rejected by Admin. Reason: {new_rec.admin_remarks}",
                        created_at=new_rec.reviewed_at or new_rec.created_at
                    ))
                    stats['audits_added'] += 1
                elif new_rec.status == 'CORRECTION_REQUIRED':
                    db.session.add(AuditLog(
                        actor_id=admin_user.id,
                        actor_role='ADMIN',
                        action='RECORD_CORRECTION_REQUESTED',
                        entity_type='FUEL_RECORD',
                        entity_id=new_rec.id,
                        new_state=new_rec.to_dict(),
                        details=f"[DEMO SETUP] Correction requested for {ref} by Admin. Instructions: {new_rec.correction_notes}",
                        created_at=new_rec.reviewed_at or new_rec.created_at
                    ))
                    stats['audits_added'] += 1

        db.session.commit()
        print(f"[Fuel Records] Added: {stats['records_added']}, Existing/Skipped: {stats['records_skipped']}")
        print(f"[Mileage Logs] Added: {stats['mileage_added']}")
        print(f"[Audit Logs] Added: {stats['audits_added']}")

        print("\n" + "=" * 65)
        print(" SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 65)
        print(f"Total Users in DB: {User.query.count()}")
        print(f"Total Buses in DB: {Bus.query.count()}")
        print(f"Total Bunks in DB: {ApprovedPetrolBunk.query.count()}")
        print(f"Total Fuel Records in DB: {FuelRecord.query.count()}")
        print("=" * 65)

        return stats

if __name__ == '__main__':
    # 1. Back up database first
    backup_path = backup_database()

    # 2. Seed data safely
    seed_demo_data()
