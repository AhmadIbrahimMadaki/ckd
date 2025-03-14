from flask import Blueprint, request, jsonify
from app.models import Patient, db
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    full_name = data.get('fullName')
    email = data.get('email')
    password = data.get('password')
    user_type = data.get('userType')

    if not all([full_name, email, password, user_type]):
        return jsonify({"message": "All fields are required"}), 400

    existing_user = Patient.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"message": "Email already registered"}), 400

    hashed_password = generate_password_hash(password)
    new_user = Patient(
        full_name=full_name,
        email=email,
        password=hashed_password,
        user_type=user_type
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Registration successful"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    user = Patient.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        return jsonify({
            "message": "Login successful",
            "user_id": user.id,
            "user_type": user.user_type
        }), 200
    else:
        return jsonify({"message": "Invalid email or password"}), 401
