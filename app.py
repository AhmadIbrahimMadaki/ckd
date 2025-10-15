from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pymysql
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from sqlalchemy.exc import IntegrityError
import pandas as pd
import numpy as np
# from sklearn.model_selection import train_test_split
# from sklearn.linear_model import LogisticRegression
# from sklearn.preprocessing import StandardScaler
from flask_mail import Mail, Message
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

app = Flask(__name__)

CORS(app)


import os


load_dotenv()

# API_URL = os.getenv('REACT_APP_API_URL')
# print("API URL:", API_URL)

# SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://ab6585_ckd:tNrGVGM@s2R4G6V@MYSQL1001.site4now.net/ckd_platform"
# SQLALCHEMY_TRACK_MODIFICATIONS = False
# Configure the app to use SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/ckd_platform'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:cWAJedzCGO1plS1a6XDEbnTAQSvfcG66@dpg-cvbcd5in91rc739ff960-a.oregon-postgres.render.com/ckd_platform'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(50), nullable=False)
    diagnosis_status = db.Column(db.String(50), default="undiagnosed")

class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    diagnosis_status = db.Column(db.String(50), default="undiagnosed")
    clinical_history = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('patients', lazy=True))
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    
    

class Assessment(db.Model):
    __tablename__ = 'assessments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    responses = db.Column(db.JSON, nullable=False)  # Store answers in JSON format
    is_draft = db.Column(db.Boolean, default=False, nullable=False)
    risk_score = db.Column(db.Float, nullable=True)  # CKD risk score
    risk_category = db.Column(db.String(50), nullable=True)  # "Red", "Yellow", or "Green"
    recommendations = db.Column(db.Text, nullable=True)  # AI-generated recommendations
    medicines = db.Column(db.JSON, nullable=True) 
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    # Relationship with Patient model
    patient = db.relationship('Patient', backref=db.backref('assessments', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "responses": self.responses,
            "is_draft": self.is_draft,
            "risk_score": self.risk_score,
            "risk_category": self.risk_category,
            "recommendations": self.recommendations,
            "medicines": self.medicines,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

# class Medicine(db.Model):
#     __tablename__ = "medicines"
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(255), nullable=False)
#     description = db.Column(db.Text, nullable=True)
#     dosage = db.Column(db.String(100), nullable=False)
#     frequency = db.Column(db.String(100), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.now)


class Prescription(db.Model):
    __tablename__ = 'prescriptions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    medicine_name = db.Column(db.String(255), nullable=False)
    dosage = db.Column(db.String(100), nullable=False)
    frequency = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    # Relationships
    patient = db.relationship('Patient', backref=db.backref('prescriptions', lazy=True))
    assessment = db.relationship('Assessment', backref=db.backref('prescriptions', lazy=True))       

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    medicines = db.Column(db.JSON, nullable=False)  # store ordered meds
    status = db.Column(db.String(50), default="pending")  # pending, approved, delivered
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    patient = db.relationship('Patient', backref=db.backref('orders', lazy=True))
     
import os
import pymysql

import psycopg2
from urllib.parse import urlparse

import psycopg2.extras

def get_db_connection():
    try:
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="ckd_platform",
            cursorclass=pymysql.cursors.DictCursor  # Ensures results are returned as dictionaries
        )
        return connection
    except pymysql.MySQLError as err:
        print(f"Database connection error: {err}")
        return None

# def get_db_connection():
#     try:
#         connection = psycopg2.connect(
#             host="dpg-cvbcd5in91rc739ff960-a.oregon-postgres.render.com",
#             user="root",
#             password="cWAJedzCGO1plS1a6XDEbnTAQSvfcG66",
#             database="ckd_platform",
#             cursor_factory=psycopg2.extras.DictCursor  # ✅ Enables dictionary access
#         )
#         return connection
#     except psycopg2.Error as err:
#         print(f"Database connection error: {err}")
#         return None
    # print("✅ PostgreSQL connection successful")
    #     return connection

    # except psycopg2.Error as err:
    #     print(f"❌ Database connection error: {err}")
    #     return None
    # except ValueError as ve:
    #     print(f"❌ Configuration error: {ve}")
    #     return None
    

