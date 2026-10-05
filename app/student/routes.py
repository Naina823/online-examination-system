from datetime import datetime, timezone, timedelta
from functools import wraps

from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    jsonify,
    abort,
)

from flask_login import login_required, current_user

from app.student import student_bp
from app.extensions import db

from app.models.exam import Exam
from app.models.exam_question import ExamQuestion
from app.models.exam_attempt import ExamAttempt
from app.models.student_answer import StudentAnswer


# ============================================================
# STUDENT ACCESS CONTROL
# ============================================================

def student_required(view_function):

    @wraps(view_function)
    @login_required
    def wrapped(*args, **kwargs):

        if current_user.role != "student":

            flash(
                "You are not authorized to access the student panel.",
                "danger"
            )

            return redirect(
                url_for("main.home")
            )

        return view_function(*args, **kwargs)

    return wrapped


# ============================================================
# STUDENT DASHBOARD
# ============================================================

@student_bp.route("/dashboard")
@student_required
def dashboard():

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    # --------------------------------------------------------
    # PUBLISHED EXAMS
    # --------------------------------------------------------

    all_published_exams = (
        Exam.query
        .filter_by(status="Published")
        .order_by(Exam.created_at.desc())
        .all()
    )

    available_exams = []

    for exam in all_published_exams:

        # If the exam has a start time, it must have started.
        if exam.start_time and now < exam.start_time:
            continue

        # If the exam has an end time, it must not have ended.
        if exam.end_time and now > exam.end_time:
            continue

        # Exam must contain at least one question.
        question_count = (
            ExamQuestion.query
            .filter_by(exam_id=exam.id)
            .count()
        )

        if question_count == 0:
            continue

        # ----------------------------------------------------
        # Do not show an exam as available if the student has
        # already submitted it.
        # ----------------------------------------------------

        submitted_attempt = (
            ExamAttempt.query
            .filter_by(
                student_id=current_user.id,
                exam_id=exam.id
            )
            .filter(
                ExamAttempt.status.in_([
                    "Submitted",
                    "Evaluated",
                    "Published"
                ])
            )
            .first()
        )

        if submitted_attempt:
            continue

        available_exams.append(exam)


    # --------------------------------------------------------
    # IN-PROGRESS ATTEMPTS
    # --------------------------------------------------------

    in_progress_attempts = (
        ExamAttempt.query
        .filter_by(
            student_id=current_user.id,
            status="In Progress"
        )
        .order_by(
            ExamAttempt.started_at.desc()
        )
        .all()
    )


    # --------------------------------------------------------
    # COMPLETED ATTEMPTS
    # --------------------------------------------------------

    completed_attempts = (
        ExamAttempt.query
        .filter_by(
            student_id=current_user.id
        )
        .filter(
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
        "student/dashboard.html",
        available_exams=available_exams,
        in_progress_attempts=in_progress_attempts,
        completed_attempts=completed_attempts
    )


# ============================================================
# EXAM DETAILS
# ============================================================

@student_bp.route(
    "/exam/<int:exam_id>"
)
@student_required
def exam_details(exam_id):

    exam = Exam.query.get_or_404(exam_id)

    # --------------------------------------------------------
    # ONLY PUBLISHED EXAMS
    # --------------------------------------------------------

    if exam.status != "Published":

        flash(
            "This examination is not currently available.",
            "warning"
        )

        return redirect(
            url_for("student.dashboard")
        )


    # --------------------------------------------------------
    # QUESTION COUNT
    # --------------------------------------------------------

    question_count = (
        ExamQuestion.query
        .filter_by(exam_id=exam.id)
        .count()
    )


    # --------------------------------------------------------
    # CURRENT TIME
    # --------------------------------------------------------

    now = datetime.now(timezone.utc).replace(
        tzinfo=None
    )


    exam_started = True
    exam_ended = False


    if exam.start_time:

        if now < exam.start_time:

            exam_started = False


    if exam.end_time:

        if now > exam.end_time:

            exam_ended = True


    # --------------------------------------------------------
    # PREVIOUS ATTEMPT
    # --------------------------------------------------------

    previous_attempt = (
        ExamAttempt.query
        .filter_by(
            student_id=current_user.id,
            exam_id=exam.id
        )
        .order_by(
            ExamAttempt.started_at.desc()
        )
        .first()
    )


    return render_template(
        "student/exam_details.html",
        exam=exam,
        question_count=question_count,
        exam_started=exam_started,
        exam_ended=exam_ended,
        previous_attempt=previous_attempt
    )


# ============================================================
# START EXAM
# ============================================================

@student_bp.route(
    "/exam/<int:exam_id>/start",
    methods=["POST"]
)
@student_required
def start_exam(exam_id):

    exam = Exam.query.get_or_404(exam_id)


    # --------------------------------------------------------
    # EXAM MUST BE PUBLISHED
    # --------------------------------------------------------

    if exam.status != "Published":

        flash(
            "This examination is not published.",
            "danger"
        )

        return redirect(
            url_for("student.dashboard")
        )


    # --------------------------------------------------------
    # CHECK QUESTIONS
    # --------------------------------------------------------

    question_count = (
        ExamQuestion.query
        .filter_by(exam_id=exam.id)
        .count()
    )


    if question_count == 0:

        flash(
            "This examination does not contain any questions yet.",
            "danger"
        )

        return redirect(
            url_for(
                "student.exam_details",
                exam_id=exam.id
            )
        )


    # --------------------------------------------------------
    # CHECK EXAM WINDOW
    # --------------------------------------------------------

    now = datetime.now(timezone.utc).replace(
        tzinfo=None
    )


    if exam.start_time and now < exam.start_time:

        flash(
            "This examination has not started yet.",
            "warning"
        )

        return redirect(
            url_for(
                "student.exam_details",
                exam_id=exam.id
            )
        )


    if exam.end_time and now > exam.end_time:

        flash(
            "This examination has already ended.",
            "warning"
        )

        return redirect(
            url_for(
                "student.exam_details",
                exam_id=exam.id
            )
        )


    # --------------------------------------------------------
    # CHECK FOR EXISTING ATTEMPT
    # --------------------------------------------------------

    existing_attempt = (
        ExamAttempt.query
        .filter_by(
            student_id=current_user.id,
            exam_id=exam.id
        )
        .order_by(
            ExamAttempt.started_at.desc()
        )
        .first()
    )


    # --------------------------------------------------------
    # RESUME IN-PROGRESS ATTEMPT
    # --------------------------------------------------------

    if existing_attempt:

        if existing_attempt.status == "In Progress":

            return redirect(
                url_for(
                    "student.take_exam",
                    attempt_id=existing_attempt.id
                )
            )


        if existing_attempt.status in [
            "Submitted",
            "Evaluated",
            "Published"
        ]:

            flash(
                "You have already submitted this examination.",
                "warning"
            )

            return redirect(
                url_for(
                    "student.dashboard"
                )
            )


    # --------------------------------------------------------
    # CREATE NEW ATTEMPT
    # --------------------------------------------------------

    attempt = ExamAttempt(

        student_id=current_user.id,

        exam_id=exam.id,

        started_at=now,

        status="In Progress"

    )


    db.session.add(attempt)

    db.session.commit()


    return redirect(
        url_for(
            "student.take_exam",
            attempt_id=attempt.id
        )
    )


# ============================================================
# TAKE EXAM
# ============================================================

@student_bp.route(
    "/attempt/<int:attempt_id>"
)
@student_required
def take_exam(attempt_id):

    attempt = ExamAttempt.query.get_or_404(
        attempt_id
    )


    # --------------------------------------------------------
    # SECURITY
    # --------------------------------------------------------

    if attempt.student_id != current_user.id:

        abort(403)


    # --------------------------------------------------------
    # CHECK STATUS
    # --------------------------------------------------------

    if attempt.status != "In Progress":

        if attempt.status == "Published":

            return redirect(
                url_for(
                    "student.result",
                    attempt_id=attempt.id
                )
            )

        return redirect(
            url_for(
                "student.submission_success",
                attempt_id=attempt.id
            )
        )


    exam = attempt.exam


    # --------------------------------------------------------
    # GET QUESTIONS
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # SERVER-SIDE DEADLINE
    # --------------------------------------------------------

    deadline = (
        attempt.started_at
        + timedelta(minutes=exam.duration)
    )


    now = datetime.now(timezone.utc).replace(
        tzinfo=None
    )


    remaining_seconds = int(
        (deadline - now).total_seconds()
    )


    # --------------------------------------------------------
    # TIMER EXPIRED
    # --------------------------------------------------------

    if remaining_seconds <= 0:

        return redirect(
            url_for(
                "student.submit_exam",
                attempt_id=attempt.id
            )
        )


    # --------------------------------------------------------
    # EXISTING ANSWERS
    # --------------------------------------------------------

    answers = (
        StudentAnswer.query
        .filter_by(
            attempt_id=attempt.id
        )
        .all()
    )


    answers_by_question = {

        answer.question_id: answer

        for answer in answers

    }


    return render_template(
        "student/take_exam.html",
        attempt=attempt,
        exam=exam,
        exam_questions=exam_questions,
        answers_by_question=answers_by_question,
        remaining_seconds=remaining_seconds
    )


# ============================================================
# SAVE ANSWER
# ============================================================

@student_bp.route(
    "/attempt/<int:attempt_id>/save-answer",
    methods=["POST"]
)
@student_required
def save_answer(attempt_id):

    attempt = ExamAttempt.query.get_or_404(
        attempt_id
    )


    # --------------------------------------------------------
    # SECURITY
    # --------------------------------------------------------

    if attempt.student_id != current_user.id:

        return jsonify({
            "success": False,
            "message": "Unauthorized."
        }), 403


    if attempt.status != "In Progress":

        return jsonify({
            "success": False,
            "message": "This examination is no longer active."
        }), 400


    exam = attempt.exam


    # --------------------------------------------------------
    # SERVER-SIDE TIMER
    # --------------------------------------------------------

    deadline = (
        attempt.started_at
        + timedelta(minutes=exam.duration)
    )


    now = datetime.now(timezone.utc).replace(
        tzinfo=None
    )


    if now >= deadline:

        return jsonify({
            "success": False,
            "message": "The examination time has expired.",
            "expired": True
        }), 400


    # --------------------------------------------------------
    # FORM DATA
    # --------------------------------------------------------

    question_id = request.form.get(
        "question_id"
    )

    selected_answer = request.form.get(
        "selected_answer"
    )

    text_answer = request.form.get(
        "text_answer"
    )


    try:

        question_id = int(question_id)

    except (TypeError, ValueError):

        return jsonify({
            "success": False,
            "message": "Invalid question."
        }), 400


    # --------------------------------------------------------
    # VERIFY QUESTION BELONGS TO EXAM
    # --------------------------------------------------------

    exam_question = (
        ExamQuestion.query
        .filter_by(
            exam_id=exam.id,
            question_id=question_id
        )
        .first()
    )


    if not exam_question:

        return jsonify({
            "success": False,
            "message": "Question does not belong to this examination."
        }), 400


    # --------------------------------------------------------
    # FIND EXISTING ANSWER
    # --------------------------------------------------------

    answer = (
        StudentAnswer.query
        .filter_by(
            attempt_id=attempt.id,
            question_id=question_id
        )
        .first()
    )


    if answer is None:

        answer = StudentAnswer(

            attempt_id=attempt.id,

            question_id=question_id

        )

        db.session.add(answer)


    # --------------------------------------------------------
    # SAVE ANSWER
    # --------------------------------------------------------

    answer.selected_answer = (
        selected_answer
        if selected_answer
        else None
    )

    answer.text_answer = (
        text_answer
        if text_answer
        else None
    )


    db.session.commit()


    return jsonify({
        "success": True,
        "message": "Answer saved successfully."
    })


# ============================================================
# SUBMIT EXAM
# ============================================================

@student_bp.route(
    "/attempt/<int:attempt_id>/submit",
    methods=["GET", "POST"]
)
@student_required
def submit_exam(attempt_id):

    attempt = ExamAttempt.query.get_or_404(
        attempt_id
    )


    # --------------------------------------------------------
    # SECURITY
    # --------------------------------------------------------

    if attempt.student_id != current_user.id:

        abort(403)


    # --------------------------------------------------------
    # ALREADY SUBMITTED
    # --------------------------------------------------------

    if attempt.status != "In Progress":

        if attempt.status == "Published":

            return redirect(
                url_for(
                    "student.result",
                    attempt_id=attempt.id
                )
            )

        return redirect(
            url_for(
                "student.submission_success",
                attempt_id=attempt.id
            )
        )


    exam = attempt.exam


    # --------------------------------------------------------
    # GET QUESTIONS
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # GET / CREATE ANSWERS
    # --------------------------------------------------------

    existing_answers = (
        StudentAnswer.query
        .filter_by(
            attempt_id=attempt.id
        )
        .all()
    )


    answers_by_question = {

        answer.question_id: answer

        for answer in existing_answers

    }


    # --------------------------------------------------------
    # AUTOMATIC EVALUATION
    # --------------------------------------------------------

    total_score = 0


    for exam_question in exam_questions:

        question = exam_question.question

        answer = answers_by_question.get(
            question.id
        )


        # ----------------------------------------------------
        # CREATE EMPTY ANSWER FOR UNANSWERED QUESTION
        # ----------------------------------------------------

        if answer is None:

            answer = StudentAnswer(

                attempt_id=attempt.id,

                question_id=question.id,

                selected_answer=None,

                text_answer=None,

                is_correct=False,

                marks_obtained=0,

                evaluated=(
                    question.question_type
                    in [
                        "MCQ",
                        "True/False"
                    ]
                )

            )

            db.session.add(answer)

            answers_by_question[
                question.id
            ] = answer


        # ----------------------------------------------------
        # MCQ
        # ----------------------------------------------------

        if question.question_type == "MCQ":

            selected = (
                answer.selected_answer
                or ""
            ).strip()

            correct = (
                question.correct_answer
                or ""
            ).strip()


            if selected and selected == correct:

                answer.is_correct = True

                answer.marks_obtained = (
                    question.marks
                )

            else:

                answer.is_correct = False

                answer.marks_obtained = 0


            answer.evaluated = True


        # ----------------------------------------------------
        # TRUE / FALSE
        # ----------------------------------------------------

        elif question.question_type == "True/False":

            selected = (
                answer.selected_answer
                or ""
            ).strip()

            correct = (
                question.correct_answer
                or ""
            ).strip()


            if selected and selected == correct:

                answer.is_correct = True

                answer.marks_obtained = (
                    question.marks
                )

            else:

                answer.is_correct = False

                answer.marks_obtained = 0


            answer.evaluated = True


        # ----------------------------------------------------
        # SHORT / LONG ANSWER
        # ----------------------------------------------------

        else:

            # Teacher will evaluate this later.

            answer.is_correct = False

            answer.marks_obtained = 0

            answer.evaluated = False


        total_score += float(
            answer.marks_obtained or 0
        )


    # --------------------------------------------------------
    # SAVE SCORE
    # --------------------------------------------------------

    attempt.score = total_score


    if exam.total_marks > 0:

        attempt.percentage = (
            total_score
            / exam.total_marks
        ) * 100

    else:

        attempt.percentage = 0


    # --------------------------------------------------------
    # SUBMISSION STATUS
    # --------------------------------------------------------

    attempt.submitted_at = (
        datetime.now(timezone.utc)
        .replace(tzinfo=None)
    )

    attempt.status = "Submitted"


    db.session.commit()


    return redirect(
        url_for(
            "student.submission_success",
            attempt_id=attempt.id
        )
    )


# ============================================================
# SUBMISSION SUCCESS
# ============================================================

@student_bp.route(
    "/attempt/<int:attempt_id>/submitted"
)
@student_required
def submission_success(attempt_id):

    attempt = ExamAttempt.query.get_or_404(
        attempt_id
    )


    if attempt.student_id != current_user.id:

        abort(403)


    return render_template(
        "student/submission_success.html",
        attempt=attempt,
        exam=attempt.exam
    )


# ============================================================
# STUDENT RESULT
# ============================================================

@student_bp.route(
    "/result/<int:attempt_id>"
)
@student_required
def result(attempt_id):

    attempt = ExamAttempt.query.get_or_404(
        attempt_id
    )


    # --------------------------------------------------------
    # SECURITY
    # --------------------------------------------------------

    if attempt.student_id != current_user.id:

        abort(403)


    # --------------------------------------------------------
    # RESULT MUST BE PUBLISHED
    # --------------------------------------------------------

    if attempt.status != "Published":

        flash(
            "The result has not been published by the teacher yet.",
            "warning"
        )

        return redirect(
            url_for(
                "student.dashboard"
            )
        )


    exam = attempt.exam


    # --------------------------------------------------------
    # EXAM QUESTIONS
    # --------------------------------------------------------

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


    answers = (
        StudentAnswer.query
        .filter_by(
            attempt_id=attempt.id
        )
        .all()
    )


    answers_by_question = {

        answer.question_id: answer

        for answer in answers

    }


    # --------------------------------------------------------
    # STATISTICS
    # --------------------------------------------------------

    correct_count = 0

    incorrect_count = 0

    unanswered_count = 0


    for exam_question in exam_questions:

        question = exam_question.question

        answer = answers_by_question.get(
            question.id
        )


        if answer is None:

            unanswered_count += 1

            continue


        if question.question_type in [
            "MCQ",
            "True/False"
        ]:

            if answer.is_correct:

                correct_count += 1

            elif answer.selected_answer:

                incorrect_count += 1

            else:

                unanswered_count += 1


        else:

            if not answer.text_answer:

                unanswered_count += 1


    # --------------------------------------------------------
    # PASS / FAIL
    # --------------------------------------------------------

    percentage = (
        attempt.percentage
        if attempt.percentage is not None
        else 0
    )


    passing_percentage = (
        exam.passing_percentage
        if exam.passing_percentage is not None
        else 40
    )


    passed = (
        percentage >= passing_percentage
    )


    return render_template(

        "student/result.html",

        attempt=attempt,

        exam=exam,

        exam_questions=exam_questions,

        answers_by_question=answers_by_question,

        correct_count=correct_count,

        incorrect_count=incorrect_count,

        unanswered_count=unanswered_count,

        passed=passed

    )