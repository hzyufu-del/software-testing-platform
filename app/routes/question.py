"""Question routes: question list, detail, submit answer, wrong questions, records."""

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.services.question_service import (
    get_all_questions,
    get_answer_records,
    get_answer_status_map,
    get_next_question_id,
    get_question_by_id,
    get_wrong_questions,
    submit_answer,
)

question_bp = Blueprint("question", __name__)


@question_bp.get("/questions")
def question_list():
    """Display all questions."""
    questions = get_all_questions()
    status_map: dict[int, str] = {}
    if current_user.is_authenticated:
        status_map = get_answer_status_map(current_user.id)
    return render_template(
        "questions.html", questions=questions, status_map=status_map
    )


@question_bp.get("/questions/<int:question_id>")
def question_detail(question_id: int):
    """Display a single question for answering (always show form)."""
    question = get_question_by_id(question_id)
    if question is None:
        abort(404)

    # Hint: user has practiced this question before (but still show form)
    already_practiced = False
    if current_user.is_authenticated:
        from app.models import AnswerRecord

        last = (
            AnswerRecord.query
            .filter_by(user_id=current_user.id, question_id=question_id)
            .order_by(AnswerRecord.answer_time.desc())
            .first()
        )
        already_practiced = last is not None

    next_id = get_next_question_id(question_id)

    return render_template(
        "question_detail.html",
        question=question,
        result=None,
        already_practiced=already_practiced,
        next_id=next_id,
    )


@question_bp.post("/questions/<int:question_id>/submit")
@login_required
def question_submit(question_id: int):
    """Submit an answer for a question and render result."""
    question = get_question_by_id(question_id)
    if question is None:
        abort(404)

    user_answer = request.form.get("answer", "").strip().upper()
    if not user_answer:
        flash("请选择一个答案", "warning")
        return redirect(url_for("question.question_detail", question_id=question_id))

    valid_answers = {
        "single": {"A", "B", "C", "D"},
        "true_false": {"A", "B", "T", "F"},
    }.get(question.question_type, set())
    if user_answer not in valid_answers:
        flash("提交的答案不合法，请重新选择", "warning")
        return redirect(url_for("question.question_detail", question_id=question_id))

    result = submit_answer(current_user.id, question_id, user_answer)
    next_id = get_next_question_id(question_id)

    return render_template(
        "question_detail.html",
        question=question,
        result=result,
        already_practiced=True,
        next_id=next_id,
    )


@question_bp.get("/wrong-questions")
@login_required
def wrong_questions():
    """Display the current user's wrong questions."""
    wrongs = get_wrong_questions(current_user.id)
    return render_template("wrong_questions.html", wrongs=wrongs)


@question_bp.get("/answer-records")
@login_required
def answer_records():
    """Display the current user's answer records."""
    records = get_answer_records(current_user.id)
    return render_template("answer_records.html", records=records)