from werkzeug.security import generate_password_hash

def create_default_admin():
    admin_email = "admin@gmail.com"
    existing_admin = User.query.filter_by(email=admin_email).first()
    
    if not existing_admin:
        admin = User(
            full_name="System Administrator",
            email=admin_email,
            password=generate_password_hash("123admin123"),  # secure password hash
            user_type="admin",
            diagnosis_status="N/A"
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Default admin user created successfully!")
    else:
        print("ℹ️ Default admin already exists.")



def generate_medicines(risk_category):
    if "Red" in risk_category:
        return [
            {"name": "Losartan", "dosage": "50mg", "frequency": "1 tablet daily"},
            {"name": "Furosemide", "dosage": "40mg", "frequency": "1 tablet in the morning"}
        ]
    elif "Orange" in risk_category:
        return [
            {"name": "Amlodipine", "dosage": "10mg", "frequency": "1 tablet daily"},
            {"name": "Lisinopril", "dosage": "20mg", "frequency": "1 tablet daily"}
        ]
    elif "Yellow" in risk_category:
        return [
            {"name": "Hydrochlorothiazide", "dosage": "25mg", "frequency": "1 tablet daily"}
        ]
    elif "Light Green" in risk_category:
        return [
            {"name": "Vitamin D", "dosage": "1000 IU", "frequency": "1 daily"}
        ]
    else:
        return []


# Routes
@app.route("/")
def home():
    return "Server is running!"


@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        full_name = data.get('fullName')
        email = data.get('email')
        password = data.get('password')
        user_type = data.get('userType')

        # Check for missing fields
        if not all([full_name, email, password, user_type]):
            return jsonify({"message": "All fields are required"}), 400

        # Check if the email is already registered
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"message": "Email is already registered. Please use a different email."}), 409

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Create new user and save to the database
        new_user = User(
            full_name=full_name, 
            email=email, 
            password=hashed_password, 
            user_type=user_type,
            diagnosis_status="undiagnosed"  # Assuming this is a required default field
        )
        db.session.add(new_user)
        db.session.commit()

        # Automatically create a patient record if the user type is 'Patient'
        if user_type.lower() == 'patient':
            patient = Patient(
                user_id=new_user.id, 
                full_name=full_name,
                email=email,
                created_at=datetime.now()
            )
            db.session.add(patient)
            db.session.commit()

        return jsonify({"message": "Registration successful"}), 201

    except IntegrityError as e:
        db.session.rollback()
        # Handle duplicate email or unique constraint errors
        if "Duplicate entry" in str(e):
            return jsonify({"message": "Email is already registered. Please use a different email."}), 409
        return jsonify({"message": "A database error occurred. Please try again."}), 500

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500


@app.route('/api/login', methods=['POST'])
def login():
    db = get_db_connection()
    if not db:
        return jsonify({"message": "Failed to connect to the database"}), 500

    try:
        cursor = db.cursor()  # Use dictionary cursor for JSON responses
        data = request.get_json()

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"message": "Email and password are required"}), 400

        # Fetch user from the database
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):  # Verify hashed password
            
            # Determine redirect URL based on user type and other conditions
            if user['user_type'] == "patient" and user['diagnosis_status'] == "diagosed":
                redirect_url = "/patient/clinical-history"
            elif user['user_type'] == "patient":
                redirect_url = "/patientselection"
            elif user['user_type'] == "admin":
                redirect_url = "/admin/dashboard"
            else:
                redirect_url = "/dashboard"

            return jsonify({
                "message": "Login successful!",
                "redirect": redirect_url,
                "user": {
                    "id": user['id'],
                    "email": user['email'],
                    "full_name": user['full_name'],
                    "user_type": user['user_type'],
                    "diagnosis_status": user['diagnosis_status'],
                }
            }), 200
        else:
            return jsonify({"message": "Invalid email or password."}), 401

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

    finally:
        try:
            if cursor:
                cursor.close()
            if db:
                db.close()
        except Exception as e:
            print(f"Error closing the connection: {e}")
    
