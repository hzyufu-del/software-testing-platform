"""Tests for training routes."""

import json
import re
from unittest.mock import MagicMock, patch

import pytest

from app import create_app, db as _db
from app.models import ApiTestCase, ApiTestResult, TrainingTask, User


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
def sample_task(app):
    """Create a sample training task."""
    with app.app_context():
        task = TrainingTask(
            title="登录接口测试",
            description="测试模拟登录接口",
            method="POST",
            endpoint="/mock/login",
            request_example='{"username": "admin", "password": "123456"}',
            expected_example='{"code": 200, "message": "登录成功"}',
            sort_order=1,
        )
        _db.session.add(task)
        _db.session.commit()
        task_id = task.id
    return task_id


# ---------- Task list ----------


def test_task_list_page(client, sample_task):
    resp = client.get("/training")
    assert resp.status_code == 200
    assert "接口实训" in resp.get_data(as_text=True)
    assert "登录接口测试" in resp.get_data(as_text=True)


def test_task_list_empty(client):
    resp = client.get("/training")
    assert resp.status_code == 200
    assert "暂无实训任务数据" in resp.get_data(as_text=True)


# ---------- Task detail ----------


def test_task_detail(client, sample_task):
    resp = client.get(f"/training/{sample_task}")
    assert resp.status_code == 200
    assert "登录接口测试" in resp.get_data(as_text=True)
    assert "/mock/login" in resp.get_data(as_text=True)
    assert "填写测试用例" in resp.get_data(as_text=True)


def test_task_detail_404(client):
    resp = client.get("/training/999")
    assert resp.status_code == 404


def test_task_detail_shows_form(client, sample_task):
    resp = client.get(f"/training/{sample_task}")
    html = resp.get_data(as_text=True)
    assert "用例名称" in html
    assert "请求地址" in html
    assert "预期状态码" in html
    assert "执行测试" in html


# ---------- Execute test ----------


def test_run_requires_login(client, sample_task):
    resp = client.post(f"/training/{sample_task}/run")
    assert resp.status_code == 400  # CSRF rejects before login check


