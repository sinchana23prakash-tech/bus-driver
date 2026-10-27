from datetime import datetime
from app.extensions import db

class ApprovedPetrolBunk(db.Model):
    __tablename__ = 'approved_petrol_bunks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.Text, nullable=True)
    latitude = db.Column(db.Numeric(10, 8), nullable=False)
    longitude = db.Column(db.Numeric(11, 8), nullable=False)
    geofence_radius_meters = db.Column(db.Integer, nullable=False, default=500)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    fuel_records = db.relationship('FuelRecord', backref='nearest_bunk', lazy=True, foreign_keys='FuelRecord.gps_nearest_bunk_id')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'latitude': float(self.latitude),
            'longitude': float(self.longitude),
            'geofence_radius_meters': self.geofence_radius_meters,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