@app.route('/api/patient/profile', methods=['GET'])
def get_patient_profile():
    email = request.args.get('email')
    patient = Patient.query.filter_by(email=email).first()

    if not patient:
        return jsonify({"message": "Patient not found"}), 404

    if patient.diagnosis_status:
        return jsonify({"message": "Access to clinical history", "diagnosed": True}), 200
    else:
        return jsonify({"message": "Access to previous assessments", "diagnosed": False}), 200

@app.route('/api/clinical-history', methods=['GET'])
def get_clinical_history():
    email = request.args.get('email')
    patient = Patient.query.filter_by(email=email).first()

    if not patient:
        return jsonify({"message": "Patient not found"}), 404

    if not patient.diagnosis_status:
        return jsonify({"message": "Patient is not diagnosed"}), 400

    return jsonify({"history": patient.clinical_history}), 200

@app.route('/api/previous-assessments', methods=['GET'])
def get_previous_assessments():
    email = request.args.get('email')
    patient = Patient.query.filter_by(email=email).first()

    if not patient:
        return jsonify({"message": "Patient not found"}), 404

    if patient.diagnosis_status:
        return jsonify({"message": "Patient is diagnosed"}), 400

    assessments = Assessment.query.filter_by(patient_id=patient.id).all()
    assessments_data = [{"date": assessment.created_at, "details": assessment.responses} for assessment in assessments]


    return jsonify({"assessments": assessments_data}), 200

@app.route('/api/update-clinical-history', methods=['POST'])
def update_clinical_history():
    data = request.get_json()
    email = data.get('email')
    history = data.get('history')

    patient = Patient.query.filter_by(email=email).first()

    if not patient:
        return jsonify({"message": "Patient not found"}), 404

    if not patient.diagnosis_status:
        return jsonify({"message": "Patient is not diagnosed"}), 400

    patient.clinical_history = history
    db.session.commit()

    return jsonify({"message": "Clinical history updated successfully"}), 200

# @app.route('/api/assessments', methods=['POST'])
# def save_assessment():
#     try:
#         data = request.get_json()
#         patient_id = data.get("patient_id")
#         responses = data.get("responses")
#         is_draft = data.get("is_draft", True)

#         # Get a session
#         session = db.session
#         # Fetch the patient correctly
#         patient = session.get(Patient, patient_id) 

#         if not patient:
#             print(f"Patient not found for ID: {patient_id}")
#             return jsonify({"message": "Patient not found."}), 404

#         is_undiagnosed = patient.diagnosis_status == "undiagnosed"

#         # Save the assessment
#         new_assessment = Assessment(
#             patient_id=patient_id,
#             responses=responses,
#             is_draft=is_draft
#         )
#         db.session.add(new_assessment)
#         db.session.commit()

#         return jsonify({
#             "message": "Assessment saved successfully.",
#             "redirect_to_dashboard": is_undiagnosed
#         }), 201
#     except Exception as e:
#         return jsonify({"message": str(e)}), 500

