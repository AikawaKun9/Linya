"""Linya: a queue system for the campus registrar (CCC181 Week 3).

Run it with:
    flask --app app run --debug
then open http://127.0.0.1:5000
"""
import re

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
     "service_id": 1, "priority": False, "window": 3, "status": "called"},
    {"number": 2, "name": "Ben Cruz", "student_id": "2022-0457",
     "service_id": 2, "priority": True, "window": None, "status": "waiting"},
]


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/join")
def join_form():
    return render_template("join.html", services=SERVICES, form={}, errors={})


@app.post("/join")
def join():
    form = request.form
    name = form.get("name", "").strip()
    student_id = form.get("student_id", "").strip()
    service_id = form.get("service_id", type=int)
    priority = form.get("priority") == "on"

    errors = {}
    if not name:
        errors["name"] = "Enter your name or a nickname."
    if student_id and not re.fullmatch(r"\d{4}-\d{4}", student_id):
        errors["student_id"] = "Use the format YYYY-#### (for example 2022-0457), or leave it blank."
    if service_id not in [s["id"] for s in SERVICES]:
        errors["service_id"] = "Choose a service."

    if errors:
        flash("Please fix the highlighted fields.", "danger")
        return render_template("join.html", services=SERVICES, form=form,
                               errors=errors), 400

    number = TICKETS[-1]["number"] + 1 if TICKETS else 1
    TICKETS.append({
        "number": number, "name": name, "student_id": student_id or None,
        "service_id": service_id, "p    riority": priority,
        "window": None, "status": "waiting",
    })
    flash(f"You joined the queue. Your ticket is #{number}.", "success")
    return redirect(url_for("ticket", ticket_id=number))


@app.route("/staff")
def staff_dashboard():
    return "Staff dashboard coming soon"


def find_ticket(ticket_id):
    return next((t for t in TICKETS if t["number"] == ticket_id), None)


def count_ahead(t):
    """People still waiting ahead of this ticket, for the same service."""
    return sum(1 for x in TICKETS
               if x["service_id"] == t["service_id"]
               and x["status"] == "waiting"
               and x["number"] < t["number"])


@app.get("/queue/<int:ticket_id>")
def ticket(ticket_id):
    t = find_ticket(ticket_id)
    if t is None:
        abort(404)
    service = next(s for s in SERVICES if s["id"] == t["service_id"])
    return render_template("ticket.html", ticket=t, service=service,
                           ahead=count_ahead(t))


@app.post("/queue/<int:ticket_id>/leave")
def leave_queue(ticket_id):
    t = find_ticket(ticket_id)
    if t is None:
        abort(404)
    if t["status"] in ("waiting", "called"):
        t["status"] = "no-show"
    flash("You left the queue.", "info")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)