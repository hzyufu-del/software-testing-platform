"""Question service: queries for questions, answer records, and wrong questions."""

from datetime import datetime

from app import db
from app.models import AnswerRecord, Question, WrongQuestion


# ---------- Question queries ----------


def get_all_questions() -> list[Question]:
    """Return all questions ordered by id."""
    return Question.query.order_by(Question.id).all()


def get_question_by_id(question_id: int) -> Question | None:
    """Return a Question by primary key, or None."""
    return db.session.get(Question, question_id)


# ---------- Answer submission ----------


def submit_answer(user_id: int, question_id: int, user_answer: str) -> dict:
    """Submit an answer and return the result dict.

    Returns:
        dict with keys: user_answer, is_correct, correct_answer, explanation,
        record_id
    """
    question = get_question_by_id(question_id)
    if question is None:
        raise ValueError("题目不存在")

    normalized_answer = user_answer.strip().upper()
    normalized_correct_answer = question.correct_answer.strip().upper()
    comparison_answer = normalized_answer
    if question.question_type == "true_false":
        if normalized_correct_answer in {"A", "B"}:
            comparison_answer = {"T": "A", "F": "B"}.get(
                normalized_answer, normalized_answer
            )
        elif normalized_correct_answer in {"T", "F"}:
            comparison_answer = {"A": "T", "B": "F"}.get(
                normalized_answer, normalized_answer
            )

    is_correct = comparison_answer == normalized_correct_answer

    record = AnswerRecord(
        user_id=user_id,
        question_id=question_id,
        user_answer=normalized_answer,
        is_correct=is_correct,
        answer_time=datetime.now(),
    )
    db.session.add(record)

    # Update wrong question tracking
    if not is_correct:
        _update_wrong_question(user_id, question_id)

    db.session.commit()

    return {
        "user_answer": normalized_answer,
        "is_correct": is_correct,
        "correct_answer": question.correct_answer,
        "explanation": question.explanation,
        "record_id": record.id,
    }


def _update_wrong_question(user_id: int, question_id: int) -> None:
    """Create or update a WrongQuestion entry."""
    wrong = WrongQuestion.query.filter_by(
        user_id=user_id, question_id=question_id
    ).first()

    if wrong is None:
        wrong = WrongQuestion(
            user_id=user_id,
            question_id=question_id,
            wrong_count=1,
            last_wrong_time=datetime.now(),
        )
        db.session.add(wrong)
    else:
        wrong.wrong_count += 1
        wrong.last_wrong_time = datetime.now()


# ---------- Wrong questions ----------


def get_wrong_questions(user_id: int) -> list[WrongQuestion]:
    """Return all wrong questions for a user, newest first."""
    return (
        WrongQuestion.query
        .filter_by(user_id=user_id)
        .order_by(WrongQuestion.last_wrong_time.desc())
        .all()
    )


# ---------- Answer records ----------


def get_answer_records(user_id: int) -> list[AnswerRecord]:
    """Return all answer records for a user, newest first."""
    return (
        AnswerRecord.query
        .filter_by(user_id=user_id)
        .order_by(AnswerRecord.answer_time.desc())
        .all()
    )


# ---------- Navigation helpers ----------


def get_next_question_id(current_id: int) -> int | None:
    """Return the next question's id after current_id, or None if last."""
    next_q = (
        Question.query
        .filter(Question.id > current_id)
        .order_by(Question.id)
        .first()
    )
    return next_q.id if next_q else None


def get_answer_status_map(user_id: int) -> dict[int, str]:
    """Return {question_id: 'correct'|'wrong'} for a user's latest answers."""
    records = (
        AnswerRecord.query
        .filter_by(user_id=user_id)
        .order_by(AnswerRecord.answer_time.desc())
        .all()
    )
    status_map: dict[int, str] = {}
    for r in records:
        if r.question_id not in status_map:
            status_map[r.question_id] = "correct" if r.is_correct else "wrong"
    return status_map