# ---------------------- API Route for Prediction ----------------------
@app.route("/api/assessments", methods=["POST"])
def save_or_predict_assessment():
    try:
        data = request.json
        patient_id = data.get("patient_id")
        responses = data.get("responses")
        is_draft = data.get("is_draft", True)

        if not patient_id or not responses:
            return jsonify({"message": "Invalid data. Patient ID and responses are required."}), 400

        session = db.session
        patient = session.query(Patient).filter_by(id=patient_id).first()

        if not patient:
            return jsonify({"message": "Patient not found."}), 404

        is_undiagnosed = patient.diagnosis_status == "undiagnosed"

        # **1️⃣ Handle Draft Logic First**
        existing_draft = session.query(Assessment).filter_by(patient_id=patient_id, is_draft=True).first()
        if is_draft:
            if existing_draft:
                existing_draft.responses = responses
                session.commit()
                return jsonify({"message": "Draft updated successfully!", "redirect_to_dashboard": is_undiagnosed}), 200
            else:
                new_draft = Assessment(patient_id=patient_id, responses=responses, is_draft=True)
                session.add(new_draft)
                session.commit()
                return jsonify({"message": "Draft saved successfully!", "redirect_to_dashboard": is_undiagnosed}), 201

        # **2️⃣ Calculate Severity Percentage (Based on Responses)**
        severity_scores = {
            "A": 10,  # Low risk
            "B": 30,  # Mild risk
            "C": 50,  # Moderate risk
            "D": 70,  # High risk
            "E": 90   # Critical risk
        }

        total_score = 0
        num_questions = len(responses)
        max_score_per_question = max(severity_scores.values())  # 90
        max_possible_score = num_questions * max_score_per_question  # Correct max score

        for key, value in responses.items():
            option_letter = value.split(")")[0]  # Extract option letter (A, B, C, etc.)
            total_score += severity_scores.get(option_letter, 0)

        # ✅ Corrected severity percentage calculation
        severity_percentage = round((total_score / max_possible_score) * 100, 2)

        # **3️⃣ Determine Risk Category**
        if 81 <= severity_percentage <= 100:
            risk_category = "Red (Very High Risk)"
            recommendations = "Advanced CKD detected. Urgent nephrologist visit required."
            medicines = generate_medicines(risk_category)

        elif 61 <= severity_percentage < 81:
            risk_category = "Orange (High Risk)"
            medicines = generate_medicines(risk_category)

            recommendations = "Likely CKD progression. Consult a specialist."
        elif 41 <= severity_percentage < 61:
            risk_category = "Yellow (Moderate Risk)"
            medicines = generate_medicines(risk_category)

            recommendations = "Potential CKD detected. A medical check-up is recommended."
        elif 21 <= severity_percentage < 41:
            risk_category = "Light Green (Mild Risk)"
            recommendations = "Early CKD signs detected. Lifestyle adjustments needed."
            medicines = generate_medicines(risk_category)

        elif 0 <= severity_percentage < 21:
            risk_category = "Green (Low Risk)"
            recommendations = "No significant CKD symptoms. Maintain a healthy lifestyle."
            medicines = generate_medicines(risk_category)

        else:
            risk_category = "Unknown"
            recommendations = "Invalid severity percentage value."
            medicines = generate_medicines(risk_category)


            
        # **4️⃣ Assign Diagnosis Status Based on Risk**
        if patient.diagnosis_status == "undiagnosed" and severity_percentage < 40:
            patient.diagnosis_status = "diagnosed"
        elif patient.diagnosis_status == "diagnosed" and severity_percentage >= 40:
            patient.diagnosis_status = "undiagnosed"



        # **4️⃣ Update or Save the Assessment**
        existing_assessment = session.query(Assessment).filter_by(patient_id=patient_id).first()

        if existing_assessment:
            # ✅ Update assessment
            existing_assessment.responses = responses
            existing_assessment.risk_score = severity_percentage
            existing_assessment.risk_category = risk_category
            existing_assessment.recommendations = recommendations
            existing_assessment.medicines = medicines
            existing_assessment.updated_at = datetime.now()
            existing_assessment.is_draft = False
            session.commit()

            # ✅ Prescription handling
            # Convert new medicines to a dict for quick lookup
            new_meds_dict = {med["name"]: med for med in medicines}

            # Get all existing prescriptions for this assessment
            existing_prescriptions = session.query(Prescription).filter_by(
                patient_id=patient_id,
                assessment_id=existing_assessment.id
            ).all()

            # Update or delete old prescriptions
            for prescription in existing_prescriptions:
                if prescription.medicine_name in new_meds_dict:
                    # ✅ Update existing prescription
                    med = new_meds_dict[prescription.medicine_name]
                    prescription.dosage = med["dosage"]
                    prescription.frequency = med["frequency"]
                    prescription.created_at = datetime.now()
                    # remove it from dict so we don’t add it again
                    del new_meds_dict[prescription.medicine_name]
                else:
                    # ❌ Delete prescriptions not in new list
                    session.delete(prescription)

            # Add any remaining new prescriptions
            for med in new_meds_dict.values():
                prescription = Prescription(
                    patient_id=patient_id,
                    assessment_id=existing_assessment.id,
                    medicine_name=med["name"],
                    dosage=med["dosage"],
                    frequency=med["frequency"],
                    created_at=datetime.now()
                )
                session.add(prescription)

            session.commit()

            return jsonify({
                "message": "Assessment updated successfully!",
                "risk_score": severity_percentage,
                "risk_category": risk_category,
                "recommendations": recommendations,
                "medicines": medicines,
                "redirect_to_dashboard": is_undiagnosed
            }), 200


        # ✅ Create new assessment
        new_assessment = Assessment(
            patient_id=patient_id,
            responses=responses,
            is_draft=False,
            risk_score=severity_percentage,
            risk_category=risk_category,
            recommendations=recommendations,
            medicines=medicines,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(new_assessment)
        session.commit()
        session.refresh(new_assessment)

        # Save prescriptions in DB linked to new_assessment
        for med in medicines:
            prescription = Prescription(
                patient_id=patient_id,
                assessment_id=new_assessment.id,
                medicine_name=med["name"],
                dosage=med["dosage"],
                frequency=med["frequency"],
                created_at=datetime.now()
            )
            session.add(prescription)

        session.commit()

        return jsonify({
            "message": "Assessment submitted successfully!",
            "risk_score": severity_percentage,
            "risk_category": risk_category,
            "recommendations": recommendations,
            "medicines": medicines,
            "redirect_to_dashboard": is_undiagnosed
        }), 200


    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"message": "Internal Server Error"}), 500



