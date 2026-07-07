"""
app.py

Main Flask application for the Student Performance Predictor project.

Routes:
    /            -> Home page
    /predict     -> Prediction form (GET) + handles prediction (POST)
    /dashboard   -> Shows dataset insights and charts

The trained model (model.pkl) is loaded once when the app starts,
so we don't have to load it again on every request.
"""

import base64
import io
import json

import joblib
import matplotlib
import numpy as np
import pandas as pd

# Using 'Agg' backend because we are generating charts on a server,
# not showing them in a window.
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from flask import Flask, render_template, request

app = Flask(__name__)

# ---------------------------------------------------------
# Load the trained model and metrics once at startup
# ---------------------------------------------------------
model = joblib.load("model.pkl")

with open("model_metrics.json", "r") as f:
    model_metrics = json.load(f)

# Load the dataset once as well, it is reused on the dashboard page
student_df = pd.read_csv("dataset/student_data.csv")


def convert_plot_to_base64():
    """
    Helper function that takes the current matplotlib figure,
    converts it into a base64 string, and returns it.

    This way we don't need to save images to disk every time,
    we can just embed the chart directly into the HTML page.
    """
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    plt.close()
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    return image_base64


def get_performance_category(score):
    """
    Converts a numeric score into a readable performance category.
    Simple if-else ladder, easy to understand and modify later.
    """
    if score >= 85:
        return "Excellent"
    elif score >= 70:
        return "Good"
    elif score >= 50:
        return "Average"
    else:
        return "Needs Improvement"


def get_suggestions(study_hours, attendance, sleep_hours, assignments_completed):
    """
    Generates a small list of personalized study tips based on the
    values the student entered. Nothing fancy, just basic threshold checks.
    """
    tips = []

    if study_hours < 4:
        tips.append("Try to increase your daily study hours to at least 4-5 hours.")

    if attendance < 75:
        tips.append("Improve your class attendance, it has a noticeable impact on your score.")

    if sleep_hours < 7:
        tips.append("Try to sleep at least 7 hours a night, it helps with focus and memory.")

    if assignments_completed < 7:
        tips.append("Complete your assignments regularly, they contribute a lot to your final score.")

    # If everything looks good, give some positive feedback instead
    if not tips:
        tips.append("Great job! Keep maintaining your current study routine.")

    return tips


@app.route("/")
def home():
    """Renders the home / landing page."""
    return render_template("index.html")


@app.route("/predict", methods=["GET", "POST"])
def predict():
    """
    GET  -> just shows the input form
    POST -> reads form values, validates them, runs the model, and
            shows the prediction result on the same page
    """

    # This dictionary will hold everything we send back to the template
    result = None
    error_message = None

    if request.method == "POST":
        try:
            # Reading form values (they come in as strings by default)
            study_hours = float(request.form["study_hours"])
            attendance = float(request.form["attendance"])
            previous_score = float(request.form["previous_score"])
            assignments_completed = int(request.form["assignments_completed"])
            sleep_hours = float(request.form["sleep_hours"])
            internet_access = request.form["internet_access"]

            # ---------------- Basic input validation ----------------
            if not (0 <= study_hours <= 24):
                raise ValueError("Study hours must be between 0 and 24.")

            if not (0 <= attendance <= 100):
                raise ValueError("Attendance must be between 0 and 100.")

            if not (0 <= previous_score <= 100):
                raise ValueError("Previous score must be between 0 and 100.")

            if not (0 <= assignments_completed <= 10):
                raise ValueError("Assignments completed must be between 0 and 10.")

            if not (0 <= sleep_hours <= 24):
                raise ValueError("Sleep hours must be between 0 and 24.")

            if internet_access not in ("Yes", "No"):
                raise ValueError("Internet access must be Yes or No.")

            # Encoding internet access the same way we did during training
            internet_encoded = 1 if internet_access == "Yes" else 0

            # Building the input row in the exact same column order used in training
            input_data = np.array([[
                study_hours,
                attendance,
                previous_score,
                assignments_completed,
                sleep_hours,
                internet_encoded,
            ]])

            # Running the prediction
            predicted_score = model.predict(input_data)[0]

            # Keeping the score within a sensible 0-100 range
            predicted_score = max(0, min(100, predicted_score))

            category = get_performance_category(predicted_score)
            suggestions = get_suggestions(
                study_hours, attendance, sleep_hours, assignments_completed
            )

            result = {
                "score": round(predicted_score, 1),
                "category": category,
                "suggestions": suggestions,
            }

        except (ValueError, KeyError) as e:
            # KeyError happens if a field is missing, ValueError for bad values
            error_message = str(e) if isinstance(e, ValueError) else "Please fill in all the fields correctly."

    return render_template("predict.html", result=result, error_message=error_message)


