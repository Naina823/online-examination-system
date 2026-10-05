from datetime import datetime, timezone
from functools import wraps

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
)

from flask_login import login_required, current_user

from app.teacher import teacher_bp
from app.extensions import db

from app.models.exam import Exam
from app.models.question import Question
from app.models.question_option import QuestionOption
from app.models.exam_question import ExamQuestion
from app.models.exam_attempt import ExamAttempt
from app.models.student_answer import StudentAnswer


# ============================================================
# TEACHER ACCESS CONTROL
# ============================================================

def teacher_required(view_function):

    @wraps(view_function)
    @login_required
    def wrapped(*args, **kwargs):

        if current_user.role != "teacher":
            flash(
                "You are not authorized to access the teacher panel.",
                "danger"
            )

            return redirect(
                url_for("main.home")
            )

        return view_function(*args, **kwargs)

    return wrapped


# ============================================================
# TEACHER DASHBOARD
# ============================================================

@teacher_bp.route("/dashboard")
@teacher_required
def dashboard():

    exams = (
        Exam.query
        .filter_by(teacher_id=current_user.id)
        .order_by(Exam.created_at.desc())
        .all()
    )

    total_exams = len(exams)

    published_exams = sum(
        1 for exam in exams
        if exam.status == "Published"
    )

    draft_exams = sum(
        1 for exam in exams
        if exam.status == "Draft"
    )

    exam_ids = [exam.id for exam in exams]

    student_attempts = 0

    if exam_ids:

        student_attempts = (
            ExamAttempt.query
            .filter(
                ExamAttempt.exam_id.in_(exam_ids)
            )
            .count()
        )

    return render_template(
        "teacher/dashboard.html",
        exams=exams,
        total_exams=total_exams,
        published_exams=published_exams,
        draft_exams=draft_exams,
        student_attempts=student_attempts,
    )


# ============================================================
# VIEW ALL EXAMS
# ============================================================

@teacher_bp.route("/exams")
@teacher_required
def exams():

    exams = (
        Exam.query
        .filter_by(teacher_id=current_user.id)
        .order_by(Exam.created_at.desc())
        .all()
    )

    return render_template(
        "teacher/exams.html",
        exams=exams
    )


# ============================================================
# CREATE EXAM
# ============================================================

@teacher_bp.route("/create-exam", methods=["GET", "POST"])
@teacher_required
def create_exam():

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        subject = request.form.get(
            "subject",
            ""
        ).strip()

        duration = request.form.get(
            "duration",
            ""
        ).strip()

        total_marks = request.form.get(
            "total_marks",
            ""
        ).strip()

        passing_percentage = request.form.get(
            "passing_percentage",
            "40"
        ).strip()

        difficulty = request.form.get(
            "difficulty",
            "Medium"
        ).strip()

        start_time = request.form.get(
            "start_time",
            ""
        ).strip()

        end_time = request.form.get(
            "end_time",
            ""
        ).strip()


        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if not title:

            flash(
                "Exam title is required.",
                "danger"
            )

            return redirect(
                url_for("teacher.create_exam")
            )


        if not subject:

            flash(
                "Subject is required.",
                "danger"
            )

            return redirect(
                url_for("teacher.create_exam")
            )


        try:

            duration = int(duration)
            total_marks = int(total_marks)
            passing_percentage = float(
                passing_percentage
            )

        except ValueError:

            flash(
                "Please enter valid numeric values.",
                "danger"
            )

            return redirect(
                url_for("teacher.create_exam")
            )


        if duration <= 0:

            flash(
                "Duration must be greater than zero.",
                "danger"
            )

            return redirect(
                url_for("teacher.create_exam")
            )


        if total_marks <= 0:

            flash(
                "Total marks must be greater than zero.",
                "danger"
            )

            return redirect(
                url_for("teacher.create_exam")
            )


        if not 0 <= passing_percentage <= 100:

            flash(
                "Passing percentage must be between 0 and 100.",
                "danger"
            )

            return redirect(
                url_for("teacher.create_exam")
            )


        # ----------------------------------------------------
        # DATETIME
        # ----------------------------------------------------

        parsed_start_time = None
        parsed_end_time = None

        try:

            if start_time:

                parsed_start_time = datetime.fromisoformat(
                    start_time
                )

            if end_time:

                parsed_end_time = datetime.fromisoformat(
                    end_time
                )

        except ValueError:

            flash(
                "Invalid examination date/time.",
                "danger"
            )

            return redirect(
                url_for("teacher.create_exam")
            )


        if (
            parsed_start_time
            and parsed_end_time
            and parsed_end_time <= parsed_start_time
        ):

            flash(
                "End time must be after start time.",
                "danger"
            )

            return redirect(
                url_for("teacher.create_exam")
            )


        # ----------------------------------------------------
        # CREATE EXAM
        # ----------------------------------------------------

        exam = Exam(

            title=title,

            description=description,

            subject=subject,

            teacher_id=current_user.id,

            duration=duration,

            total_marks=total_marks,

            passing_percentage=passing_percentage,

            difficulty=difficulty,

            start_time=parsed_start_time,

            end_time=parsed_end_time,

            status="Draft",

        )

        db.session.add(exam)

        db.session.commit()


        flash(
            "Examination saved as draft. Now add questions.",
            "success"
        )


        return redirect(
            url_for(
                "teacher.add_questions",
                exam_id=exam.id
            )
        )


    return render_template(
        "teacher/create_exam.html"
    )


