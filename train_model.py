"""
train_model.py

This script trains a simple Linear Regression model to predict a student's
final exam score based on their study habits.

Steps followed:
1. Load the dataset
2. Do some basic preprocessing (convert Yes/No to 1/0)
3. Split into training and testing sets
4. Train the Linear Regression model
5. Check how good the model is (R2 score, MAE)
6. Save the trained model using joblib so app.py can use it later
7. Save some extra info (feature importance, accuracy) to a small json file
   so the dashboard page can display it without retraining every time
"""

import json

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

# ---------------------------------------------------------
# STEP 1: Load the dataset
# ---------------------------------------------------------
df = pd.read_csv("dataset/student_data.csv")

print("Dataset loaded. Shape:", df.shape)

# ---------------------------------------------------------
# STEP 2: Preprocessing
# ---------------------------------------------------------
# The model can only work with numbers, so we convert internet_access
# (Yes/No) into 1/0. This is a common and simple encoding technique.
df["internet_access_encoded"] = df["internet_access"].map({"Yes": 1, "No": 0})

# These are the columns the model will use to make predictions
feature_columns = [
    "study_hours",
    "attendance",
    "previous_score",
    "assignments_completed",
    "sleep_hours",
    "internet_access_encoded",
]

X = df[feature_columns]
y = df["final_score"]

# ---------------------------------------------------------
# STEP 3: Train / Test split
# ---------------------------------------------------------
# 80% of the data is used for training, 20% is kept aside for testing
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ---------------------------------------------------------
# STEP 4: Train the Linear Regression model
# ---------------------------------------------------------
model = LinearRegression()
model.fit(X_train, y_train)

# ---------------------------------------------------------
# STEP 5: Evaluate the model
# ---------------------------------------------------------
predictions = model.predict(X_test)

r2 = r2_score(y_test, predictions)
mae = mean_absolute_error(y_test, predictions)

print("\nModel Evaluation:")
print(f"R2 Score: {r2:.3f}")
print(f"Mean Absolute Error: {mae:.2f}")

# ---------------------------------------------------------
# STEP 6: Save the trained model
# ---------------------------------------------------------
joblib.dump(model, "model.pkl")
print("\nModel saved as model.pkl")

# ---------------------------------------------------------
# STEP 7: Save extra details for the dashboard page
# ---------------------------------------------------------
# Feature importance for Linear Regression is basically the coefficients.
# A bigger (absolute) coefficient means that feature affects the final
# score more strongly.
feature_importance = dict(zip(feature_columns, model.coef_.tolist()))

model_info = {
    "r2_score": round(r2 * 100, 2),   # stored as a percentage for easy display
    "mae": round(mae, 2),
    "feature_importance": feature_importance,
    "feature_columns": feature_columns,
}

with open("model_metrics.json", "w") as f:
    json.dump(model_info, f, indent=4)

print("Model metrics saved as model_metrics.json")