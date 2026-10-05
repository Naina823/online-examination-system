from datetime import datetime, timezone

from app.extensions import db


class ExamAttempt(db.Model):

    __tablename__ = "exam_attempts"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    exam_id = db.Column(
        db.Integer,
        db.ForeignKey("exams.id"),
        nullable=False
    )

    started_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    submitted_at = db.Column(
        db.DateTime,
        nullable=True
    )

    score = db.Column(
        db.Float,
        nullable=True
    )

    percentage = db.Column(
        db.Float,
        nullable=True
    )

    status = db.Column(
        db.String(30),
        default="In Progress"
    )

    student = db.relationship(
        "User",
        backref="exam_attempts"
    )

    exam = db.relationship(
        "Exam",
        backref="attempts"
    )