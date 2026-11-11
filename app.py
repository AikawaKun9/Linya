"""Linya: a queue system for the campus registrar (CCC181 Week 4).

Run it with:
    flask --app app run --debug
then open http://127.0.0.1:5000
"""
import os
import re
from datetime import timedelta, timezone

from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask_migrate import Migrate
from sqlalchemy import and_, func, or_
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


#helpers

PH_TIME = timezone(timedelta(hours=8))  # Philippine time has no daylight saving


@app.template_filter("local")
def local_time(value):
    """Show a database time in Philippine time, e.g. Nov 02, 08:01 AM."""
    return value.astimezone(PH_TIME).strftime("%b %d, %I:%M %p") if value else ""


def all_services():
    return db.session.scalars(db.select(Service).order_by(Service.name)).all()


def active_services():
    stmt = db.select(Service).filter_by(active=True).order_by(Service.name)
    return db.session.scalars(stmt).all()


def all_windows():
    return db.session.scalars(db.select(Window).order_by(Window.number)).all()


def people_ahead(t):
    """Count waiting tickets for the same service that will be called before t.

    Priority tickets go first. Within the same lane, earlier join time goes first.
    """
    earlier_same_lane = and_(Ticket.is_priority == t.is_priority,
                             Ticket.created_at < t.created_at)
    if t.is_priority:
        before_me = earlier_same_lane
    else:
        before_me = or_(Ticket.is_priority.is_(True), earlier_same_lane)

    stmt = (db.select(func.count())
            .select_from(Ticket)
            .where(Ticket.service_id == t.service_id,
                   Ticket.status == "waiting",
                   before_me))
    return db.session.scalar(stmt)


#student pages

@app.route("/")
def index():
    return render_template("index.html")