# ============================================================
# ADD QUESTIONS
# ============================================================

@teacher_bp.route(
    "/add-questions/<int:exam_id>",
    methods=["GET"]
)
@teacher_required
def add_questions(exam_id):

    exam = Exam.query.get_or_404(exam_id)


    if exam.teacher_id != current_user.id:

        abort(403)


    exam_questions = (
        ExamQuestion.query
        .filter_by(exam_id=exam.id)
        .order_by(
            ExamQuestion.question_order.asc()
        )
        .all()
    )


    return render_template(
        "teacher/add_questions.html",
        exam=exam,
        exam_questions=exam_questions
    )


# ============================================================
# ADD QUESTION
# ============================================================

@teacher_bp.route(
    "/add-question",
    methods=["POST"]
)
@teacher_required
def add_question():

    exam_id = request.form.get(
        "exam_id"
    )

    exam = Exam.query.get_or_404(exam_id)


    if exam.teacher_id != current_user.id:

        abort(403)


    if exam.status == "Published":

        flash(
            "Published examinations cannot be modified.",
            "danger"
        )

        return redirect(
            url_for(
                "teacher.add_questions",
                exam_id=exam.id
            )
        )


    question_text = request.form.get(
        "question_text",
        ""
    ).strip()

    question_type = request.form.get(
        "question_type",
        ""
    ).strip()

    marks = request.form.get(
        "marks",
        "1"
    ).strip()

    difficulty = request.form.get(
        "difficulty",
        "Medium"
    ).strip()

    explanation = request.form.get(
        "explanation",
        ""
    ).strip()


    if not question_text:

        flash(
            "Please enter the question.",
            "danger"
        )

        return redirect(
            url_for(
                "teacher.add_questions",
                exam_id=exam.id
            )
        )


    try:

        marks = float(marks)

    except ValueError:

        flash(
            "Marks must be a valid number.",
            "danger"
        )

        return redirect(
            url_for(
                "teacher.add_questions",
                exam_id=exam.id
            )
        )


    if marks <= 0:

        flash(
            "Marks must be greater than zero.",
            "danger"
        )

        return redirect(
            url_for(
                "teacher.add_questions",
                exam_id=exam.id
            )
        )


    correct_answer = None


    # ========================================================
    # MCQ
    # ========================================================

    if question_type == "MCQ":

        option_a = request.form.get(
            "option_a",
            ""
        ).strip()

        option_b = request.form.get(
            "option_b",
            ""
        ).strip()

        option_c = request.form.get(
            "option_c",
            ""
        ).strip()

        option_d = request.form.get(
            "option_d",
            ""
        ).strip()

        correct_answer = request.form.get(
            "mcq_correct_answer",
            ""
        ).strip()


        if not all([
            option_a,
            option_b,
            option_c,
            option_d
        ]):

            flash(
                "Please enter all four options.",
                "danger"
            )

            return redirect(
                url_for(
                    "teacher.add_questions",
                    exam_id=exam.id
                )
            )


        if correct_answer not in [
            "A",
            "B",
            "C",
            "D"
        ]:

            flash(
                "Please select the correct MCQ option.",
                "danger"
            )

            return redirect(
                url_for(
                    "teacher.add_questions",
                    exam_id=exam.id
                )
            )


    # ========================================================
    # TRUE / FALSE
    # ========================================================

    elif question_type == "True/False":

        correct_answer = request.form.get(
            "tf_correct_answer",
            ""
        ).strip()


        if correct_answer not in [
            "True",
            "False"
        ]:

            flash(
                "Please select True or False.",
                "danger"
            )

            return redirect(
                url_for(
                    "teacher.add_questions",
                    exam_id=exam.id
                )
            )


    # ========================================================
    # SHORT / LONG ANSWER
    # ========================================================

    elif question_type in [
        "Short Answer",
        "Long Answer"
    ]:

        correct_answer = request.form.get(
            "text_correct_answer",
            ""
        ).strip()


    else:

        flash(
            "Invalid question type.",
            "danger"
        )

        return redirect(
            url_for(
                "teacher.add_questions",
                exam_id=exam.id
            )
        )


    # ========================================================
    # CREATE QUESTION
    # ========================================================

    question = Question(

        question_text=question_text,

        question_type=question_type,

        marks=marks,

        correct_answer=correct_answer,

        explanation=explanation,

        difficulty=difficulty,

    )

    db.session.add(question)

    db.session.flush()


    # ========================================================
    # OPTIONS
    # ========================================================

    if question_type == "MCQ":

        options = [

            QuestionOption(
                question_id=question.id,
                option_label="A",
                option_text=option_a,
                is_correct=(
                    correct_answer == "A"
                )
            ),

            QuestionOption(
                question_id=question.id,
                option_label="B",
                option_text=option_b,
                is_correct=(
                    correct_answer == "B"
                )
            ),

            QuestionOption(
                question_id=question.id,
                option_label="C",
                option_text=option_c,
                is_correct=(
                    correct_answer == "C"
                )
            ),

            QuestionOption(
                question_id=question.id,
                option_label="D",
                option_text=option_d,
                is_correct=(
                    correct_answer == "D"
                )
            ),

        ]

        db.session.add_all(options)


    # ========================================================
    # EXAM QUESTION ORDER
    # ========================================================

    existing_count = (
        ExamQuestion.query
        .filter_by(exam_id=exam.id)
        .count()
    )


    exam_question = ExamQuestion(

        exam_id=exam.id,

        question_id=question.id,

        question_order=existing_count + 1

    )

    db.session.add(exam_question)

    db.session.commit()


    flash(
        "Question added successfully.",
        "success"
    )


    return redirect(
        url_for(
            "teacher.add_questions",
            exam_id=exam.id
        )
    )


