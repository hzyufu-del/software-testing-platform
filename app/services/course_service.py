"""Course service: queries for courses, chapters, and learning records."""

from datetime import datetime

from app import db
from app.models import Chapter, Course, LearningRecord


# ---------- Course queries ----------


def get_all_courses() -> list[Course]:
    """Return all courses ordered by sort_order."""
    return Course.query.order_by(Course.sort_order).all()


def get_course_by_id(course_id: int) -> Course | None:
    """Return a Course by primary key, or None."""
    return db.session.get(Course, course_id)


# ---------- Chapter queries ----------


def get_chapters_by_course(course_id: int) -> list[Chapter]:
    """Return chapters for a course, ordered by sort_order."""
    return (
        Chapter.query
        .filter_by(course_id=course_id)
        .order_by(Chapter.sort_order)
        .all()
    )


def get_chapter_by_id(chapter_id: int) -> Chapter | None:
    """Return a Chapter by primary key, or None."""
    return db.session.get(Chapter, chapter_id)


# ---------- Learning record queries ----------


def get_completed_chapter_ids(user_id: int, course_id: int) -> set[int]:
    """Return the set of chapter IDs a user has completed in a course."""
    records = (
        db.session.query(LearningRecord.chapter_id)
        .join(Chapter, Chapter.id == LearningRecord.chapter_id)
        .filter(
            LearningRecord.user_id == user_id,
            Chapter.course_id == course_id,
            LearningRecord.is_completed.is_(True),
        )
        .all()
    )
    return {r[0] for r in records}


def get_course_progress(user_id: int, course_id: int) -> tuple[int, int]:
    """Return (completed_count, total_count) for a user in a course."""
    total = Chapter.query.filter_by(course_id=course_id).count()
    if total == 0:
        return 0, 0
    completed = len(get_completed_chapter_ids(user_id, course_id))
    return completed, total


def mark_chapter_completed(user_id: int, chapter_id: int) -> bool:
    """Mark a chapter as completed for a user. Returns True if newly completed."""
    record = LearningRecord.query.filter_by(
        user_id=user_id, chapter_id=chapter_id
    ).first()

    if record is None:
        record = LearningRecord(
            user_id=user_id,
            chapter_id=chapter_id,
            is_completed=True,
            complete_time=datetime.now(),
        )
        db.session.add(record)
        db.session.commit()
        return True

    if record.is_completed:
        return False

    record.is_completed = True
    record.complete_time = datetime.now()
    db.session.commit()
    return True
