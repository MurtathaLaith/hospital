from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, User
from src.models.doctor import Doctor
from src.models.patient import Patient
from src.models.visit import Visit
from datetime import datetime, date

secretary_bp = Blueprint('secretary', __name__)

def require_secretary_role():
    """Decorator to ensure user has secretary role"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 'secretary':
        return jsonify({'error': 'Access denied. Secretary role required.'}), 403
    return user

# Patient management for secretary
@secretary_bp.route('/patients/search', methods=['GET'])
@jwt_required()
def search_patient():
    user = require_secretary_role()
    if isinstance(user, tuple):  # Error response
        return user
    
    try:
        social_id = request.args.get('social_id')
        if not social_id:
            return jsonify({'error': 'Social ID is required'}), 400
        
        patient = Patient.query.filter_by(social_id=social_id).first()
        if patient:
            # Get patient's visit history
            visits = Visit.query.filter_by(patient_id=patient.id).order_by(Visit.created_at.desc()).all()
            return jsonify({
                'patient': patient.to_dict(),
                'visits': [visit.to_dict() for visit in visits]
            }), 200
        else:
            return jsonify({'patient': None, 'visits': []}), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@secretary_bp.route('/patients', methods=['POST'])
@jwt_required()
def create_patient():
    user = require_secretary_role()
    if isinstance(user, tuple):  # Error response
        return user
    
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

# Visit management for secretary
@secretary_bp.route('/visits', methods=['GET'])
@jwt_required()
def get_visits():
    user = require_secretary_role()
    if isinstance(user, tuple):  # Error response
        return user
    
    try:
        # Get visits for the secretary's assigned doctor
        if not user.doctor_id:
            return jsonify({'error': 'Secretary not assigned to any doctor'}), 400
        
        today = date.today()
        visits = Visit.query.filter_by(
            doctor_id=user.doctor_id,
            visit_date=today
        ).order_by(Visit.queue_number).all()
        
        return jsonify([visit.to_dict() for visit in visits]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@secretary_bp.route('/visits', methods=['POST'])
@jwt_required()
def create_visit():
    user = require_secretary_role()
    if isinstance(user, tuple):  # Error response
        return user
    
    try:
        if not user.doctor_id:
            return jsonify({'error': 'Secretary not assigned to any doctor'}), 400
        
        # Check if doctor can assign patients
        doctor = Doctor.query.get(user.doctor_id)
        if not doctor or not doctor.can_assign_patients:
            return jsonify({'error': 'Doctor is not allowed to assign patients'}), 403
        
        data = request.get_json()
        
        # Get next queue number for the doctor on this date
        today = date.today()
        last_queue = Visit.query.filter_by(
            doctor_id=user.doctor_id,
            visit_date=today
        ).order_by(Visit.queue_number.desc()).first()
        
        next_queue_number = (last_queue.queue_number + 1) if last_queue else 1
        
        visit = Visit(
            patient_id=data.get('patient_id'),
            doctor_id=user.doctor_id,
            queue_number=next_queue_number,
            description=data.get('description', '')
        )
        db.session.add(visit)
        db.session.commit()
        return jsonify(visit.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@secretary_bp.route('/visits/<int:visit_id>', methods=['PUT'])
@jwt_required()
def update_visit(visit_id):
    user = require_secretary_role()
    if isinstance(user, tuple):  # Error response
        return user
    
    try:
        visit = Visit.query.get_or_404(visit_id)
        
        # Ensure the visit belongs to the secretary's doctor
        if visit.doctor_id != user.doctor_id:
            return jsonify({'error': 'Access denied. Visit does not belong to your doctor.'}), 403
        
        data = request.get_json()
        
        visit.status = data.get('status', visit.status)
        visit.description = data.get('description', visit.description)
        
        if data.get('status') == 'completed' and not visit.completed_at:
            visit.completed_at = datetime.utcnow()
        
        visit.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify(visit.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Get doctor information
@secretary_bp.route('/doctor', methods=['GET'])
@jwt_required()
def get_doctor_info():
    user = require_secretary_role()
    if isinstance(user, tuple):  # Error response
        return user
    
    try:
        if not user.doctor_id:
            return jsonify({'error': 'Secretary not assigned to any doctor'}), 400
        
        doctor = Doctor.query.get(user.doctor_id)
        if not doctor:
            return jsonify({'error': 'Assigned doctor not found'}), 404
        
        return jsonify(doctor.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

