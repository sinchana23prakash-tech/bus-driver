from datetime import datetime
from app.extensions import db

class Bus(db.Model):
    __tablename__ = 'buses'

    id = db.Column(db.Integer, primary_key=True)
    bus_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    registration_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    model_name = db.Column(db.String(80), nullable=True)
    fuel_tank_capacity = db.Column(db.Numeric(7, 2), nullable=False, default=150.0)
    fuel_type = db.Column(db.String(20), nullable=False, default='DIESEL')  # Institutional fleet is 100% DIESEL
    current_odometer = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)
    status = db.Column(db.String(20), nullable=False, default='ACTIVE')  # ACTIVE, MAINTENANCE, INACTIVE
    assigned_driver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    fuel_records = db.relationship('FuelRecord', backref='bus', lazy=True, foreign_keys='FuelRecord.bus_id')
    mileage_logs = db.relationship('MileageComputation', backref='bus', lazy=True, foreign_keys='MileageComputation.bus_id')

    def to_dict(self):
        return {
            'id': self.id,
            'bus_number': self.bus_number,
            'registration_number': self.registration_number,
            'model_name': self.model_name,
            'fuel_tank_capacity': float(self.fuel_tank_capacity) if self.fuel_tank_capacity else 0.0,
            'fuel_type': self.fuel_type,
            'current_odometer': float(self.current_odometer) if self.current_odometer else 0.0,
            'status': self.status,
            'assigned_driver_id': self.assigned_driver_id,
            'assigned_driver_name': self.assigned_driver.full_name if self.assigned_driver else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
