import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
from imblearn.over_sampling import SMOTE
import warnings
warnings.filterwarnings("ignore")

# Load dataset
df = pd.read_csv("CKD_Severity_Questionnaire.csv")
df.drop("id", axis=1, inplace=True)

# Select only relevant columns
df = df[["Swelling", "Urination", "Tiredness", "Blood Pressure", "Diabetes", "class"]]

# Handle missing values
def solve_mv_mode(feature):
    mode = df[feature].mode()[0]
    df[feature] = df[feature].fillna(mode)

for col in df.columns:
    solve_mv_mode(col)

# Encode categorical variables
encoder = LabelEncoder()
for col in ["Swelling", "Urination", "Tiredness", "Diabetes", "class"]:
    df[col] = encoder.fit_transform(df[col])

# Define features and target variable
X = df.drop(columns=["class"])
y = df["class"]

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Scale features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Handle class imbalance
smote = SMOTE(sampling_strategy="auto", random_state=42)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)

# Train model
dtc = DecisionTreeClassifier(max_depth=5, min_samples_split=10, min_samples_leaf=5, random_state=42)
dtc.fit(X_train_balanced, y_train_balanced)

# Predictions
y_pred = dtc.predict(X_test)

# Evaluation
print(f"Accuracy Score: {accuracy_score(y_test, y_pred):.2f}\n")
print(f"Confusion Matrix:\n{confusion_matrix(y_test, y_pred)}\n")
print(f"Classification Report:\n{classification_report(y_test, y_pred)}\n")

# Save model and scaler
joblib.dump(dtc, "ckd_m2.pkl")
joblib.dump(scaler, "scaler2.pkl")

print("CKD Model saved successfully!")
print("Scaler saved successfully!")
