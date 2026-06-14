"""Tests for question routes."""

import re

import pytest

from app import create_app, db as _db
from app.models import AnswerRecord, Question, User, WrongQuestion


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
def sample_questions(app):
    """Create sample questions."""
    with app.app_context():
        q1 = Question(
            question_type="single",
            title="什么是软件测试？",
            option_a="编写代码",
            option_b="发现缺陷",
            option_c="部署软件",
            option_d="设计界面",
            correct_answer="B",
            explanation="测试是发现缺陷的过程。",
            difficulty="easy",
        )
        q2 = Question(
            question_type="true_false",
            title="穷尽测试是可行的。",
            option_a="正确",
            option_b="错误",
            option_c="",
            option_d="",
            correct_answer="B",
            explanation="穷尽测试是不可能的。",
            difficulty="easy",
        )
        _db.session.add_all([q1, q2])
        _db.session.commit()
        return q1.id, q2.id


# ---------- Question list ----------


def test_question_list_page(client, sample_questions):
    resp = client.get("/questions")
    assert resp.status_code == 200
    assert "题库练习" in resp.get_data(as_text=True)
    assert "什么是软件测试" in resp.get_data(as_text=True)


def test_question_list_empty(client):
    resp = client.get("/questions")
    assert resp.status_code == 200
    assert "暂无题目数据" in resp.get_data(as_text=True)


def test_question_list_shows_status_for_logged_in(client, sample_questions, sample_user):
    q1_id, q2_id = sample_questions
    login(client)
    # Answer q1 correctly
    client.post(
        f"/questions/{q1_id}/submit",
        data={"answer": "B", "csrf_token": get_csrf_token(client, f"/questions/{q1_id}")},
    )
    # Answer q2 incorrectly
    client.post(
        f"/questions/{q2_id}/submit",
        data={"answer": "A", "csrf_token": get_csrf_token(client, f"/questions/{q2_id}")},
    )
    resp = client.get("/questions")
    html = resp.get_data(as_text=True)
    assert "最近答对" in html
    assert "最近答错" in html


# ---------- Question detail ----------


def test_question_detail(client, sample_questions):
    q1_id, q2_id = sample_questions
    resp = client.get(f"/questions/{q1_id}")
    assert resp.status_code == 200
    assert "什么是软件测试" in resp.get_data(as_text=True)
    assert "发现缺陷" in resp.get_data(as_text=True)


def test_question_detail_404(client):
    resp = client.get("/questions/999")
    assert resp.status_code == 404


def test_question_detail_shows_login_prompt_for_anonymous(client, sample_questions):
    q1_id, q2_id = sample_questions
    resp = client.get(f"/questions/{q1_id}")
    assert resp.status_code == 200
    assert "登录后提交答案" in resp.get_data(as_text=True)


def test_question_detail_shows_submit_for_logged_in(client, sample_questions, sample_user):
    q1_id, q2_id = sample_questions
    login(client)
    resp = client.get(f"/questions/{q1_id}")
    assert resp.status_code == 200
    assert "提交答案" in resp.get_data(as_text=True)


def test_question_detail_shows_form_even_after_answering(client, sample_questions, sample_user):
    """After answering, GET should still show the form (not the result)."""
    q1_id, q2_id = sample_questions
    login(client)
    # Submit an answer first
    client.post(
        f"/questions/{q1_id}/submit",
        data={"answer": "B", "csrf_token": get_csrf_token(client, f"/questions/{q1_id}")},
    )
    # GET again should show form, not result
    resp = client.get(f"/questions/{q1_id}")
    html = resp.get_data(as_text=True)
    assert "提交答案" in html
    assert "你之前已练习过本题" in html
    # Should NOT show result
    assert "回答正确" not in html
    assert "回答错误" not in html