# ============================================================
# PUBLISH EXAM
# ============================================================

@teacher_bp.route(
    "/publish-exam/<int:exam_id>",
    methods=["POST"]
)
@teacher_required
def publish_exam(exam_id):

    exam = Exam.query.get_or_404(exam_id)


    if exam.teacher_id != current_user.id:

        abort(403)


    question_count = (
        ExamQuestion.query
        .filter_by(exam_id=exam.id)
        .count()
    )


    if question_count == 0:

        flash(
            "You must add at least one question before publishing.",
            "danger"
        )

        return redirect(
            url_for(
                "teacher.add_questions",
                exam_id=exam.id
            )
        )


    exam.status = "Published"

    db.session.commit()


    flash(
        "Examination published successfully.",
        "success"
    )


    return redirect(
        url_for(
            "teacher.exams"
        )
    )


# ============================================================
# TEACHER SUBMISSIONS
# ============================================================

@teacher_bp.route("/submissions")
@teacher_required
def submissions():

    teacher_exam_ids = [
        exam.id
        for exam in (
            Exam.query
            .filter_by(
                teacher_id=current_user.id
            )
            .all()
        )
    ]


    attempts = []


    if teacher_exam_ids:

        attempts = (
            ExamAttempt.query
            .filter(
                ExamAttempt.exam_id.in_(
                    teacher_exam_ids
                ),
                ExamAttempt.status.in_([
                    "Submitted",
                    "Evaluated",
                    "Published"
                ])
            )
            .order_by(
                ExamAttempt.submitted_at.desc()
            )
            .all()
        )


    return render_template(
        "teacher/submissions.html",
        attempts=attempts
    )


