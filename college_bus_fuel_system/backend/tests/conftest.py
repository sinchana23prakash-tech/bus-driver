import os
import io
import pytest
from types import SimpleNamespace
from PIL import Image
from flask_jwt_extended import create_access_token
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.bus import Bus
from app.models.petrol_bunk import ApprovedPetrolBunk
from config import TestConfig

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def test_users(app):
    with app.app_context():
        # Admin
        admin = User(
            username="testadmin",
            email="admin@college.edu",
            full_name="Fleet Admin",
            role="ADMIN",
            is_active=True
        )
        admin.set_password("AdminPass@123")
        db.session.add(admin)

        # VC
        vc = User(
            username="testvc",
            email="vc@college.edu",
            full_name="Vice Chancellor",
            role="VC",
            is_active=True
        )
        vc.set_password("VCPass@123")
        db.session.add(vc)

        # Driver 1
        driver1 = User(
            username="driver1",
            email="driver1@college.edu",
            full_name="Ramesh Kumar",
            role="DRIVER",
            is_active=True
        )
        driver1.set_password("DriverPass@123")
        db.session.add(driver1)

        # Driver 2
        driver2 = User(
            username="driver2",
            email="driver2@college.edu",
            full_name="Suresh Patel",
            role="DRIVER",
            is_active=True
        )
        driver2.set_password("DriverPass@123")
        db.session.add(driver2)

        db.session.commit()

        # Capture detached values
        admin_data = SimpleNamespace(id=admin.id, username=admin.username, email=admin.email, full_name=admin.full_name, role=admin.role)
        vc_data = SimpleNamespace(id=vc.id, username=vc.username, email=vc.email, full_name=vc.full_name, role=vc.role)
        d1_data = SimpleNamespace(id=driver1.id, username=driver1.username, email=driver1.email, full_name=driver1.full_name, role=driver1.role)
        d2_data = SimpleNamespace(id=driver2.id, username=driver2.username, email=driver2.email, full_name=driver2.full_name, role=driver2.role)

        # Generate tokens
        admin_token = create_access_token(identity=str(admin.id))
        vc_token = create_access_token(identity=str(vc.id))
        d1_token = create_access_token(identity=str(driver1.id))
        d2_token = create_access_token(identity=str(driver2.id))

        return {
            'admin': admin_data,
            'vc': vc_data,
            'driver1': d1_data,
            'driver2': d2_data,
            'tokens': {
                'admin': admin_token,
                'vc': vc_token,
                'driver1': d1_token,
                'driver2': d2_token
            }
        }

@pytest.fixture
def sample_bus(app, test_users):
    with app.app_context():
        bus = Bus(
            bus_number="Bus #07",
            registration_number="KA-05-CL-4500",
            model_name="Tata Starbus Ultra",
            fuel_tank_capacity=160.0,
            fuel_type="DIESEL",
            current_odometer=12500.0,
            status="ACTIVE",
            assigned_driver_id=test_users['driver1'].id
        )
        db.session.add(bus)
        db.session.commit()
        return SimpleNamespace(
            id=bus.id,
            bus_number=bus.bus_number,
            registration_number=bus.registration_number,
            current_odometer=float(bus.current_odometer)
        )

@pytest.fixture
def sample_bunk(app):
    with app.app_context():
        bunk = ApprovedPetrolBunk(
            name="HPCL Campus Express Fuel Station",
            address="National Highway 44, Near College Gate",
            latitude=12.971600,
            longitude=77.594600,
            geofence_radius_meters=500,
            is_active=True
        )
        db.session.add(bunk)
        db.session.commit()
        return SimpleNamespace(
            id=bunk.id,
            name=bunk.name,
            latitude=float(bunk.latitude),
            longitude=float(bunk.longitude),
            geofence_radius_meters=bunk.geofence_radius_meters
        )

@pytest.fixture
def sample_receipt_image():
    """Generates an in-memory test receipt image."""
    img = Image.new('RGB', (200, 200), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    buf.seek(0)
    return buf
