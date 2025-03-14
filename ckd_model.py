import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.preprocessing import LabelEncoder
import joblib
from sklearn.preprocessing import StandardScaler

import warnings
warnings.filterwarnings("ignore")

df = pd.read_csv("kidney_disease.csv")
df.drop("id", axis = 1, inplace = True)

print(df.head(50))

df.columns = ["age", "blood_pressure", "specific_gravity", "albumin", "sugar", 
              "red_blood_cells", "pus_cell", "pus_cell_clumbs", "bacteria", "blood_glucose_random",
              "blood_urea", "serum_creatinine", "sodium", "potassium", "hemoglobin", "packed_cell_volume", 
              "white_blood_cell_count", "red_blood_cell_count", "hypertension", "diabetes_mellitus", "coronary_artery_disease", 
              "appetite", "peda_edema", "anemia", "class"]

print(df.info())

df["packed_cell_volume"] = pd.to_numeric(df["packed_cell_volume"], errors = "coerce")
df["white_blood_cell_count"] = pd.to_numeric(df["white_blood_cell_count"], errors = "coerce")
df["red_blood_cell_count"] = pd.to_numeric(df["red_blood_cell_count"], errors = "coerce")

cat_cols = [col for col in df.columns if df[col].dtype == "object"] # categoric data
num_cols = [col for col in df.columns if df[col].dtype != "object"] # numeric data

for col in cat_cols:
    print(f"{col}: {df[col].unique()}")
    
df["diabetes_mellitus"].replace(to_replace = {"\tno": "no", "\types": "yes", "yes": "yes"}, inplace = True)
df["coronary_artery_disease"].replace(to_replace = {"\tno": "no"}, inplace = True)
df["class"].replace(to_replace = {"ckd\t": "ckd"}, inplace = True)

df["class"] = df["class"].map({"ckd": 0, "notckd": 1})

plt.figure(figsize = (15, 15))
plotnumber = 1

for col in num_cols:
    if plotnumber <= 14:
        ax = plt.subplot(3, 5, plotnumber)
        sns.distplot(df[col])
        plt.xlabel(col)

    plotnumber += 1

# plt.tight_layout()
# plt.show()

plt.figure()
sns.heatmap(df.select_dtypes(include=np.number).corr(), fmt=".1f", annot = True, linecolor = "white", linewidths = 0.5)
# plt.show()

def kde(col):
    grid = sns.FacetGrid(df, hue = "class", height = 6, aspect = 2)
    grid.map(sns.kdeplot, col)
    grid.add_legend()

kde("hemoglobin")
kde("white_blood_cell_count")
kde("packed_cell_volume")
kde("red_blood_cell_count")
kde("albumin")
kde("specific_gravity")

df.isna().sum().sort_values(ascending = False)

def solve_mv_random_value(feature):
    random_sample = df[feature].dropna().sample(df[feature].isna().sum())
    random_sample.index = df[df[feature].isnull()].index
    df.loc[df[feature].isnull(), feature] = random_sample
    
for col in num_cols:
    solve_mv_random_value(col)
    
df[num_cols].isnull().sum()

solve_mv_random_value("red_blood_cells")
solve_mv_random_value("pus_cell")

def solve_mv_mode(feature):
    mode = df[feature].mode()[0]
    df[feature] = df[feature].fillna(mode)
    
for col in cat_cols:
    solve_mv_mode(col)
    
df[cat_cols].isnull().sum()

# for col in cat_cols:
#     print(f"{col}: {df[col].nunique()}")
    
encoder = LabelEncoder()
for col in cat_cols:
    df[col] = encoder.fit_transform(df[col])
    
independent_col = [col for col in df.columns if col != "class"]
dependent_col = "class"

X = df[independent_col]
y = df[dependent_col]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3, random_state = 42)

# Initialize StandardScaler
scaler = StandardScaler()

# Fit on training data and transform both train & test data
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

from imblearn.over_sampling import SMOTE

smote = SMOTE(sampling_strategy="auto", random_state=42)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)

# dtc = DecisionTreeClassifier(max_depth=5, min_samples_split=10, min_samples_leaf=5, random_state=42)

from sklearn.ensemble import RandomForestClassifier

from sklearn.calibration import CalibratedClassifierCV

dtc = DecisionTreeClassifier(max_depth=5, min_samples_split=10, min_samples_leaf=5)
dtc.fit(X_train, y_train)

dtc_calibrated = CalibratedClassifierCV(dtc, method="sigmoid")
dtc_calibrated.fit(X_train, y_train)

# rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
# rf.fit(X_train, y_train)
# dtc = DecisionTreeClassifier(max_depth=5, min_samples_split=10, min_samples_leaf=5)
# dtc.fit(X_train, y_train)


predictions = dtc_calibrated.predict(X_test)
print("Predictions:", predictions)
y_pred = dtc_calibrated.predict(X_test)

dtc_acc = accuracy_score(y_test, y_pred)
print(f"Accuracy Score: {dtc_acc:.2f}\n")

cm = confusion_matrix(y_test, y_pred)
print(f"confusion Matrix:\n{cm}\n")

cr = classification_report(y_test, y_pred)
print(f"Classification Report:\n{cr}\n")

class_names = ["ckd", "notckd"]

# plt.figure(figsize = (20, 10))
# plot_tree(dtc, feature_names = independent_col, filled = True, rounded = True, fontsize = 15)
# plt.show()

feature_importance = pd.DataFrame({"Feature": independent_col, "Importance": dtc.feature_importances_})

print("Most important feature: ", feature_importance.sort_values(by="Importance", ascending=False).iloc[0])

plt.figure()
sns.barplot(x = "Importance", y = "Feature", data = feature_importance)
plt.title("Feature Importance")
# plt.show()
# X_scaled = scaler.transform(df)
# risk_score = rf.predict_proba(X_scaled)[0][1]  # Probability of CKD
# print(f"Risk Score: {risk_score}")
# Save the trained model
joblib.dump(dtc_calibrated, "ckd_model.pkl")
joblib.dump(scaler, "scaler.pkl")

print("CKD_Model saved successfully!")
print("scaler saved successfully!")