def test_question_detail_retry_shows_form(client, sample_questions, sample_user):
    """?retry=1 should show the form."""
    q1_id, q2_id = sample_questions
    login(client)
    # Submit first
    client.post(
        f"/questions/{q1_id}/submit",
        data={"answer": "B", "csrf_token": get_csrf_token(client, f"/questions/{q1_id}")},
    )
    # GET with retry=1
    resp = client.get(f"/questions/{q1_id}?retry=1")
    html = resp.get_data(as_text=True)
    assert "提交答案" in html
    assert "回答正确" not in html


# ---------- Submit answer ----------


def test_submit_requires_login(client, sample_questions):
    q1_id, q2_id = sample_questions
    resp = client.post(f"/questions/{q1_id}/submit")
    assert resp.status_code == 400  # CSRF rejects before login check


def test_submit_correct_answer(client, sample_questions, sample_user):
    q1_id, q2_id = sample_questions
    login(client)
    resp = client.post(
        f"/questions/{q1_id}/submit",
        data={"answer": "B", "csrf_token": get_csrf_token(client, f"/questions/{q1_id}")},
    )
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "回答正确" in html
    # Should show action buttons
    assert "下一题" in html
    assert "重新练习" in html
    assert "返回题库" in html


def test_submit_wrong_answer(client, sample_questions, sample_user):
    q1_id, q2_id = sample_questions
    login(client)
    resp = client.post(
        f"/questions/{q1_id}/submit",
        data={"answer": "A", "csrf_token": get_csrf_token(client, f"/questions/{q1_id}")},
    )
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "回答错误" in html
    assert "你的答案：A" in html
    assert "B" in html  # shows correct answer
    # Should show wrong-question-specific button
    assert "查看错题本" in html


def test_submit_shows_explanation_after_wrong(client, sample_questions, sample_user):
    q1_id, q2_id = sample_questions
    login(client)
    resp = client.post(
        f"/questions/{q1_id}/submit",
        data={"answer": "A", "csrf_token": get_csrf_token(client, f"/questions/{q1_id}")},
    )
    assert resp.status_code == 200
    assert "答案解析" in resp.get_data(as_text=True)
    assert "测试是发现缺陷的过程" in resp.get_data(as_text=True)


def test_submit_last_question_shows_disabled_next(client, sample_questions, sample_user):
    """Last question should show '已是最后一题' instead of next link."""
    q1_id, q2_id = sample_questions
    login(client)
    resp = client.post(
        f"/questions/{q2_id}/submit",
        data={"answer": "B", "csrf_token": get_csrf_token(client, f"/questions/{q2_id}")},
    )
    assert resp.status_code == 200
    assert "已是最后一题" in resp.get_data(as_text=True)


