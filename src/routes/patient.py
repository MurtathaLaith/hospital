from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.patient import Patient
from src.models.visit import Visit
from datetime import date, datetime

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/queue', methods=['GET'])
def get_queue_status():
    try:
        phone = request.args.get('phone')
        name = request.args.get('name')
        
        if not phone and not name:
            return jsonify({'error': 'Phone number or name is required'}), 400
        
        # Find patient by phone or name
        query = Patient.query
        if phone:
            query = query.filter_by(phone=phone)
        elif name:
            query = query.filter(Patient.name.ilike(f'%{name}%'))
        
        patient = query.first()
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Get current active visit (today's visit that's not completed)
        today = date.today()
        current_visit = Visit.query.filter_by(
            patient_id=patient.id,
            visit_date=today
        ).filter(Visit.status.in_(['waiting', 'in_progress'])).first()
        
        if not current_visit:
            return jsonify({
                'patient': patient.to_dict(),
                'current_visit': None,
                'queue_position': None,
                'estimated_waiting_time': None
            }), 200
        
        # Calculate queue position (how many people are ahead)
        ahead_count = Visit.query.filter_by(
            doctor_id=current_visit.doctor_id,
            visit_date=today,
            status='waiting'
        ).filter(Visit.queue_number < current_visit.queue_number).count()
        
        # Estimate waiting time (15 minutes per person ahead)
        estimated_waiting_time = ahead_count * 15
        
        return jsonify({
            'patient': patient.to_dict(),
            'current_visit': current_visit.to_dict(),
            'queue_position': ahead_count + 1,
            'estimated_waiting_time_minutes': estimated_waiting_time
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/visits/<int:patient_id>', methods=['GET'])
def get_patient_visits(patient_id):
    try:
        patient = Patient.query.get_or_404(patient_id)
        visits = Visit.query.filter_by(patient_id=patient_id).order_by(Visit.created_at.desc()).all()
        
        return jsonify({
            'patient': patient.to_dict(),
            'visits': [visit.to_dict() for visit in visits]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/visits/<int:visit_id>/rating', methods=['PUT'])
def rate_visit(visit_id):
    try:
        visit = Visit.query.get_or_404(visit_id)
        
        # Only allow rating completed visits
        if visit.status != 'completed':
            return jsonify({'error': 'Can only rate completed visits'}), 400
        
        data = request.get_json()
        rating = data.get('rating')
        patient_notes = data.get('patient_notes', '')
        
        if not rating or rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        
        visit.rating = rating
        visit.patient_notes = patient_notes
        visit.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify(visit.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/search', methods=['GET'])
def search_patient():
    try:
        phone = request.args.get('phone')
        name = request.args.get('name')
        
        if not phone and not name:
            return jsonify({'error': 'Phone number or name is required'}), 400
        
        # Find patient by phone or name
        query = Patient.query
        if phone:
            query = query.filter_by(phone=phone)
        elif name:
            query = query.filter(Patient.name.ilike(f'%{name}%'))
        
        patients = query.all()
        
        return jsonify([patient.to_dict() for patient in patients]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