@app.get("/join")
def join_form():
    return render_template("join.html", services=active_services(), form={}, errors={})


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
    if service is None or not service.active:
        errors["service_id"] = "Choose a service."

    if errors:
        flash("Please fix the highlighted fields.", "danger")
        return render_template("join.html", services=active_services(),
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
        return render_template("join.html", services=active_services(),
                               form=form, errors={}), 409

    flash(f"You joined the queue. Your ticket is #{new_ticket.id}.", "success")
    return redirect(url_for("ticket", ticket_id=new_ticket.id))


@app.get("/queue/<int:ticket_id>")
def ticket(ticket_id):
    t = db.get_or_404(Ticket, ticket_id)
    return render_template("ticket.html", ticket=t, service=t.service,
                           ahead=people_ahead(t))


@app.get("/queue/<int:ticket_id>/status.json")
def ticket_status(ticket_id):
    t = db.get_or_404(Ticket, ticket_id)
    return {"status": t.status, "ahead": people_ahead(t),
            "window": t.window.number if t.window else None}


@app.post("/queue/<int:ticket_id>/leave")
def leave_queue(ticket_id):
    t = db.get_or_404(Ticket, ticket_id)
    if t.status in ("waiting", "called"):
        t.status = "left"  # soft delete: the row stays for reports
        t.finished_at = func.now()
        db.session.commit()
    flash("You left the queue.", "info")
    return redirect(url_for("index"))


#staff

@app.get("/staff")
def staff_dashboard():
    service_id = request.args.get("service_id", type=int)
    stmt = (db.select(Ticket)
            .where(Ticket.status.in_(["waiting", "called"]))
            .order_by((Ticket.status == "called").desc(),
                      Ticket.is_priority.desc(),
                      Ticket.created_at))
    if service_id:
        stmt = stmt.where(Ticket.service_id == service_id)
    queue = db.session.scalars(stmt).all()

    services = all_services()
    names = {s.id: s.name for s in services}
    counts = dict(db.session.execute(
        db.select(Ticket.service_id, func.count())
        .where(Ticket.status == "waiting")
        .group_by(Ticket.service_id)).all())
    return render_template("staff.html", queue=queue, services=services,
                           windows=all_windows(), names=names, counts=counts,
                           selected=service_id)


@app.post("/staff/call-next")
def call_next():
    service_id = request.form.get("service_id", type=int)
    number = request.form.get("window", type=int)
    window = db.session.scalar(db.select(Window).filter_by(number=number)) if number else None

    if window is None:
        flash("Choose a window.", "danger")
        return redirect(url_for("staff_dashboard", service_id=service_id))

    stmt = (db.select(Ticket)
            .where(Ticket.status == "waiting")
            .order_by(Ticket.is_priority.desc(), Ticket.created_at)
            .limit(1))
    if service_id:
        stmt = stmt.where(Ticket.service_id == service_id)
    nxt = db.session.scalar(stmt)

    if nxt is None:
        flash("No one is waiting.", "warning")
        return redirect(url_for("staff_dashboard", service_id=service_id))

    nxt.status = "called"
    nxt.window = window
    nxt.called_at = func.now()  # the database fills in the time
    db.session.commit()
    flash(f"Called ticket #{nxt.id} to Window {window.number}.", "success")
    return redirect(url_for("staff_dashboard", service_id=service_id))


STAFF_ACTIONS = {"serve": "served", "no-show": "no-show"}


@app.post("/staff/tickets/<int:ticket_id>/delete")
def delete_ticket(ticket_id):
    """Hard delete: the ticket is gone for good (for tickets made by mistake)."""
    t = db.get_or_404(Ticket, ticket_id)
    visitor = t.visitor
    db.session.delete(t)
    db.session.flush()
    # Do not keep a visitor with no tickets: it is personal data with no purpose.
    others = db.session.scalar(
        db.select(func.count()).select_from(Ticket).where(Ticket.visitor_id == visitor.id))
    if others == 0:
        db.session.delete(visitor)
    db.session.commit()
    flash(f"Ticket #{ticket_id} was deleted.", "warning")
    return redirect(url_for("staff_dashboard",
                            service_id=request.form.get("service_id", type=int)))


@app.post("/staff/tickets/<int:ticket_id>/<action>")
def staff_action(ticket_id, action):
    new_status = STAFF_ACTIONS.get(action)
    if new_status is None:
        abort(404)
    t = db.get_or_404(Ticket, ticket_id)
    t.status = new_status
    t.finished_at = func.now()
    db.session.commit()
    flash(f"Ticket #{ticket_id} marked {new_status}.", "info")
    return redirect(url_for("staff_dashboard",
                            service_id=request.form.get("service_id", type=int)))


#staff: manage services

@app.get("/staff/services")
def services_list():
    return render_template("services.html", services=all_services())


def read_service_form():
    """Return (name, minutes, error message or None) from the submitted form."""
    name = request.form.get("name", "").strip()
    minutes = request.form.get("avg_minutes", type=int)
    if not name or len(name) > 60 or not minutes or minutes <= 0:
        return name, minutes, "Enter a name (up to 60 characters) and minutes greater than 0."
    return name, minutes, None


@app.post("/staff/services")
def service_create():
    name, minutes, error = read_service_form()
    if error:
        flash(error, "danger")
        return redirect(url_for("services_list"))
    db.session.add(Service(name=name, avg_minutes=minutes))
    try:
        db.session.commit()
        flash(f"Service “{name}” added.", "success")
    except IntegrityError:
        db.session.rollback()
        flash(f"A service named “{name}” already exists.", "danger")
    return redirect(url_for("services_list"))


@app.post("/staff/services/<int:service_id>")
def service_edit(service_id):
    s = db.get_or_404(Service, service_id)
    name, minutes, error = read_service_form()
    if error:
        flash(error, "danger")
        return redirect(url_for("services_list"))
    s.name = name
    s.avg_minutes = minutes
    s.active = request.form.get("active") == "on"  # an unticked box is not sent at all
    try:
        db.session.commit()
        flash(f"Service “{name}” saved.", "success")
    except IntegrityError:
        db.session.rollback()
        flash(f"A service named “{name}” already exists.", "danger")
    return redirect(url_for("services_list"))


@app.post("/staff/services/<int:service_id>/delete")
def service_delete(service_id):
    s = db.get_or_404(Service, service_id)
    if s.tickets:
        flash(f"“{s.name}” has tickets, so it cannot be deleted. Turn it off instead.", "danger")
        return redirect(url_for("services_list"))
    name = s.name
    db.session.delete(s)
    db.session.commit()
    flash(f"Service “{name}” deleted.", "warning")
    return redirect(url_for("services_list"))


if __name__ == "__main__":
    app.run(debug=True)