"""Linya: a queue system for the campus registrar (CCC181 Week 3).

Run it with:
    flask --app app run --debug
then open http://127.0.0.1:5000
"""
from flask import Flask, abort, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = "dev-only-change-me"  # Week 11 moves this into an environment variable

SERVICES = [
    {"id": 1, "name": "Transcript of Records (TOR)"},
    {"id": 2, "name": "Certificates (enrollment, good moral, etc.)"},
    {"id": 3, "name": "Enrollment concerns"},
    {"id": 4, "name": "Submit requirements"},
]

# status is one of: waiting, called, served, no-show
# window is None until staff call the ticket
TICKETS = [
    {"number": 1, "name": "Ana Reyes", "student_id": "2023-0001",
     "email": "ana@school.edu", "service_id": 1,
     "priority": False, "window": None, "status": "waiting"},
    {"number": 2, "name": "Ben Cruz", "student_id": "2022-0457",
     "email": "ben@school.edu", "service_id": 2,
     "priority": True, "window": None, "status": "waiting"},
]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/join")
def join_form():
    return render_template("join.html")


@app.route("/staff")
def staff_dashboard():
    return "Staff dashboard coming soon"


@app.route("/queue/<int:ticket_id>")
def ticket(ticket_id):
    # Temporary: Part 6 replaces this with the real My place page.
    return render_template("ticket.html", ticket_id=ticket_id)


if __name__ == "__main__":
    app.run(debug=True)