@app.route("/dashboard")
def dashboard():
    """
    Shows dataset insights:
    - A preview table of the dataset
    - Correlation heatmap
    - Study hours vs final score scatter plot
    - Attendance distribution histogram
    - Feature importance bar chart
    - Model accuracy (R2 score)
    """

    # ---------------- Dataset preview (first 10 rows) ----------------
    dataset_preview = student_df.head(10).to_html(
        classes="preview-table", index=False, border=0
    )

    # ---------------- Correlation heatmap ----------------
    # Only using numeric columns for correlation
    numeric_df = student_df.copy()
    numeric_df["internet_access"] = numeric_df["internet_access"].map({"Yes": 1, "No": 0})
    correlation_matrix = numeric_df.corr()

    plt.figure(figsize=(6, 5))
    plt.imshow(correlation_matrix, cmap="Blues")
    plt.colorbar(label="Correlation")
    plt.xticks(range(len(correlation_matrix.columns)), correlation_matrix.columns, rotation=45, ha="right")
    plt.yticks(range(len(correlation_matrix.columns)), correlation_matrix.columns)

    # Adding correlation values on top of each cell
    for i in range(len(correlation_matrix.columns)):
        for j in range(len(correlation_matrix.columns)):
            plt.text(j, i, f"{correlation_matrix.iloc[i, j]:.2f}",
                     ha="center", va="center", color="black", fontsize=7)

    plt.title("Correlation Heatmap")
    heatmap_image = convert_plot_to_base64()

    # ---------------- Study hours vs Final score ----------------
    plt.figure(figsize=(6, 4))
    plt.scatter(student_df["study_hours"], student_df["final_score"], color="#1E5AA8", alpha=0.6)
    plt.xlabel("Study Hours")
    plt.ylabel("Final Exam Score")
    plt.title("Study Hours vs Final Exam Score")
    study_vs_score_image = convert_plot_to_base64()

    # ---------------- Attendance distribution ----------------
    plt.figure(figsize=(6, 4))
    plt.hist(student_df["attendance"], bins=15, color="#3B82F6", edgecolor="white")
    plt.xlabel("Attendance (%)")
    plt.ylabel("Number of Students")
    plt.title("Attendance Distribution")
    attendance_dist_image = convert_plot_to_base64()

    # ---------------- Feature importance ----------------
    feature_importance = model_metrics["feature_importance"]
    features = list(feature_importance.keys())
    importance_values = list(feature_importance.values())

    plt.figure(figsize=(6, 4))
    plt.barh(features, importance_values, color="#1E5AA8")
    plt.xlabel("Coefficient Value")
    plt.title("Feature Importance (Linear Regression Coefficients)")
    feature_importance_image = convert_plot_to_base64()

    return render_template(
        "dashboard.html",
        dataset_preview=dataset_preview,
        heatmap_image=heatmap_image,
        study_vs_score_image=study_vs_score_image,
        attendance_dist_image=attendance_dist_image,
        feature_importance_image=feature_importance_image,
        r2_score=model_metrics["r2_score"],
        mae=model_metrics["mae"],
    )


if __name__ == "__main__":
    # debug=True gives auto-reload + error pages, useful during development
    app.run(debug=True)