@app.route('/api/assessments/<int:patient_id>', methods=['GET'])
def get_assessments(patient_id):
    try:
        
        assessments = Assessment.query.filter_by(patient_id=patient_id).all()
        return jsonify([assessment.to_dict() for assessment in assessments])
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    
@app.route("/api/assessments/draft/<int:patient_id>", methods=["GET"])
def get_draft(patient_id):
    try:
        session = db.session
        draft = session.query(Assessment).filter_by(patient_id=patient_id, is_draft=True).first()

        if not draft:
            return jsonify({"message": "No draft found"}), 404

        return jsonify({"formData": draft.responses}), 200
    except Exception as e:
        return jsonify({"message": "Error retrieving draft"}), 500

# Fetch prescriptions for a patient
@app.route("/api/prescriptions/<int:patient_id>", methods=["GET"])
def get_prescriptions(patient_id):
    prescriptions = Prescription.query.filter_by(patient_id=patient_id).all()
    if not prescriptions:
        return jsonify({"message": "No prescriptions found"}), 404
    
    prescription_list = [
        {
            "medicine_name": p.medicine_name,
            "dosage": p.dosage,
            "frequency": p.frequency,
            "created_at": p.created_at.strftime("%Y-%m-%d")
        }
        for p in prescriptions
    ]
    return jsonify(prescription_list), 200

# Place an order
@app.route("/api/orders", methods=["POST"])
def create_order():
    data = request.get_json()
    patient_id = data.get("patientId")
    medicines = data.get("medicines")

    if not patient_id or not medicines:
        return jsonify({"message": "Patient ID and medicines are required"}), 400

    order = Order(patient_id=patient_id, medicines=medicines, status="pending")
    db.session.add(order)
    db.session.commit()

    return jsonify({"message": "Order placed successfully", "order_id": order.id}), 201

    
# @app.route('/api/patient/<int:user_id>', methods=['GET'])
# def get_patient(user_id):
#     try:
#         # Log the user_id to ensure it is correctly passed
#         print(f"Fetching patient for user_id: {user_id}")

#         # Perform the query
#         query = "SELECT id AS patient_id FROM patients WHERE user_id = %s"
#         patient = db.fetch_one(query, (user_id,))

#         # Debug log for the patient object
#         print(f"Query result: {patient}")

