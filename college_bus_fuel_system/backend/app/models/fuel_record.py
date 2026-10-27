from datetime import datetime
from app.extensions import db

class FuelRecord(db.Model):
    __tablename__ = 'fuel_records'

    id = db.Column(db.Integer, primary_key=True)
    reference_code = db.Column(db.String(40), unique=True, nullable=False, index=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False, index=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Financial & Fuel details
    fuel_litres = db.Column(db.Numeric(8, 2), nullable=False)
    rate_per_litre = db.Column(db.Numeric(8, 2), nullable=False)
    total_cost = db.Column(db.Numeric(10, 2), nullable=False)
    odometer_reading = db.Column(db.Numeric(10, 2), nullable=False)
    fuel_station_name = db.Column(db.String(120), nullable=False)
    fuel_type = db.Column(db.String(20), nullable=False, default='DIESEL')
    bill_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Secure Storage & Image Integrity
    bill_image_filename = db.Column(db.String(255), nullable=False)
    bill_image_hash = db.Column(db.String(64), nullable=True, index=True)
    
    # OCR Extraction State
    ocr_extracted_data = db.Column(db.JSON, nullable=True)
    ocr_confidence_score = db.Column(db.Numeric(5, 2), default=0.0)
    ocr_status = db.Column(db.String(40), default='MANUAL_FALLBACK')
    
    # Privacy-conscious GPS Check
    submission_latitude = db.Column(db.Numeric(10, 8), nullable=True)
    submission_longitude = db.Column(db.Numeric(11, 8), nullable=True)
    gps_nearest_bunk_id = db.Column(db.Integer, db.ForeignKey('approved_petrol_bunks.id'), nullable=True)
    gps_distance_meters = db.Column(db.Numeric(10, 2), nullable=True)
    is_gps_verified = db.Column(db.Boolean, default=False)
    
    # Duplicate Screening (Warning Flag for Reviewer)
    duplicate_flag = db.Column(db.Boolean, default=False)
    duplicate_warning_details = db.Column(db.Text, nullable=True)
    duplicate_matched_id = db.Column(db.Integer, db.ForeignKey('fuel_records.id'), nullable=True)
    
    # Approval Workflow
    status = db.Column(db.String(30), default='PENDING', index=True) # PENDING, APPROVED, REJECTED, CORRECTION_REQUIRED
    admin_remarks = db.Column(db.Text, nullable=True)
    vc_remarks = db.Column(db.Text, nullable=True)
    correction_notes = db.Column(db.Text, nullable=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reviewer = db.relationship('User', foreign_keys=[reviewed_by], lazy=True)
    mileage_entry = db.relationship('MileageComputation', backref='fuel_record', uselist=False, lazy=True, foreign_keys='MileageComputation.fuel_record_id')

    def to_dict(self):
        prev_record = None
        if self.mileage_entry and self.mileage_entry.previous_fuel_record_id:
            prev_record = db.session.get(FuelRecord, self.mileage_entry.previous_fuel_record_id)

        prev_odometer = float(prev_record.odometer_reading) if prev_record and prev_record.odometer_reading is not None else None
        distance_travelled_km = float(self.mileage_entry.distance_travelled_km) if self.mileage_entry and self.mileage_entry.distance_travelled_km is not None else None

        bus_fuel = self.bus.fuel_type if self.bus else None
        mismatch = bool(bus_fuel and self.fuel_type and self.fuel_type.upper() != bus_fuel.upper())

        return {
            'id': self.id,
            'reference_code': self.reference_code,
            'bus_id': self.bus_id,
            'bus_number': self.bus.bus_number if self.bus else None,
            'bus_registration': self.bus.registration_number if self.bus else None,
            'bus_fuel_type': bus_fuel,
            'driver_id': self.driver_id,
            'driver_name': self.driver.full_name if self.driver else None,
            'fuel_litres': float(self.fuel_litres) if self.fuel_litres else 0.0,
            'rate_per_litre': float(self.rate_per_litre) if self.rate_per_litre else 0.0,
            'total_cost': float(self.total_cost) if self.total_cost else 0.0,
            'odometer_reading': float(self.odometer_reading) if self.odometer_reading else 0.0,
            'previous_odometer': prev_odometer,
            'distance_travelled_km': distance_travelled_km,
            'fuel_station_name': self.fuel_station_name,
            'fuel_type': self.fuel_type or bus_fuel or 'DIESEL',
            'fuel_type_mismatch': mismatch,
            'bill_date': self.bill_date.isoformat() if self.bill_date else None,
            'bill_image_filename': self.bill_image_filename,
            'ocr_extracted_data': self.ocr_extracted_data,
            'ocr_confidence_score': float(self.ocr_confidence_score) if self.ocr_confidence_score else 0.0,
            'ocr_status': self.ocr_status,
            'submission_latitude': float(self.submission_latitude) if self.submission_latitude else None,
            'submission_longitude': float(self.submission_longitude) if self.submission_longitude else None,
            'gps_nearest_bunk_id': self.gps_nearest_bunk_id,
            'gps_nearest_bunk_name': self.nearest_bunk.name if self.nearest_bunk else None,
            'gps_distance_meters': float(self.gps_distance_meters) if self.gps_distance_meters else None,
            'is_gps_verified': self.is_gps_verified,
            'duplicate_flag': self.duplicate_flag,
            'duplicate_warning_details': self.duplicate_warning_details,
            'duplicate_matched_id': self.duplicate_matched_id,
            'status': self.status,
            'admin_remarks': self.admin_remarks,
            'vc_remarks': self.vc_remarks,
            'correction_notes': self.correction_notes,
            'reviewed_by': self.reviewed_by,
            'reviewer_name': self.reviewer.full_name if self.reviewer else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'mileage_kmpl': float(self.mileage_entry.calculated_kmpl) if self.mileage_entry and self.mileage_entry.calculated_kmpl is not None else None,
            'is_mileage_reliable': self.mileage_entry.is_statistically_reliable if self.mileage_entry else False
        }
