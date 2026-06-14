"""Tests for course routes."""

import re

import pytest

from app import create_app, db as _db
from app.models import Chapter, Course, User


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def get_csrf_token(client, path: str) -> str:
    response = client.get(path)
    match = re.search(
        r'name="csrf_token" value="([^"]+)"',
        response.get_data(as_text=True),
    )
    assert match is not None
    return match.group(1)


def login(client, username: str = "testuser", password: str = "password123"):
    return client.post(
        "/login",
        data={
            "username": username,
            "password": password,
            "csrf_token": get_csrf_token(client, "/login"),
        },
    )


@pytest.fixture()
def sample_user(app):
    with app.app_context():
        user = User(username="testuser", role="student")
        user.set_password("password123")
        _db.session.add(user)
        _db.session.commit()
        user_id = user.id
    return user_id


@pytest.fixture()
def sample_course(app):
    """Create a sample course with two chapters."""
    with app.app_context():
        course = Course(title="测试课程", description="课程简介", sort_order=1)
        _db.session.add(course)
        _db.session.flush()

        ch1 = Chapter(
            course_id=course.id, title="第一章", content="<p>内容一</p>", sort_order=1
        )
        ch2 = Chapter(
            course_id=course.id, title="第二章", content="<p>内容二</p>", sort_order=2
        )
        _db.session.add_all([ch1, ch2])
        _db.session.commit()
        return course.id, ch1.id, ch2.id


# ---------- Course list ----------


def test_course_list_page(client, sample_course):
    resp = client.get("/courses")
    assert resp.status_code == 200
    assert "课程学习" in resp.get_data(as_text=True)
    assert "测试课程" in resp.get_data(as_text=True)


def test_course_list_shows_real_chapter_count_for_anonymous(client, sample_course):
    resp = client.get("/courses")
    html = resp.get_data(as_text=True)

    assert "共 2 章" in html
    assert "course-progress-bar-wrap" not in html


def test_course_list_empty(client):
    resp = client.get("/courses")
    assert resp.status_code == 200
    assert "暂无课程数据" in resp.get_data(as_text=True)


# ---------- Course detail ----------


def test_course_detail(client, sample_course):
    course_id, ch1_id, ch2_id = sample_course
    resp = client.get(f"/courses/{course_id}")
    assert resp.status_code == 200
    assert "测试课程" in resp.get_data(as_text=True)
    assert "第一章" in resp.get_data(as_text=True)
    assert "第二章" in resp.get_data(as_text=True)


def test_course_detail_404(client):
    resp = client.get("/courses/999")
    assert resp.status_code == 404


def test_course_detail_shows_progress_for_logged_in_user(client, sample_course, sample_user):
    course_id, ch1_id, ch2_id = sample_course
    login(client)
    resp = client.get(f"/courses/{course_id}")
    assert resp.status_code == 200
    assert "0/2" in resp.get_data(as_text=True)


# ---------- Chapter detail ----------


def test_chapter_detail(client, sample_course):
    course_id, ch1_id, ch2_id = sample_course
    resp = client.get(f"/chapters/{ch1_id}")
    assert resp.status_code == 200
    assert "第一章" in resp.get_data(as_text=True)
    assert "内容一" in resp.get_data(as_text=True)


def test_chapter_detail_404(client):
    resp = client.get("/chapters/999")
    assert resp.status_code == 404


def test_chapter_detail_shows_login_prompt_for_anonymous(client, sample_course):
    course_id, ch1_id, ch2_id = sample_course
    resp = client.get(f"/chapters/{ch1_id}")
    assert resp.status_code == 200
    assert "登录后标记完成" in resp.get_data(as_text=True)


def test_chapter_detail_shows_complete_button_for_logged_in(client, sample_course, sample_user):
    course_id, ch1_id, ch2_id = sample_course
    login(client)
    resp = client.get(f"/chapters/{ch1_id}")
    assert resp.status_code == 200
    assert "标记为已完成" in resp.get_data(as_text=True)


def test_chapter_detail_navigation(client, sample_course):
    course_id, ch1_id, ch2_id = sample_course
    # First chapter: has next, no prev
    resp = client.get(f"/chapters/{ch1_id}")
    html = resp.get_data(as_text=True)
    assert "第二章" in html  # next link

    # Second chapter: has prev, no next
    resp = client.get(f"/chapters/{ch2_id}")
    html = resp.get_data(as_text=True)
    assert "第一章" in html  # prev link


# ---------- Mark complete ----------


def test_mark_complete_requires_login(client, sample_course):
    course_id, ch1_id, ch2_id = sample_course
    # Without CSRF token, the request is rejected before the login check
    resp = client.post(f"/chapters/{ch1_id}/complete")
    assert resp.status_code == 400


def test_mark_complete_success(client, sample_course, sample_user):
    course_id, ch1_id, ch2_id = sample_course
    login(client)
    resp = client.post(
        f"/chapters/{ch1_id}/complete",
        data={"csrf_token": get_csrf_token(client, f"/chapters/{ch1_id}")},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert "章节已标记为完成" in resp.get_data(as_text=True)
    assert "本章已完成" in resp.get_data(as_text=True)


def test_mark_complete_then_course_detail_shows_progress(client, sample_course, sample_user):
    course_id, ch1_id, ch2_id = sample_course
    login(client)
    # Complete chapter 1
    client.post(
        f"/chapters/{ch1_id}/complete",
        data={"csrf_token": get_csrf_token(client, f"/chapters/{ch1_id}")},
    )
    # Check course detail shows 1/2
    resp = client.get(f"/courses/{course_id}")
    html = resp.get_data(as_text=True)
    assert "1/2" in html
    assert "已完成" in html


def test_mark_complete_idempotent(client, sample_course, sample_user):
    """Marking the same chapter complete twice should not error."""
    course_id, ch1_id, ch2_id = sample_course
    login(client)
    token = get_csrf_token(client, f"/chapters/{ch1_id}")
    resp1 = client.post(
        f"/chapters/{ch1_id}/complete",
        data={"csrf_token": token},
        follow_redirects=True,
    )
    assert resp1.status_code == 200
    # Second time
    token2 = get_csrf_token(client, f"/chapters/{ch1_id}")
    resp2 = client.post(
        f"/chapters/{ch1_id}/complete",
        data={"csrf_token": token2},
        follow_redirects=True,
    )
    assert resp2.status_code == 200
    assert "本章已完成" in resp2.get_data(as_text=True)


def test_mark_complete_404(client, sample_user):
    login(client)
    resp = client.post(
        "/chapters/999/complete",
        data={"csrf_token": get_csrf_token(client, "/courses")},
    )
    assert resp.status_code == 404
