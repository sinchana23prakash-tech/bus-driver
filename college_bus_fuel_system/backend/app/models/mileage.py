from datetime import datetime
from app.extensions import db

class MileageComputation(db.Model):
    __tablename__ = 'mileage_computations'

    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False, index=True)
    fuel_record_id = db.Column(db.Integer, db.ForeignKey('fuel_records.id'), nullable=False, unique=True)
    previous_fuel_record_id = db.Column(db.Integer, db.ForeignKey('fuel_records.id'), nullable=True)
    
    distance_travelled_km = db.Column(db.Numeric(9, 2), nullable=True)
    calculated_kmpl = db.Column(db.Numeric(6, 2), nullable=True)
    is_statistically_reliable = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'bus_id': self.bus_id,
            'fuel_record_id': self.fuel_record_id,
            'previous_fuel_record_id': self.previous_fuel_record_id,
            'distance_travelled_km': float(self.distance_travelled_km) if self.distance_travelled_km else None,
            'calculated_kmpl': float(self.calculated_kmpl) if self.calculated_kmpl else None,
            'is_statistically_reliable': self.is_statistically_reliable,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