def test_submit_empty_answer(client, sample_questions, sample_user):
    q1_id, q2_id = sample_questions
    login(client)
    resp = client.post(
        f"/questions/{q1_id}/submit",
        data={"answer": "", "csrf_token": get_csrf_token(client, f"/questions/{q1_id}")},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert "请选择一个答案" in resp.get_data(as_text=True)
    with client.application.app_context():
        assert AnswerRecord.query.count() == 0


def test_submit_invalid_answer_does_not_write_records(
    client, sample_questions, sample_user
):
    q1_id, q2_id = sample_questions
    login(client)

    resp = client.post(
        f"/questions/{q1_id}/submit",
        data={"answer": " Z ", "csrf_token": get_csrf_token(client, f"/questions/{q1_id}")},
        follow_redirects=True,
    )

    assert resp.status_code == 200
    assert "提交的答案不合法，请重新选择" in resp.get_data(as_text=True)
    with client.application.app_context():
        assert AnswerRecord.query.count() == 0
        assert WrongQuestion.query.count() == 0


def test_submit_invalid_answer_does_not_increment_wrong_count(
    client, sample_questions, sample_user
):
    q1_id, q2_id = sample_questions
    login(client)
    client.post(
        f"/questions/{q1_id}/submit",
        data={"answer": "A", "csrf_token": get_csrf_token(client, f"/questions/{q1_id}")},
    )

    client.post(
        f"/questions/{q1_id}/submit",
        data={"answer": "Z", "csrf_token": get_csrf_token(client, f"/questions/{q1_id}")},
    )

    with client.application.app_context():
        wrong = WrongQuestion.query.filter_by(
            user_id=sample_user, question_id=q1_id
        ).one()
        assert wrong.wrong_count == 1
        assert AnswerRecord.query.filter_by(
            user_id=sample_user, question_id=q1_id
        ).count() == 1


def test_submit_true_false_accepts_tf_alias(client, sample_questions, sample_user):
    q1_id, q2_id = sample_questions
    login(client)

    resp = client.post(
        f"/questions/{q2_id}/submit",
        data={"answer": " f ", "csrf_token": get_csrf_token(client, f"/questions/{q2_id}")},
    )

    assert resp.status_code == 200
    assert "回答正确" in resp.get_data(as_text=True)
    with client.application.app_context():
        record = AnswerRecord.query.filter_by(
            user_id=sample_user, question_id=q2_id
        ).one()
        assert record.user_answer == "F"
        assert record.is_correct is True


def test_submit_404(client, sample_user):
    login(client)
    resp = client.post(
        "/questions/999/submit",
        data={"answer": "A", "csrf_token": get_csrf_token(client, "/questions")},
    )
    assert resp.status_code == 404


# ---------- Wrong questions ----------


def test_wrong_questions_requires_login(client):
    resp = client.get("/wrong-questions", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_wrong_questions_after_wrong_answer(client, sample_questions, sample_user):
    q1_id, q2_id = sample_questions
    login(client)
    client.post(
        f"/questions/{q1_id}/submit",
        data={"answer": "A", "csrf_token": get_csrf_token(client, f"/questions/{q1_id}")},
    )
    resp = client.get("/wrong-questions")
    assert resp.status_code == 200
    assert "什么是软件测试" in resp.get_data(as_text=True)
    assert "1次" in resp.get_data(as_text=True)


def test_wrong_questions_retry_link(client, sample_questions, sample_user):
    """Wrong questions page should have retry link with ?retry=1."""
    q1_id, q2_id = sample_questions
    login(client)
    client.post(
        f"/questions/{q1_id}/submit",
        data={"answer": "A", "csrf_token": get_csrf_token(client, f"/questions/{q1_id}")},
    )
    resp = client.get("/wrong-questions")
    html = resp.get_data(as_text=True)
    assert f"/questions/{q1_id}?retry=1" in html


def test_wrong_questions_empty(client, sample_user):
    login(client)
    resp = client.get("/wrong-questions")
    assert resp.status_code == 200
    assert "暂无错题" in resp.get_data(as_text=True)


def test_wrong_count_increments(client, sample_questions, sample_user):
    """Same question answered wrong twice should increment wrong_count."""
    q1_id, q2_id = sample_questions
    login(client)
    # Wrong answer twice
    client.post(
        f"/questions/{q1_id}/submit",
        data={"answer": "A", "csrf_token": get_csrf_token(client, f"/questions/{q1_id}")},
    )
    # Need to GET first to get a fresh CSRF token for the second submission
    client.post(
        f"/questions/{q1_id}/submit",
        data={"answer": "A", "csrf_token": get_csrf_token(client, f"/questions/{q1_id}")},
    )
    resp = client.get("/wrong-questions")
    assert resp.status_code == 200
    assert "2次" in resp.get_data(as_text=True)


# ---------- Answer records ----------


def test_answer_records_requires_login(client):
    resp = client.get("/answer-records", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_answer_records_after_submit(client, sample_questions, sample_user):
    q1_id, q2_id = sample_questions
    login(client)
    client.post(
        f"/questions/{q1_id}/submit",
        data={"answer": "B", "csrf_token": get_csrf_token(client, f"/questions/{q1_id}")},
    )
    resp = client.get("/answer-records")
    assert resp.status_code == 200
    assert "什么是软件测试" in resp.get_data(as_text=True)
    assert "B" in resp.get_data(as_text=True)


def test_answer_records_empty(client, sample_user):
    login(client)
    resp = client.get("/answer-records")
    assert resp.status_code == 200
    assert "暂无答题记录" in resp.get_data(as_text=True)
