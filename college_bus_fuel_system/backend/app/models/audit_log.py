from datetime import datetime
from app.extensions import db

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    actor_role = db.Column(db.String(30), nullable=False)
    action = db.Column(db.String(60), nullable=False, index=True) # e.g. SUBMIT_FUEL, APPROVE, REJECT, REQUEST_CORRECTION, RESUBMIT
    entity_type = db.Column(db.String(40), nullable=False) # FUEL_RECORD, BUS, USER, SYSTEM
    entity_id = db.Column(db.Integer, nullable=False, index=True)
    previous_state = db.Column(db.JSON, nullable=True)
    new_state = db.Column(db.JSON, nullable=True)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationship
    actor = db.relationship('User', foreign_keys=[actor_id], lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'actor_id': self.actor_id,
            'actor_name': self.actor.full_name if self.actor else 'System/Initial Setup',
            'actor_role': self.actor_role,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'previous_state': self.previous_state,
            'new_state': self.new_state,
            'details': self.details,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
