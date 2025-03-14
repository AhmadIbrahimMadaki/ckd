# import pandas as pd
# import numpy as np
# import joblib
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import StandardScaler, LabelEncoder
# from sklearn.linear_model import LogisticRegression
# from sklearn.metrics import accuracy_score, classification_report
# import joblib

# # Load dataset
# df = {
#     "age": 24,
#     "gender": "Male",
#     "height": 189,
#     "weight": 67,
#     "medical_history": "No",
#     "family_history": "No",
#     "diet": "Low",
#     "smoking_alcohol": "No",
#     "physical_activity": "2X in a week"
# }

# # Feature Selection
# features = ['Age', 'Height', 'Weight', 'Medical History', 'Family History', 'Diet', 'Smoking Alcohol', 'Physical Activity', 'Gender']
# target = 'CKD Condition'

# # Convert categorical features to numerical
# categorical_features = ['Gender', 'Medical History', 'Family History', 'Diet', 'Smoking Alcohol', 'Physical Activity']
# df_encoded = pd.get_dummies(df, columns=categorical_features, drop_first=True)

# # Compute BMI (Body Mass Index)
# df_encoded['BMI'] = df_encoded['Weight'] / ((df_encoded['Height'] / 100) ** 2)

# # Define features and target
# X = df_encoded.drop(columns=[target])
# y = df[target]

# # Split dataset
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# # Standardize numerical features
# scaler = StandardScaler()
# X_train_scaled = scaler.fit_transform(X_train)
# X_test_scaled = scaler.transform(X_test)

# # Train Logistic Regression model
# model = LogisticRegression()
# model.fit(X_train_scaled, y_train)

# # Model Evaluation
# y_pred = model.predict(X_test_scaled)
# accuracy = accuracy_score(y_test, y_pred)
# print(f'Model Accuracy: {accuracy:.2f}')
# print(classification_report(y_test, y_pred))

# # Save the model and scaler
# joblib.dump(model, 'CKD_Predictor.pkl')
# joblib.dump(scaler, 'scaler.pkl')
# print("Model and scaler saved successfully!")

# # Function to Predict CKD Risk
# def predict_ckd_risk(patient_data):
#     """ Takes patient data as input and predicts CKD risk level. """

#     # Convert patient data to DataFrame
#     patient_df = pd.DataFrame([patient_data])

#     # Compute BMI
#     patient_df['BMI'] = patient_df['weight'] / ((patient_df['height'] / 100) ** 2)

#     # One-hot encode categorical features (ensure same column format as training data)
#     patient_df_encoded = pd.get_dummies(patient_df, columns=categorical_features, drop_first=True)

#     # Align columns with training data
#     missing_cols = set(X.columns) - set(patient_df_encoded.columns)
#     for col in missing_cols:
#         patient_df_encoded[col] = 0  # Add missing columns with default value

#     patient_df_encoded = patient_df_encoded[X.columns]  # Ensure correct column order

#     # Scale input data
#     patient_scaled = scaler.transform(patient_df_encoded)

#     # Predict CKD risk
#     predicted_proba = model.predict_proba(patient_scaled)[:, 1].mean()
    
#     # Interpret risk level
#     if predicted_proba < 0.3:
#         return "Low CKD Risk"
#     elif 0.3 <= predicted_proba < 0.7:
#         return "Moderate CKD Risk"
#     else:
#         return "High CKD Risk"

# # Example Patient Data
# example_patient = {
#     "age": 24,
#     "gender": "Male",
#     "height": 189,
#     "weight": 67,
#     "medical_history": "No",
#     "family_history": "No",
#     "diet": "Low",
#     "smoking_alcohol": "No",
#     "physical_activity": "2X in a week"
# }

# # Predict Risk for Example Patient
# risk_level = predict_ckd_risk(example_patient)
# print(f"Predicted CKD Risk Level: {risk_level}")

# # Save the trained model
# joblib.dump(dtc, "test.pkl")

# print("Model saved successfully!")

# import pickle

# with open("ckd_model.pkl", "rb") as f:
#     ckd_model = pickle.load(f)

# print(type(ckd_model))  # This should return a trained model, not a numpy.ndarray

from sqlalchemy import create_engine

db_uri = "mysql+pymysql://ab6585_ckd:tNrGVGM@s2R4G6V@MYSQL1001.site4now.net/ckd_platform"
engine = create_engine(db_uri)

try:
    with engine.connect() as conn:
        print("✅ Database connection successful!")
except Exception as e:
    print("❌ Database connection failed:", e)
