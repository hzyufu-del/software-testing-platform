"""Course routes: course list, detail, chapter view, mark complete."""

from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.services.course_service import (
    get_all_courses,
    get_chapter_by_id,
    get_chapters_by_course,
    get_completed_chapter_ids,
    get_course_by_id,
    get_course_progress,
    mark_chapter_completed,
)

course_bp = Blueprint("course", __name__)


@course_bp.get("/courses")
def course_list():
    """Display all courses."""
    courses = get_all_courses()
    progress_map: dict[int, tuple[int, int]] = {}
    for c in courses:
        if current_user.is_authenticated:
            progress_map[c.id] = get_course_progress(current_user.id, c.id)
        else:
            progress_map[c.id] = (0, c.chapters.count())
    return render_template("courses.html", courses=courses, progress_map=progress_map)


@course_bp.get("/courses/<int:course_id>")
def course_detail(course_id: int):
    """Display a course and its chapter list."""
    course = get_course_by_id(course_id)
    if course is None:
        abort(404)

    chapters = get_chapters_by_course(course_id)
    completed_ids: set[int] = set()
    progress: tuple[int, int] = (0, len(chapters))

    if current_user.is_authenticated:
        completed_ids = get_completed_chapter_ids(current_user.id, course_id)
        progress = (len(completed_ids), len(chapters))

    return render_template(
        "course_detail.html",
        course=course,
        chapters=chapters,
        completed_ids=completed_ids,
        progress=progress,
    )


@course_bp.get("/chapters/<int:chapter_id>")
def chapter_detail(chapter_id: int):
    """Display a single chapter's content."""
    chapter = get_chapter_by_id(chapter_id)
    if chapter is None:
        abort(404)

    is_completed = False
    if current_user.is_authenticated:
        completed_ids = get_completed_chapter_ids(current_user.id, chapter.course_id)
        is_completed = chapter_id in completed_ids

    # Get sibling chapters for navigation
    siblings = get_chapters_by_course(chapter.course_id)
    current_idx = next(
        (i for i, ch in enumerate(siblings) if ch.id == chapter_id), 0
    )
    prev_ch = siblings[current_idx - 1] if current_idx > 0 else None
    next_ch = siblings[current_idx + 1] if current_idx < len(siblings) - 1 else None

    return render_template(
        "chapter_detail.html",
        chapter=chapter,
        course=chapter.course,
        is_completed=is_completed,
        prev_ch=prev_ch,
        next_ch=next_ch,
    )


@course_bp.post("/chapters/<int:chapter_id>/complete")
@login_required
def chapter_complete(chapter_id: int):
    """Mark a chapter as completed for the current user."""
    chapter = get_chapter_by_id(chapter_id)
    if chapter is None:
        abort(404)

    mark_chapter_completed(current_user.id, chapter_id)
    flash("章节已标记为完成", "success")
    return redirect(url_for("course.chapter_detail", chapter_id=chapter_id))
