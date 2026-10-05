from app.extensions import db


class QuestionOption(db.Model):

    __tablename__ = "question_options"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    question_id = db.Column(
        db.Integer,
        db.ForeignKey("questions.id"),
        nullable=False
    )

    option_text = db.Column(
        db.String(500),
        nullable=False
    )

    option_label = db.Column(
        db.String(5),
        nullable=False
    )

    is_correct = db.Column(
        db.Boolean,
        default=False
    )