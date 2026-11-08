from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, false, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class Visitor(db.Model):
    __tablename__ = "visitors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    student_id: Mapped[str | None] = mapped_column(String(9), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    tickets: Mapped[list["Ticket"]] = relationship(back_populates="visitor")

    __table_args__ = (
        CheckConstraint("student_id ~ '^[0-9]{4}-[0-9]{4}$'", name="ck_visitors_student_id"),
    )


class Service(db.Model):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True)
    avg_minutes: Mapped[int] = mapped_column(default=10, server_default="10")

    tickets: Mapped[list["Ticket"]] = relationship(back_populates="service")

    __table_args__ = (
        CheckConstraint("avg_minutes > 0", name="ck_services_avg_minutes"),
    )


class Window(db.Model):
    __tablename__ = "windows"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[int] = mapped_column(unique=True)

    tickets: Mapped[list["Ticket"]] = relationship(back_populates="window")

    __table_args__ = (
        CheckConstraint("number > 0", name="ck_windows_number"),
    )


class Ticket(db.Model):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String(20), default="waiting", server_default="waiting")
    is_priority: Mapped[bool] = mapped_column(default=False, server_default=false())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    called_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    visitor_id: Mapped[int] = mapped_column(ForeignKey("visitors.id", ondelete="RESTRICT"))
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id", ondelete="RESTRICT"))
    window_id: Mapped[int | None] = mapped_column(ForeignKey("windows.id", ondelete="RESTRICT"))

    visitor: Mapped["Visitor"] = relationship(back_populates="tickets")
    service: Mapped["Service"] = relationship(back_populates="tickets")
    window: Mapped["Window | None"] = relationship(back_populates="tickets")

    __table_args__ = (
        CheckConstraint(
            "status IN ('waiting', 'called', 'served', 'no-show', 'left')",
            name="ck_tickets_status",
        ),
    )