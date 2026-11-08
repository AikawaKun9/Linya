"""Linya: a queue system for the campus registrar (CCC181 Week 3).

Run it with:
    flask --app app run --debug
then open http://127.0.0.1:5000
"""
import re
import os

from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask_migrate import Migrate
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from models import Service, Ticket, Visitor, Window, db

load_dotenv()

app = Flask(__name__)
app.secret_key = "dev-only-change-me"  # Week 11 moves this into an environment variable
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_ECHO"] = os.environ.get("SQLALCHEMY_ECHO") == "1"

db.init_app(app)
migrate = Migrate(app, db)

@app.cli.command("seed")
def seed():
    """Add the starting services and windows if they are not there yet."""
    services = [
        ("Transcript of Records (TOR)", 15),
        ("Certificates (enrollment, good moral, etc.)", 10),
        ("Enrollment concerns", 10),
        ("Submit requirements", 5),
    ]
    for name, minutes in services:
        exists = db.session.scalar(db.select(Service).filter_by(name=name))
        if exists is None:
            db.session.add(Service(name=name, avg_minutes=minutes))

    for number in (1, 2, 3, 4):
        exists = db.session.scalar(db.select(Window).filter_by(number=number))
        if exists is None:
            db.session.add(Window(number=number))

    db.session.commit()
    print("Services and windows are ready.")


@app.route("/")
def index():
    return render_template("index.html")

def all_services():
    return db.session.scalars(db.select(Service).order_by(Service.name)).all()


@app.get("/join")
def join_form():
    return render_template("join.html", services=all_services(), form={}, errors={})


@app.post("/join")
def join():
    form = request.form
    name = form.get("name", "").strip()
    student_id = form.get("student_id", "").strip()
    service_id = form.get("service_id", type=int)
    is_priority = form.get("priority") == "on"
    service = db.session.get(Service, service_id) if service_id else None

    errors = {}
    if not name or len(name) > 80:
        errors["name"] = "Enter your name or a nickname (up to 80 characters)."
    if student_id and not re.fullmatch(r"\d{4}-\d{4}", student_id):
        errors["student_id"] = "Use the format YYYY-#### (for example 2022-0457), or leave it blank."
    if service is None:
        errors["service_id"] = "Choose a service."

    if errors:
        flash("Please fix the highlighted fields.", "danger")
        return render_template("join.html", services=all_services(),
                               form=form, errors=errors), 400

    visitor = None
    if student_id:
        visitor = db.session.scalar(db.select(Visitor).filter_by(student_id=student_id))
    if visitor is None:
        visitor = Visitor(name=name, student_id=student_id or None)

    new_ticket = Ticket(visitor=visitor, service=service, is_priority=is_priority)
    db.session.add(new_ticket)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("Something went wrong saving your ticket. Please try again.", "danger")
        return render_template("join.html", services=all_services(),
                               form=form, errors={}), 409

    flash(f"You joined the queue. Your ticket is #{new_ticket.id}.", "success")
    return redirect(url_for("ticket", ticket_id=new_ticket.id))


def find_ticket(ticket_id):
    return next((t for t in TICKETS if t["number"] == ticket_id), None)


def queue_order(t):
    """Priority-lane tickets come first, then by ticket number."""
    return (not t.get("priority", False), t["number"])


def count_ahead(t):
    """People still waiting ahead of this ticket, for the same service."""
    return sum(1 for x in TICKETS
               if x["service_id"] == t["service_id"]
               and x["status"] == "waiting"
               and queue_order(x) < queue_order(t))


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


@app.get("/queue/<int:ticket_id>/status.json")
def ticket_status(ticket_id):
    t = find_ticket(ticket_id)
    if t is None:
        abort(404)
    return {"status": t["status"], "ahead": count_ahead(t), "window": t["window"]}


@app.get("/staff")
def staff_dashboard():
    service_id = request.args.get("service_id", type=int)
    active = [t for t in TICKETS if t["status"] in ("waiting", "called")]
    if service_id:
        active = [t for t in active if t["service_id"] == service_id]
    # called tickets first, then waiting ones in queue order
    active.sort(key=lambda t: (t["status"] != "called", queue_order(t)))

    names = {s["id"]: s["name"] for s in SERVICES}
    counts = {s["id"]: sum(1 for t in TICKETS
                           if t["service_id"] == s["id"] and t["status"] == "waiting")
              for s in SERVICES}
    return render_template("staff.html", queue=active, services=SERVICES,
                           names=names, counts=counts, selected=service_id)


@app.post("/staff/call-next")
def call_next():
    service_id = request.form.get("service_id", type=int)
    window = request.form.get("window", type=int)

    if not window or window < 1:
        flash("Enter a window number (1 or higher).", "danger")
        return redirect(url_for("staff_dashboard", service_id=service_id))

    waiting = [t for t in TICKETS if t["status"] == "waiting"
               and (not service_id or t["service_id"] == service_id)]
    if not waiting:
        flash("No one is waiting.", "warning")
        return redirect(url_for("staff_dashboard", service_id=service_id))

    nxt = min(waiting, key=queue_order)
    nxt["status"] = "called"
    nxt["window"] = window
    flash(f"Called ticket #{nxt['number']} to Window {window}.", "success")
    return redirect(url_for("staff_dashboard", service_id=service_id))


@app.post("/staff/tickets/<int:ticket_id>/<action>")
def staff_action(ticket_id, action):
    new_status = {"serve": "served", "no-show": "no-show"}.get(action)
    t = find_ticket(ticket_id)
    if t is None or new_status is None:
        abort(404)
    t["status"] = new_status
    flash(f"Ticket #{ticket_id} marked {new_status}.", "info")
    return redirect(url_for("staff_dashboard",
                            service_id=request.form.get("service_id", type=int)))

if __name__ == "__main__":
    app.run(debug=True)