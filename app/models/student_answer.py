from app.extensions import db


class StudentAnswer(db.Model):

    __tablename__ = "student_answers"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    attempt_id = db.Column(
        db.Integer,
        db.ForeignKey("exam_attempts.id"),
        nullable=False
    )

    question_id = db.Column(
        db.Integer,
        db.ForeignKey("questions.id"),
        nullable=False
    )

    selected_answer = db.Column(
        db.String(500),
        nullable=True
    )

    text_answer = db.Column(
        db.Text,
        nullable=True
    )

    is_correct = db.Column(
        db.Boolean,
        nullable=True
    )

    marks_obtained = db.Column(
        db.Float,
        default=0
    )

    teacher_feedback = db.Column(
        db.Text,
        nullable=True
    )

    evaluated = db.Column(
        db.Boolean,
        default=False
    )

    attempt = db.relationship(
        "ExamAttempt",
        backref="answers"
    )

    question = db.relationship(
        "Question",
        backref="student_answers"
    )