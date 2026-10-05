from app.extensions import db


class ExamQuestion(db.Model):

    __tablename__ = "exam_questions"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    exam_id = db.Column(
        db.Integer,
        db.ForeignKey("exams.id"),
        nullable=False
    )

    question_id = db.Column(
        db.Integer,
        db.ForeignKey("questions.id"),
        nullable=False
    )

    question_order = db.Column(
        db.Integer,
        nullable=False
    )

    exam = db.relationship(
        "Exam",
        backref="exam_questions"
    )

    question = db.relationship(
        "Question",
        backref="exam_questions"
    )