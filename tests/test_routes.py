import pytest

from app import create_app


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


@pytest.fixture()
def client():
    app = create_app(TestConfig)
    return app.test_client()


def test_index(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "软件测试学习与接口测试实训平台" in response.get_data(as_text=True)


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_db_check(client):
    response = client.get("/db-check")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "ok",
        "database": "connected",
        "result": 1,
    }

