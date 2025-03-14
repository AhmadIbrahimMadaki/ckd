from flask import Blueprint, request, jsonify
from app.models import Patient

patient_bp = Blueprint('patient', __name__, url_prefix='/api/patient')

@patient_bp.route('/profile', methods=['GET'])
def get_patient_profile():
    email = request.args.get('email')
    patient = Patient.query.filter_by(email=email).first()

    if not patient:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "id": patient.id,
        "full_name": patient.full_name,
        "email": patient.email,
        "diagnosed": patient.diagnosed
    }), 200
