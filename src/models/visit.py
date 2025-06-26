from src.models.user import db
from datetime import datetime

class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    queue_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='waiting')  # waiting, in_progress, completed, cancelled
    description = db.Column(db.Text)
    visit_date = db.Column(db.Date, default=datetime.utcnow().date)
    completed_at = db.Column(db.DateTime)
    rating = db.Column(db.Integer)  # 1-5 rating
    patient_notes = db.Column(db.Text)
    admin_notes = db.Column(db.Text)  # Only visible to central control
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Visit {self.id} - Patient: {self.patient_id}, Doctor: {self.doctor_id}>'

    def to_dict(self, include_admin_notes=False):
        result = {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.name if self.patient else None,
            'patient_phone': self.patient.phone if self.patient else None,
            'doctor_id': self.doctor_id,
            'doctor_name': self.doctor.name if self.doctor else None,
            'department_name': self.doctor.department.name if self.doctor and self.doctor.department else None,
            'queue_number': self.queue_number,
            'status': self.status,
            'description': self.description,
            'visit_date': self.visit_date.isoformat() if self.visit_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'rating': self.rating,
            'patient_notes': self.patient_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_admin_notes:
            result['admin_notes'] = self.admin_notes
            
        return result