def _mock_response(status_code=200, json_data=None, elapsed=0.05):
    """Create a mock requests.Response."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.text = json.dumps(json_data or {})
    resp.elapsed.total_seconds.return_value = elapsed
    return resp


@patch("app.services.training_service.http_requests.post")
def test_run_mock_login_success(mock_post, client, sample_task, sample_user):
    mock_post.return_value = _mock_response(200, {"code": 200, "message": "登录成功", "token": "abc"})

    login(client)
    resp = client.post(
        f"/training/{sample_task}/run",
        data={
            "case_name": "登录成功测试",
            "method": "POST",
            "url": "/mock/login",
            "headers": '{"Content-Type": "application/json"}',
            "params": '{"username": "admin", "password": "123456"}',
            "expected_status_code": "200",
            "expected_field": "message",
            "expected_value": "登录成功",
            "max_response_time": "3000",
            "csrf_token": get_csrf_token(client, f"/training/{sample_task}"),
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "测试通过" in html


@patch("app.services.training_service.http_requests.post")
def test_run_status_assertion(mock_post, client, sample_task, sample_user):
    mock_post.return_value = _mock_response(200, {"code": 200, "message": "登录成功"})

    login(client)
    resp = client.post(
        f"/training/{sample_task}/run",
        data={
            "case_name": "状态码断言测试",
            "method": "POST",
            "url": "/mock/login",
            "headers": "{}",
            "params": '{"username": "admin", "password": "123456"}',
            "expected_status_code": "201",
            "expected_field": "",
            "expected_value": "",
            "max_response_time": "",
            "csrf_token": get_csrf_token(client, f"/training/{sample_task}"),
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "测试未通过" in html
    assert "状态码断言" in html


@patch("app.services.training_service.http_requests.post")
def test_run_field_assertion(mock_post, client, sample_task, sample_user):
    mock_post.return_value = _mock_response(200, {"code": 200, "message": "登录失败"})

    login(client)
    resp = client.post(
        f"/training/{sample_task}/run",
        data={
            "case_name": "字段断言测试",
            "method": "POST",
            "url": "/mock/login",
            "headers": "{}",
            "params": '{"username": "admin", "password": "wrong"}',
            "expected_status_code": "200",
            "expected_field": "message",
            "expected_value": "登录成功",
            "max_response_time": "",
            "csrf_token": get_csrf_token(client, f"/training/{sample_task}"),
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "测试未通过" in html
    assert "字段断言" in html


@patch("app.services.training_service.http_requests.post")
def test_run_time_assertion(mock_post, client, sample_task, sample_user):
    mock_post.return_value = _mock_response(200, {"code": 200, "message": "登录成功"})

    login(client)
    resp = client.post(
        f"/training/{sample_task}/run",
        data={
            "case_name": "响应时间断言测试",
            "method": "POST",
            "url": "/mock/login",
            "headers": "{}",
            "params": '{"username": "admin", "password": "123456"}',
            "expected_status_code": "200",
            "expected_field": "",
            "expected_value": "",
            "max_response_time": "1",
            "csrf_token": get_csrf_token(client, f"/training/{sample_task}"),
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    # The mock is fast but we set max_response_time=1ms, so it might fail
    # Either way, the test result page should be rendered
    assert "响应时间断言" in html


def test_run_empty_url(client, sample_task, sample_user):
    login(client)
    resp = client.post(
        f"/training/{sample_task}/run",
        data={
            "case_name": "空地址测试",
            "method": "POST",
            "url": "",
            "headers": "{}",
            "params": "{}",
            "expected_status_code": "",
            "expected_field": "",
            "expected_value": "",
            "max_response_time": "",
            "csrf_token": get_csrf_token(client, f"/training/{sample_task}"),
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert "请求地址不能为空" in resp.get_data(as_text=True)


def test_build_url_does_not_trust_host_header(app):
    from app.services.training_service import _build_url

    with app.test_request_context("/", base_url="http://example.com:5000/"):
        assert _build_url("/mock/login") == "http://127.0.0.1:5000/mock/login"


@pytest.mark.parametrize(
    "unsafe_url",
    [
        "/health",
        "http://example.com",
        "https://example.com/mock/login",
        "http://127.0.0.1:5000/mock/login",
        "http://localhost:5000/mock/login",
        "http://192.168.1.10/mock/login",
        "/mock/../health",
    ],
)
@patch("app.services.training_service.http_requests.post")
def test_run_rejects_non_mock_urls(
    mock_post, client, sample_task, sample_user, unsafe_url
):
    login(client)
    resp = client.post(
        f"/training/{sample_task}/run",
        data={
            "case_name": "非法地址测试",
            "method": "POST",
            "url": unsafe_url,
            "headers": "{}",
            "params": "{}",
            "expected_status_code": "200",
            "expected_field": "",
            "expected_value": "",
            "max_response_time": "",
            "csrf_token": get_csrf_token(client, f"/training/{sample_task}"),
        },
        follow_redirects=True,
    )

    assert resp.status_code == 200
    assert "仅允许测试平台内置的 /mock/... 接口" in resp.get_data(as_text=True)
    mock_post.assert_not_called()
    with client.application.app_context():
        result = ApiTestResult.query.order_by(ApiTestResult.id.desc()).first()
        assert result is not None
        assert result.is_passed is False
        assert "仅允许测试平台内置的 /mock/... 接口" in result.error_message


@patch("app.services.training_service.http_requests.post")
def test_run_json_array_field_assertion_saves_error(
    mock_post, client, sample_task, sample_user
):
    mock_post.return_value = _mock_response(200, [{"code": 200}])
    login(client)

    resp = client.post(
        f"/training/{sample_task}/run",
        data={
            "case_name": "数组响应测试",
            "method": "POST",
            "url": "/mock/login",
            "headers": "{}",
            "params": "{}",
            "expected_status_code": "200",
            "expected_field": "code",
            "expected_value": "200",
            "max_response_time": "",
            "csrf_token": get_csrf_token(client, f"/training/{sample_task}"),
        },
        follow_redirects=True,
    )

    assert resp.status_code == 200
    assert "响应JSON不是对象，无法执行字段断言" in resp.get_data(as_text=True)
    with client.application.app_context():
        result = ApiTestResult.query.order_by(ApiTestResult.id.desc()).first()
        assert result is not None
        assert result.field_assert is False
        assert result.is_passed is False
        assert result.error_message == "响应JSON不是对象，无法执行字段断言"


@patch("app.services.training_service.http_requests.post")
def test_run_requires_at_least_one_assertion(
    mock_post, client, sample_task, sample_user
):
    login(client)
    resp = client.post(
        f"/training/{sample_task}/run",
        data={
            "case_name": "空断言测试",
            "method": "POST",
            "url": "/mock/login",
            "headers": "{}",
            "params": "{}",
            "expected_status_code": "",
            "expected_field": "",
            "expected_value": "",
            "max_response_time": "",
            "csrf_token": get_csrf_token(client, f"/training/{sample_task}"),
        },
        follow_redirects=True,
    )

    assert resp.status_code == 200
    assert "请至少设置一个断言条件" in resp.get_data(as_text=True)
    mock_post.assert_not_called()
    with client.application.app_context():
        result = ApiTestResult.query.order_by(ApiTestResult.id.desc()).first()
        assert result is not None
        assert result.is_passed is False
        assert result.error_message == "请至少设置一个断言条件"


# ---------- Results ----------


def test_results_requires_login(client):
    resp = client.get("/training/results", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_results_empty(client, sample_user):
    login(client)
    resp = client.get("/training/results")
    assert resp.status_code == 200
    assert "暂无测试结果" in resp.get_data(as_text=True)


@patch("app.services.training_service.http_requests.post")
def test_results_after_run(mock_post, client, sample_task, sample_user):
    mock_post.return_value = _mock_response(200, {"code": 200, "message": "登录成功"})

    login(client)
    client.post(
        f"/training/{sample_task}/run",
        data={
            "case_name": "登录测试",
            "method": "POST",
            "url": "/mock/login",
            "headers": "{}",
            "params": '{"username": "admin", "password": "123456"}',
            "expected_status_code": "200",
            "expected_field": "",
            "expected_value": "",
            "max_response_time": "",
            "csrf_token": get_csrf_token(client, f"/training/{sample_task}"),
        },
    )
    resp = client.get("/training/results")
    assert resp.status_code == 200
    assert "登录测试" in resp.get_data(as_text=True)


@patch("app.services.training_service.http_requests.post")
def test_result_detail(mock_post, client, sample_task, sample_user):
    mock_post.return_value = _mock_response(200, {"code": 200, "message": "登录成功"})

    login(client)
    client.post(
        f"/training/{sample_task}/run",
        data={
            "case_name": "详情测试",
            "method": "POST",
            "url": "/mock/login",
            "headers": "{}",
            "params": '{"username": "admin", "password": "123456"}',
            "expected_status_code": "200",
            "expected_field": "message",
            "expected_value": "登录成功",
            "max_response_time": "3000",
            "csrf_token": get_csrf_token(client, f"/training/{sample_task}"),
        },
    )

    # Get the result
    with client.application.app_context():
        result = ApiTestResult.query.first()
        assert result is not None
        result_id = result.id

    resp = client.get(f"/training/results/{result_id}")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "详情测试" in html
    assert "状态码断言" in html
    assert "字段断言" in html
    assert "响应内容" in html


def test_result_detail_forbidden(client, sample_task, sample_user):
    """User can only see their own results."""
    login(client)

    # Create a result directly in DB for another user
    with client.application.app_context():
        other_user = User(username="other", role="student")
        other_user.set_password("pass123")
        _db.session.add(other_user)
        _db.session.commit()

        case = ApiTestCase(
            user_id=other_user.id,
            task_id=sample_task,
            case_name="他人用例",
            method="GET",
            url="/mock/user/1",
        )
        _db.session.add(case)
        _db.session.commit()

        result = ApiTestResult(
            user_id=other_user.id,
            case_id=case.id,
            is_passed=True,
        )
        _db.session.add(result)
        _db.session.commit()
        result_id = result.id

    resp = client.get(f"/training/results/{result_id}")
    assert resp.status_code == 403


# ---------- Mock API ----------


def test_mock_login_success(client):
    resp = client.post(
        "/mock/login",
        json={"username": "admin", "password": "123456"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["code"] == 200
    assert data["message"] == "登录成功"
    assert "token" in data


def test_mock_login_failure(client):
    resp = client.post(
        "/mock/login",
        json={"username": "admin", "password": "wrong"},
    )
    assert resp.status_code == 401
    data = resp.get_json()
    assert data["code"] == 401
    assert data["message"] == "用户名或密码错误"


def test_mock_user_found(client):
    resp = client.get("/mock/user/1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["code"] == 200
    assert data["data"]["username"] == "admin"


def test_mock_user_not_found(client):
    resp = client.get("/mock/user/999")
    assert resp.status_code == 404
    data = resp.get_json()
    assert data["code"] == 404


def test_mock_product_add_success(client):
    resp = client.post(
        "/mock/product/add",
        json={"product_name": "测试商品", "price": 99.9},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["code"] == 200
    assert data["message"] == "商品添加成功"


def test_mock_product_add_missing_param(client):
    resp = client.post(
        "/mock/product/add",
        json={"product_name": "缺少价格"},
    )
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["code"] == 400


# ---------- Existing routes unaffected ----------


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_db_check(client):
    resp = client.get("/db-check")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"