# ============================================================
# EVALUATE ATTEMPT
# ============================================================

@teacher_bp.route(
    "/evaluate/<int:attempt_id>",
    methods=["GET", "POST"]
)
@teacher_required
def evaluate_attempt(attempt_id):

    attempt = ExamAttempt.query.get_or_404(
        attempt_id
    )

    exam = attempt.exam


    # --------------------------------------------------------
    # SECURITY
    # --------------------------------------------------------

    if exam.teacher_id != current_user.id:

        abort(403)


    if attempt.status == "In Progress":

        flash(
            "This examination has not been submitted yet.",
            "warning"
        )

        return redirect(
            url_for(
                "teacher.submissions"
            )
        )


    exam_questions = (
        ExamQuestion.query
        .filter_by(
            exam_id=exam.id
        )
        .order_by(
            ExamQuestion.question_order.asc()
        )
        .all()
    )


    answers_by_question = {
        answer.question_id: answer
        for answer in attempt.answers
    }


    # ========================================================
    # SAVE EVALUATION
    # ========================================================

    if request.method == "POST":

        try:

            for exam_question in exam_questions:

                question = exam_question.question

                answer = answers_by_question.get(
                    question.id
                )


                if answer is None:

                    # Create an empty answer record
                    # if the student left the question unanswered.

                    answer = StudentAnswer(

                        attempt_id=attempt.id,

                        question_id=question.id,

                        selected_answer=None,

                        text_answer=None,

                        is_correct=False,

                        marks_obtained=0,

                        evaluated=False

                    )

                    db.session.add(answer)

                    answers_by_question[
                        question.id
                    ] = answer


                # ------------------------------------------------
                # OBJECTIVE QUESTIONS
                # ------------------------------------------------

                if question.question_type in [
                    "MCQ",
                    "True/False"
                ]:

                    # Already automatically evaluated
                    answer.evaluated = True

                    continue


                # ------------------------------------------------
                # DESCRIPTIVE QUESTIONS
                # ------------------------------------------------

                marks_field = (
                    f"marks_{question.id}"
                )

                feedback_field = (
                    f"feedback_{question.id}"
                )


                marks_value = request.form.get(
                    marks_field,
                    "0"
                ).strip()

                feedback = request.form.get(
                    feedback_field,
                    ""
                ).strip()


                try:

                    marks_awarded = float(
                        marks_value
                    )

                except ValueError:

                    flash(
                        f"Invalid marks for Question {exam_question.question_order}.",
                        "danger"
                    )

                    return redirect(
                        url_for(
                            "teacher.evaluate_attempt",
                            attempt_id=attempt.id
                        )
                    )


                if marks_awarded < 0:

                    flash(
                        f"Marks cannot be negative for Question {exam_question.question_order}.",
                        "danger"
                    )

                    return redirect(
                        url_for(
                            "teacher.evaluate_attempt",
                            attempt_id=attempt.id
                        )
                    )


                if marks_awarded > question.marks:

                    flash(
                        f"Marks for Question {exam_question.question_order} cannot exceed {question.marks}.",
                        "danger"
                    )

                    return redirect(
                        url_for(
                            "teacher.evaluate_attempt",
                            attempt_id=attempt.id
                        )
                    )


                answer.marks_obtained = marks_awarded

                answer.teacher_feedback = feedback

                answer.evaluated = True


            db.session.flush()


            # ====================================================
            # CHECK WHETHER ALL DESCRIPTIVE QUESTIONS ARE DONE
            # ====================================================

            descriptive_questions = [
                eq.question
                for eq in exam_questions
                if eq.question.question_type
                in [
                    "Short Answer",
                    "Long Answer"
                ]
            ]


            all_evaluated = all(

                answers_by_question[
                    question.id
                ].evaluated

                for question in descriptive_questions

                if question.id in answers_by_question

            )


            # If there are no descriptive questions,
            # everything is already automatically evaluated.

            if all_evaluated:

                attempt.status = "Evaluated"


            # ====================================================
            # CALCULATE SCORE
            # ====================================================

            total_score = sum(

                float(answer.marks_obtained or 0)

                for answer in answers_by_question.values()

            )


            attempt.score = total_score


            if exam.total_marks > 0:

                attempt.percentage = (
                    total_score
                    / exam.total_marks
                ) * 100

            else:

                attempt.percentage = 0


            db.session.commit()


            flash(
                "Evaluation saved successfully.",
                "success"
            )


            return redirect(
                url_for(
                    "teacher.evaluate_attempt",
                    attempt_id=attempt.id
                )
            )


        except Exception as error:

            db.session.rollback()

            flash(
                f"Could not save evaluation: {error}",
                "danger"
            )


    # ========================================================
    # CALCULATE CURRENT SCORE
    # ========================================================

    current_score = sum(

        float(answer.marks_obtained or 0)

        for answer in attempt.answers

    )


    if exam.total_marks:

        current_percentage = (
            current_score
            / exam.total_marks
        ) * 100

    else:

        current_percentage = 0


    return render_template(

        "teacher/evaluate_attempt.html",

        attempt=attempt,

        exam=exam,

        exam_questions=exam_questions,

        answers_by_question=answers_by_question,

        current_score=current_score,

        current_percentage=current_percentage

    )


