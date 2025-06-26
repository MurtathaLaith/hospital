from src.models.user import db
from datetime import datetime

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    specialization = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    can_assign_patients = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    visits = db.relationship('Visit', backref='doctor', lazy=True)
    secretary_user = db.relationship('User', backref='assigned_doctor', lazy=True)

    def __repr__(self):
        return f'<Doctor {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'department_id': self.department_id,
            'department_name': self.department.name if self.department else None,
            'specialization': self.specialization,
            'is_active': self.is_active,
            'can_assign_patients': self.can_assign_patients,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

