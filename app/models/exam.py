from datetime import datetime, timezone

from app.extensions import db


class Exam(db.Model):

    __tablename__ = "exams"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    subject = db.Column(
        db.String(100),
        nullable=False
    )

    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    duration = db.Column(
        db.Integer,
        nullable=False
    )

    total_marks = db.Column(
        db.Integer,
        nullable=False
    )

    passing_percentage = db.Column(
        db.Float,
        default=40.0
    )

    difficulty = db.Column(
        db.String(20),
        default="Medium"
    )

    start_time = db.Column(
        db.DateTime,
        nullable=True
    )

    end_time = db.Column(
        db.DateTime,
        nullable=True
    )

    status = db.Column(
        db.String(20),
        default="Draft"
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    teacher = db.relationship(
        "User",
        backref="created_exams"
    )