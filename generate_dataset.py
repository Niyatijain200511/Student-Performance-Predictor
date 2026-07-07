"""
generate_dataset.py

Small helper script used to create the student_data.csv file.
I could not find a public dataset that matched exactly what I needed
for this project, so I wrote this script to generate a synthetic but
fairly realistic dataset based on some reasonable assumptions about
how study habits affect exam scores.

Run this only if you want to regenerate the dataset from scratch.
The CSV is already included in the dataset/ folder, so this step
is optional.
"""

import numpy as np
import pandas as pd

# Setting a seed so the dataset is the same every time we run this script
np.random.seed(42)

NUM_STUDENTS = 500

# ---- Generating individual features ----

# Study hours per day (most students study between 0.5 and 9 hours)
study_hours = np.round(np.random.uniform(0.5, 9, NUM_STUDENTS), 1)

# Attendance percentage (skewed towards higher attendance, like real classes)
attendance = np.round(np.random.normal(80, 12, NUM_STUDENTS), 1)
attendance = np.clip(attendance, 40, 100)

# Previous exam score (some correlation with attendance, plus randomness)
previous_score = attendance * 0.5 + np.random.normal(30, 10, NUM_STUDENTS)
previous_score = np.clip(np.round(previous_score, 1), 30, 100)

# Assignments completed out of 10
assignments_completed = np.random.randint(0, 11, NUM_STUDENTS)

# Sleep hours per night (most students sleep between 4 and 9 hours)
sleep_hours = np.round(np.random.uniform(4, 9, NUM_STUDENTS), 1)

# Internet access at home (majority yes, like most urban students today)
internet_access = np.random.choice(["Yes", "No"], NUM_STUDENTS, p=[0.85, 0.15])

# ---- Building the final exam score using a weighted formula ----
# Weights below are just approximations of how much each factor
# realistically affects performance. Some random noise is added
# so the relationship isn't perfectly linear (like real life).

internet_bonus = np.where(internet_access == "Yes", 3, 0)

final_score = (
    study_hours * 4.2
    + attendance * 0.25
    + previous_score * 0.25
    + assignments_completed * 1.8
    + sleep_hours * 1.1
    + internet_bonus
    + np.random.normal(0, 5, NUM_STUDENTS)  # natural randomness
)

# Keeping scores within a realistic 0-100 range
final_score = np.clip(np.round(final_score, 1), 0, 100)

# ---- Putting everything into a DataFrame ----
student_data = pd.DataFrame({
    "study_hours": study_hours,
    "attendance": attendance,
    "previous_score": previous_score,
    "assignments_completed": assignments_completed,
    "sleep_hours": sleep_hours,
    "internet_access": internet_access,
    "final_score": final_score
})

# Saving to CSV
student_data.to_csv("dataset/student_data.csv", index=False)

print("Dataset created successfully!")
print(f"Total records: {len(student_data)}")
print(student_data.head())