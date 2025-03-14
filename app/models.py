from app import db

class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Adjusted for hashed passwords
    user_type = db.Column(db.String(50), nullable=False)
    diagnosed = db.Column(db.Boolean, default=False)
    clinical_history = db.Column(db.Text, nullable=True)

    assessments = db.relationship('Assessment', backref='patient', lazy=True)



class Assessment(db.Model):
    __tablename__ = 'assessments'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    details = db.Column(db.Text, nullable=False)
