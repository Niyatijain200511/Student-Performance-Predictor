/* ============================================================
   script.js
   Handles small front-end behaviors for the
   Student Performance Predictor project:
   - Shows a loading spinner while the prediction is being processed
   - Does basic client-side validation before the form is submitted
   - Smoothly scrolls to the result card once a prediction is shown
   ============================================================ */

document.addEventListener("DOMContentLoaded", function () {

    const predictForm = document.getElementById("predictForm");
    const submitBtn = document.getElementById("submitBtn");
    const loadingSpinner = document.getElementById("loadingSpinner");

    // This code only runs on the predict page, since that's the
    // only page that has these elements. On other pages, these
    // will just be null and nothing below will execute.
    if (predictForm) {

        predictForm.addEventListener("submit", function (event) {

            // Basic front-end validation, in addition to the
            // server-side validation already done in app.py.
            const studyHours = parseFloat(document.getElementById("study_hours").value);
            const attendance = parseFloat(document.getElementById("attendance").value);
            const previousScore = parseFloat(document.getElementById("previous_score").value);
            const sleepHours = parseFloat(document.getElementById("sleep_hours").value);

            let isValid = true;
            let message = "";

            if (isNaN(studyHours) || studyHours < 0 || studyHours > 24) {
                isValid = false;
                message = "Please enter valid study hours (0-24).";
            } else if (isNaN(attendance) || attendance < 0 || attendance > 100) {
                isValid = false;
                message = "Please enter a valid attendance percentage (0-100).";
            } else if (isNaN(previousScore) || previousScore < 0 || previousScore > 100) {
                isValid = false;
                message = "Please enter a valid previous exam score (0-100).";
            } else if (isNaN(sleepHours) || sleepHours < 0 || sleepHours > 24) {
                isValid = false;
                message = "Please enter valid sleep hours (0-24).";
            }

            if (!isValid) {
                // Stop the form from submitting and alert the user
                event.preventDefault();
                alert(message);
                return;
            }

            // If everything looks fine, show the loading spinner
            // and disable the button so the user can't click it twice
            // while the prediction is being calculated on the server.
            loadingSpinner.classList.remove("hidden");
            submitBtn.disabled = true;
            submitBtn.textContent = "Predicting...";
        });
    }

    // If a prediction result is already present on page load
    // (i.e. after the form was submitted and the page reloaded
    // with the result), scroll smoothly to it so the user notices it.
    const resultCard = document.querySelector(".result-card");
    const scoreCircle = document.querySelector(".score-circle");

    if (resultCard && scoreCircle) {
        resultCard.scrollIntoView({ behavior: "smooth", block: "center" });
    }

});