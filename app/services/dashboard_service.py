"""Lightweight dashboard statistics service.

All functions are read-only and query existing models only.
"""

from app import db
from app.models import (
    AnswerRecord,
    ApiTestResult,
    Chapter,
    LearningRecord,
    WrongQuestion,
)


def get_user_stats(user_id: int) -> dict:
    """Return learning / quiz / training statistics for a single user."""

    # ---- Course learning ----
    total_chapters = db.session.query(Chapter).count()
    completed_chapters = (
        db.session.query(LearningRecord)
        .filter_by(user_id=user_id, is_completed=True)
        .count()
    )
    course_progress = (
        round(completed_chapters / total_chapters * 100, 1)
        if total_chapters > 0
        else 0
    )

    # ---- Quiz ----
    total_answers = (
        db.session.query(AnswerRecord).filter_by(user_id=user_id).count()
    )
    correct_answers = (
        db.session.query(AnswerRecord)
        .filter_by(user_id=user_id, is_correct=True)
        .count()
    )
    wrong_count = (
        db.session.query(WrongQuestion).filter_by(user_id=user_id).count()
    )
    accuracy = (
        round(correct_answers / total_answers * 100, 1)
        if total_answers > 0
        else 0
    )

    # ---- API training ----
    total_tests = (
        db.session.query(ApiTestResult).filter_by(user_id=user_id).count()
    )
    passed_tests = (
        db.session.query(ApiTestResult)
        .filter_by(user_id=user_id, is_passed=True)
        .count()
    )
    pass_rate = (
        round(passed_tests / total_tests * 100, 1) if total_tests > 0 else 0
    )

    return {
        "completed_chapters": completed_chapters,
        "total_chapters": total_chapters,
        "course_progress": course_progress,
        "total_answers": total_answers,
        "correct_answers": correct_answers,
        "wrong_count": wrong_count,
        "accuracy": accuracy,
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "pass_rate": pass_rate,
    }
