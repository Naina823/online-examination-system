from app.extensions import db


class Question(db.Model):

    __tablename__ = "questions"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    question_text = db.Column(
        db.Text,
        nullable=False
    )

    question_type = db.Column(
        db.String(30),
        nullable=False
    )

    marks = db.Column(
        db.Float,
        nullable=False,
        default=1
    )

    correct_answer = db.Column(
        db.Text,
        nullable=True
    )

    explanation = db.Column(
        db.Text,
        nullable=True
    )

    difficulty = db.Column(
        db.String(20),
        default="Medium"
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    options = db.relationship(
        "QuestionOption",
        backref="question",
        cascade="all, delete-orphan"
    )