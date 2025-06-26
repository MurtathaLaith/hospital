from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, User
from src.models.department import Department
from src.models.doctor import Doctor
from src.models.patient import Patient
from src.models.visit import Visit
from datetime import datetime, date
from sqlalchemy import func

central_bp = Blueprint('central', __name__)

def require_central_role():
    """Decorator to ensure user has central role"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 'central':
        return jsonify({'error': 'Access denied. Central role required.'}), 403
    return None

# Department management
@central_bp.route('/departments', methods=['GET'])
@jwt_required()
def get_departments():
    auth_check = require_central_role()
    if auth_check:
        return auth_check
    
    try:
        departments = Department.query.all()
        return jsonify([dept.to_dict() for dept in departments]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@central_bp.route('/departments', methods=['POST'])
@jwt_required()
def create_department():
    auth_check = require_central_role()
    if auth_check:
        return auth_check
    
    try:
        data = request.get_json()
        department = Department(
            name=data.get('name'),
            description=data.get('description', '')
        )
        db.session.add(department)
        db.session.commit()
        return jsonify(department.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@central_bp.route('/departments/<int:dept_id>', methods=['PUT'])
@jwt_required()
def update_department(dept_id):
    auth_check = require_central_role()
    if auth_check:
        return auth_check
    
    try:
        department = Department.query.get_or_404(dept_id)
        data = request.get_json()
        
        department.name = data.get('name', department.name)
        department.description = data.get('description', department.description)
        department.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify(department.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@central_bp.route('/departments/<int:dept_id>', methods=['DELETE'])
@jwt_required()
def delete_department(dept_id):
    auth_check = require_central_role()
    if auth_check:
        return auth_check
    
    try:
        department = Department.query.get_or_404(dept_id)
        db.session.delete(department)
        db.session.commit()
        return jsonify({'message': 'Department deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Doctor management
@central_bp.route('/doctors', methods=['GET'])
@jwt_required()
def get_doctors():
    auth_check = require_central_role()
    if auth_check:
        return auth_check
    
    try:
        doctors = Doctor.query.all()
        return jsonify([doctor.to_dict() for doctor in doctors]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@central_bp.route('/doctors', methods=['POST'])
@jwt_required()
def create_doctor():
    auth_check = require_central_role()
    if auth_check:
        return auth_check
    
    try:
        data = request.get_json()
        doctor = Doctor(
            name=data.get('name'),
            department_id=data.get('department_id'),
            specialization=data.get('specialization', ''),
            is_active=data.get('is_active', True),
            can_assign_patients=data.get('can_assign_patients', True)
        )
        db.session.add(doctor)
        db.session.commit()
        return jsonify(doctor.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@central_bp.route('/doctors/<int:doctor_id>', methods=['PUT'])
@jwt_required()
def update_doctor(doctor_id):
    auth_check = require_central_role()
    if auth_check:
        return auth_check
    
    try:
        doctor = Doctor.query.get_or_404(doctor_id)
        data = request.get_json()
        
        doctor.name = data.get('name', doctor.name)
        doctor.department_id = data.get('department_id', doctor.department_id)
        doctor.specialization = data.get('specialization', doctor.specialization)
        doctor.is_active = data.get('is_active', doctor.is_active)
        doctor.can_assign_patients = data.get('can_assign_patients', doctor.can_assign_patients)
        doctor.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify(doctor.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@central_bp.route('/doctors/<int:doctor_id>', methods=['DELETE'])
@jwt_required()
def delete_doctor(doctor_id):
    auth_check = require_central_role()
    if auth_check:
        return auth_check
    
    try:
        doctor = Doctor.query.get_or_404(doctor_id)
        db.session.delete(doctor)
        db.session.commit()
        return jsonify({'message': 'Doctor deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Patient management
@central_bp.route('/patients', methods=['GET'])
@jwt_required()
def get_patients():
    auth_check = require_central_role()
    if auth_check:
        return auth_check
    
    try:
        patients = Patient.query.all()
        return jsonify([patient.to_dict() for patient in patients]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@central_bp.route('/patients', methods=['POST'])
@jwt_required()
def create_patient():
    auth_check = require_central_role()
    if auth_check:
        return auth_check
    
    try:
        data = request.get_json()
        
        # Check if patient with social_id already exists
        existing_patient = Patient.query.filter_by(social_id=data.get('social_id')).first()
        if existing_patient:
            return jsonify({'error': 'Patient with this social ID already exists'}), 400
        
        patient = Patient(
            social_id=data.get('social_id'),
            name=data.get('name'),
            age=data.get('age'),
            phone=data.get('phone')
        )
        db.session.add(patient)
        db.session.commit()
        return jsonify(patient.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@central_bp.route('/patients/<int:patient_id>', methods=['PUT'])
@jwt_required()
def update_patient(patient_id):
    auth_check = require_central_role()
    if auth_check:
        return auth_check
    
    try:
        patient = Patient.query.get_or_404(patient_id)
        data = request.get_json()
        
        patient.name = data.get('name', patient.name)
        patient.age = data.get('age', patient.age)
        patient.phone = data.get('phone', patient.phone)
        patient.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify(patient.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Visit management
@central_bp.route('/visits', methods=['GET'])
@jwt_required()
def get_visits():
    auth_check = require_central_role()
    if auth_check:
        return auth_check
    
    try:
        visits = Visit.query.all()
        return jsonify([visit.to_dict(include_admin_notes=True) for visit in visits]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@central_bp.route('/visits', methods=['POST'])
@jwt_required()
def create_visit():
    auth_check = require_central_role()
    if auth_check:
        return auth_check
    
    try:
        data = request.get_json()
        
        # Get next queue number for the doctor on this date
        today = date.today()
        last_queue = Visit.query.filter_by(
            doctor_id=data.get('doctor_id'),
            visit_date=today
        ).order_by(Visit.queue_number.desc()).first()
        
        next_queue_number = (last_queue.queue_number + 1) if last_queue else 1
        
        visit = Visit(
            patient_id=data.get('patient_id'),
            doctor_id=data.get('doctor_id'),
            queue_number=next_queue_number,
            description=data.get('description', ''),
            admin_notes=data.get('admin_notes', '')
        )
        db.session.add(visit)
        db.session.commit()
        return jsonify(visit.to_dict(include_admin_notes=True)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@central_bp.route('/visits/<int:visit_id>', methods=['PUT'])
@jwt_required()
def update_visit(visit_id):
    auth_check = require_central_role()
    if auth_check:
        return auth_check
    
    try:
        visit = Visit.query.get_or_404(visit_id)
        data = request.get_json()
        
        visit.status = data.get('status', visit.status)
        visit.description = data.get('description', visit.description)
        visit.admin_notes = data.get('admin_notes', visit.admin_notes)
        
        if data.get('status') == 'completed' and not visit.completed_at:
            visit.completed_at = datetime.utcnow()
        
        visit.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify(visit.to_dict(include_admin_notes=True)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Statistics
@central_bp.route('/visits/stats', methods=['GET'])
@jwt_required()
def get_visit_stats():
    auth_check = require_central_role()
    if auth_check:
        return auth_check
    
    try:
        today = date.today()
        
        # Average waiting time per doctor (simplified calculation)
        doctors_stats = db.session.query(
            Doctor.id,
            Doctor.name,
            func.count(Visit.id).label('total_visits'),
            func.avg(Visit.rating).label('avg_rating'),
            func.count(Visit.id).filter(Visit.status == 'waiting').label('waiting_count')
        ).join(Visit).filter(Visit.visit_date == today).group_by(Doctor.id).all()
        
        stats = []
        for stat in doctors_stats:
            # Estimate average waiting time (simplified: 15 minutes per waiting patient)
            avg_waiting_time = stat.waiting_count * 15 if stat.waiting_count else 0
            
            stats.append({
                'doctor_id': stat.id,
                'doctor_name': stat.name,
                'total_visits_today': stat.total_visits,
                'average_rating': round(stat.avg_rating, 2) if stat.avg_rating else None,
                'current_waiting_count': stat.waiting_count,
                'estimated_waiting_time_minutes': avg_waiting_time
            })
        
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