# ============================================================
# PUBLISH RESULT
# ============================================================

@teacher_bp.route(
    "/publish-result/<int:attempt_id>",
    methods=["POST"]
)
@teacher_required
def publish_result(attempt_id):

    attempt = ExamAttempt.query.get_or_404(
        attempt_id
    )

    exam = attempt.exam


    if exam.teacher_id != current_user.id:

        abort(403)


    if attempt.status == "In Progress":

        flash(
            "This examination has not been submitted.",
            "danger"
        )

        return redirect(
            url_for(
                "teacher.submissions"
            )
        )


    exam_questions = (
        ExamQuestion.query
        .filter_by(
            exam_id=exam.id
        )
        .all()
    )


    # --------------------------------------------------------
    # CHECK DESCRIPTIVE ANSWERS
    # --------------------------------------------------------

    for exam_question in exam_questions:

        question = exam_question.question


        if question.question_type in [
            "Short Answer",
            "Long Answer"
        ]:

            answer = StudentAnswer.query.filter_by(

                attempt_id=attempt.id,

                question_id=question.id

            ).first()


            if answer is None or not answer.evaluated:

                flash(
                    "Please evaluate all descriptive answers before publishing the result.",
                    "warning"
                )

                return redirect(
                    url_for(
                        "teacher.evaluate_attempt",
                        attempt_id=attempt.id
                    )
                )


    # --------------------------------------------------------
    # FINAL SCORE
    # --------------------------------------------------------

    total_score = sum(

        float(answer.marks_obtained or 0)

        for answer in attempt.answers

    )


    attempt.score = total_score


    if exam.total_marks > 0:

        attempt.percentage = (
            total_score
            / exam.total_marks
        ) * 100

    else:

        attempt.percentage = 0


    attempt.status = "Published"


    db.session.commit()


    flash(
        "Result published successfully. The student can now view it.",
        "success"
    )


    return redirect(
        url_for(
            "teacher.submissions"
        )
    )