#         if patient:
#             return jsonify(patient), 200
#         else:
#             return jsonify({"error": "Patient not found"}), 404
#     except Exception as e:
#         print(f"Error: {e}")
#         return jsonify({"error": str(e)}), 500
@app.route("/api/patient/<int:user_id>", methods=["GET"])
def get_patient(user_id):
    db = get_db_connection()
    query = """
        SELECT id AS patient_id, full_name,email, diagnosis_status, clinical_history, created_at
        FROM patients
        WHERE user_id = %s
    """
    with db.cursor() as cursor:
        cursor.execute(query, (user_id,))
        patient = cursor.fetchone()

    if patient:
        patient_data = {
            "patient_id": patient["patient_id"],
            "full_name": patient["full_name"],
            "email": patient["email"],
            "diagnosis_status": patient["diagnosis_status"],
            "clinical_history": patient["clinical_history"],
            "created_at": patient["created_at"]
        }
        return jsonify(patient_data), 200

    return jsonify({"error": "Patient not found"}), 404

# Admin 
@app.route("/api/admin/stats", methods=["GET"])
def get_stats():
    total_users = User.query.count()
    total_patients = Patient.query.count()
    diagnosed_patients = Patient.query.filter_by(diagnosis_status="diagnosed").count()
    undiagnosed_patients = total_patients - diagnosed_patients
    total_consultants = User.query.filter_by(user_type="consultant").count()

    return jsonify({
        "totalUsers": total_users,
        "totalPatients": total_patients,
        "diagnosedPatients": diagnosed_patients,
        "undiagnosedPatients": undiagnosed_patients,
        "totalConsultants": total_consultants
    })
    
@app.route("/api/admin/users", methods=["GET"])
def get_users():
    users = User.query.all()
    user_list = [{"id": user.id, "full_name": user.full_name, "email": user.email, "user_type": user.user_type} for user in users]
    return jsonify(user_list)

@app.route("/api/admin/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Delete all assessments for each patient linked to the user
    for patient in user.patients:
        for assessment in patient.assessments:
            db.session.delete(assessment)
        db.session.delete(patient)

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User and related records deleted successfully"}), 200

@app.route("/api/admin/users", methods=["POST"])
def add_user():
    data = request.get_json()
    new_user = User(full_name=data["full_name"], email=data["email"], user_type=data["user_type"])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User added successfully", "id": new_user.id}), 201


@app.route("/api/admin/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    user.full_name = data.get("full_name", user.full_name)
    user.email = data.get("email", user.email)
    user.user_type = data.get("user_type", user.user_type)
    
    # Only update password if provided
    if "password" in data and data["password"]:
        hashed_password = generate_password_hash(data["password"])
        user.password = hashed_password

    db.session.commit()
    return jsonify({"message": "User updated successfully"}), 200


# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465   # Use 465 if SSL is required
app.config['MAIL_USE_TLS'] = False  # Use False if SSL is used
app.config['MAIL_USE_SSL'] = True  # Use True if SSL is required
app.config['MAIL_USERNAME'] = 'iahmad9963@gmail.com'
app.config['MAIL_PASSWORD'] = 'ajajzpoldubocmpe'
app.config['MAIL_DEFAULT_SENDER'] = 'iahmad9963@gmail.com'

mail = Mail(app)

@app.route('/api/send-email', methods=['POST'])
def send_email():
    try:
        data = request.get_json()
        doctor_email = data.get("email")
        meet_link = "https://meet.google.com/new"  # Generate a new Google Meet link

        if not doctor_email:
            return jsonify({"error": "Doctor email is required"}), 400

        # Create the email content
        subject = "Teleconsultation Invitation"
        message_body = f"""
        Dear Doctor,

        A patient has requested a teleconsultation.

        **Join Here:** {meet_link}

        Thank you.
        """

        # Send email
        msg = Message(subject, recipients=[doctor_email], body=message_body)
        mail.send(msg)

        return jsonify({"success": True, "message": "Email sent successfully!", "meet_link": meet_link})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Create the tables within the app context
with app.app_context():
    db.create_all()
    print("Tables created successfully!")
    create_default_admin()

# Run the Flask server
if __name__ == '__main__':
    app.run(debug=True)
# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 10000))  # Render assigns a dynamic port
#     app.run(host="0.0.0.0", port=port, debug=True)
