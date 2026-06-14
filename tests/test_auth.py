"""Tests for authentication routes."""

import re

import pytest

from app import create_app, db as _db
from app.models import User


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
    """Create and return a sample user committed to the test DB."""
    with app.app_context():
        user = User(username="testuser", role="student")
        user.set_password("password123")
        _db.session.add(user)
        _db.session.commit()
        user_id = user.id
    return user_id


# ---------- Registration ----------


def test_register_page(client):
    resp = client.get("/register")
    assert resp.status_code == 200
    assert "用户注册" in resp.get_data(as_text=True)
    assert 'name="csrf_token"' in resp.get_data(as_text=True)


def test_register_success(client):
    resp = client.post(
        "/register",
        data={
            "username": "alice",
            "password": "secret1",
            "confirm": "secret1",
            "csrf_token": get_csrf_token(client, "/register"),
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert "注册成功" in resp.get_data(as_text=True)


def test_register_duplicate_username(client, sample_user):
    resp = client.post(
        "/register",
        data={
            "username": "testuser",
            "password": "secret1",
            "confirm": "secret1",
            "csrf_token": get_csrf_token(client, "/register"),
        },
    )
    assert "用户名已存在" in resp.get_data(as_text=True)


def test_register_password_mismatch(client):
    resp = client.post(
        "/register",
        data={
            "username": "bob",
            "password": "secret1",
            "confirm": "secret2",
            "csrf_token": get_csrf_token(client, "/register"),
        },
    )
    assert "两次输入的密码不一致" in resp.get_data(as_text=True)


def test_register_short_password(client):
    resp = client.post(
        "/register",
        data={
            "username": "bob",
            "password": "123",
            "confirm": "123",
            "csrf_token": get_csrf_token(client, "/register"),
        },
    )
    assert "密码长度不能少于6位" in resp.get_data(as_text=True)


def test_register_rejects_missing_csrf_token(client):
    resp = client.post(
        "/register",
        data={"username": "alice", "password": "secret1", "confirm": "secret1"},
    )
    assert resp.status_code == 400


# ---------- Login / Logout ----------


def test_login_page(client):
    resp = client.get("/login")
    assert resp.status_code == 200
    assert "用户登录" in resp.get_data(as_text=True)
    assert 'name="csrf_token"' in resp.get_data(as_text=True)


def test_login_success(client, sample_user):
    resp = login(client)
    resp = client.get(resp.headers["Location"], follow_redirects=True)
    assert resp.status_code == 200
    assert "登录成功" in resp.get_data(as_text=True)


def test_login_allows_internal_next(client, sample_user):
    path = "/login?next=/profile"
    resp = client.post(
        path,
        data={
            "username": "testuser",
            "password": "password123",
            "csrf_token": get_csrf_token(client, path),
        },
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/profile"


@pytest.mark.parametrize(
    "next_url",
    [
        "https://example.com/landing",
        "//example.com/landing",
        "/%2Fexample.com/landing",
        "/%5Cexample.com/landing",
    ],
)
def test_login_rejects_external_next(client, sample_user, next_url):
    path = f"/login?next={next_url}"
    resp = client.post(
        path,
        data={
            "username": "testuser",
            "password": "password123",
            "csrf_token": get_csrf_token(client, path),
        },
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/"


def test_login_wrong_password(client, sample_user):
    resp = login(client, password="wrong")
    assert "用户名或密码错误" in resp.get_data(as_text=True)


def test_login_nonexistent_user(client):
    resp = login(client, username="ghost")
    assert "用户名或密码错误" in resp.get_data(as_text=True)


def test_login_rejects_missing_csrf_token(client):
    resp = client.post(
        "/login",
        data={"username": "testuser", "password": "password123"},
    )
    assert resp.status_code == 400


def test_logout(client, sample_user):
    login(client)
    resp = client.post(
        "/logout",
        data={"csrf_token": get_csrf_token(client, "/profile")},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert "已退出登录" in resp.get_data(as_text=True)


def test_logout_get_is_not_allowed(client):
    assert client.get("/logout").status_code == 405


def test_logout_rejects_missing_csrf_token(client, sample_user):
    login(client)
    assert client.post("/logout").status_code == 400


# ---------- Profile ----------


def test_profile_requires_login(client):
    resp = client.get("/profile", follow_redirects=True)
    # Should redirect to login
    assert "用户登录" in resp.get_data(as_text=True)


def test_profile_accessible_when_logged_in(client, sample_user):
    login(client)
    resp = client.get("/profile")
    assert resp.status_code == 200
    assert "testuser" in resp.get_data(as_text=True)
    assert "个人中心" in resp.get_data(as_text=True)


# ---------- Password hashing ----------


def test_password_not_stored_in_plaintext(app, sample_user):
    with app.app_context():
        user = _db.session.get(User, sample_user)
        assert user.password_hash != "password123"
        assert user.check_password("password123")
        assert not user.check_password("wrong")
