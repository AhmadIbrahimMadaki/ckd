from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Patient model
class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    diagnosed = db.Column(db.Boolean, default=False)  # Indicates if the patient is diagnosed
    clinical_history = db.Column(db.Text, nullable=True)  # Clinical history for diagnosed patients

    # Relationship with assessments
    assessments = db.relationship('Assessment', backref='patient', lazy=True)


# Assessment model
class Assessment(db.Model):
    __tablename__ = 'assessments'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)  # Store the date of the assessment
    details = db.Column(db.Text, nullable=False)  # Details of the assessment
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)  # Foreign key to the patients table
