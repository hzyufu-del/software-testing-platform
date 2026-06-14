"""Training service: execute API test cases and save results."""

import json
import posixpath
import time
from urllib.parse import unquote, urlsplit

import requests as http_requests
from flask import request as flask_request

from app import db
from app.models import ApiTestCase, ApiTestResult, TrainingTask


# ---------- Training task queries ----------


def get_all_tasks() -> list[TrainingTask]:
    """Return all training tasks ordered by sort_order."""
    return TrainingTask.query.order_by(TrainingTask.sort_order).all()


def get_task_by_id(task_id: int) -> TrainingTask | None:
    """Return a TrainingTask by primary key, or None."""
    return db.session.get(TrainingTask, task_id)


# ---------- Test case CRUD ----------


def save_test_case(user_id: int, task_id: int, form_data: dict) -> ApiTestCase:
    """Create a new ApiTestCase from form data."""
    case = ApiTestCase(
        user_id=user_id,
        task_id=task_id,
        case_name=form_data.get("case_name", "未命名用例"),
        method=form_data.get("method", "GET").upper(),
        url=form_data.get("url", ""),
        headers=form_data.get("headers", "{}"),
        params=form_data.get("params", "{}"),
        expected_status_code=_parse_int(form_data.get("expected_status_code")),
        expected_field=form_data.get("expected_field", ""),
        expected_value=form_data.get("expected_value", ""),
        max_response_time=_parse_int(form_data.get("max_response_time")),
    )
    db.session.add(case)
    db.session.commit()
    return case


# ---------- Execute test ----------


def execute_test(user_id: int, case_id: int) -> ApiTestResult:
    """Execute an API test case and return the result."""
    case = db.session.get(ApiTestCase, case_id)
    if case is None:
        raise ValueError("测试用例不存在")

    if (
        case.expected_status_code is None
        and not case.expected_field
        and case.max_response_time is None
    ):
        return _save_error_result(user_id, case_id, "请至少设置一个断言条件")

    # Parse headers and params
    headers, err = _parse_json_field(case.headers, "请求头")
    if err:
        return _save_error_result(user_id, case_id, err)

    params, err = _parse_json_field(case.params, "请求参数")
    if err:
        return _save_error_result(user_id, case_id, err)

    # Build URL
    try:
        url = _build_url(case.url)
    except ValueError as exc:
        return _save_error_result(user_id, case_id, str(exc))

    # Execute request
    try:
        start = time.monotonic()
        if case.method == "GET":
            resp = http_requests.get(url, headers=headers, params=params, timeout=10)
        elif case.method == "POST":
            resp = http_requests.post(url, headers=headers, json=params, timeout=10)
        else:
            resp = http_requests.request(case.method, url, headers=headers, json=params, timeout=10)
        elapsed_ms = int((time.monotonic() - start) * 1000)
    except http_requests.RequestException as exc:
        return _save_error_result(user_id, case_id, f"请求异常: {exc}")

    # Parse response
    try:
        resp_json = resp.json()
        resp_text = json.dumps(resp_json, ensure_ascii=False, indent=2)
    except Exception:
        resp_json = {}
        resp_text = resp.text

    # Assertions
    status_ok = _assert_status(case.expected_status_code, resp.status_code)
    field_error = ""
    if case.expected_field and not isinstance(resp_json, dict):
        field_ok = False
        field_error = "响应JSON不是对象，无法执行字段断言"
    else:
        field_ok = _assert_field(case.expected_field, case.expected_value, resp_json)
    time_ok = _assert_time(case.max_response_time, elapsed_ms)

    is_passed = all(
        v is True for v in [status_ok, field_ok, time_ok] if v is not None
    )

    result = ApiTestResult(
        user_id=user_id,
        case_id=case_id,
        actual_status_code=resp.status_code,
        actual_response=resp_text,
        response_time=elapsed_ms,
        status_assert=status_ok,
        field_assert=field_ok,
        time_assert=time_ok,
        is_passed=is_passed,
        error_message=field_error,
    )
    db.session.add(result)
    db.session.commit()
    return result


# ---------- Result queries ----------


def get_results_by_user(user_id: int) -> list[ApiTestResult]:
    """Return all test results for a user, newest first."""
    return (
        ApiTestResult.query
        .filter_by(user_id=user_id)
        .order_by(ApiTestResult.execute_time.desc())
        .all()
    )


def get_result_by_id(result_id: int) -> ApiTestResult | None:
    """Return an ApiTestResult by primary key, or None."""
    return db.session.get(ApiTestResult, result_id)


# ---------- Internal helpers ----------


def _parse_json_field(raw: str, field_name: str) -> tuple[dict, str]:
    """Parse a JSON string, return (dict, error_msg)."""
    if not raw or not raw.strip():
        return {}, ""
    try:
        data = json.loads(raw)
        if not isinstance(data, dict):
            return {}, f"{field_name}必须是JSON对象"
        return data, ""
    except json.JSONDecodeError as exc:
        return {}, f"{field_name}不是合法JSON: {exc}"


def _build_url(url: str) -> str:
    """Build a local URL for an allowlisted mock API path."""
    raw_url = url.strip()
    parsed = urlsplit(raw_url)
    decoded_path = unquote(parsed.path)
    normalized_path = posixpath.normpath(decoded_path)

    if (
        parsed.scheme
        or parsed.netloc
        or parsed.fragment
        or not decoded_path.startswith("/mock/")
        or "\\" in decoded_path
        or not normalized_path.startswith("/mock/")
    ):
        raise ValueError("仅允许测试平台内置的 /mock/... 接口")

    server_port = str(flask_request.environ.get("SERVER_PORT", "5000"))
    if not server_port.isdigit():
        raise ValueError("无法确定本地模拟接口端口")

    base = f"http://127.0.0.1:{server_port}"
    return base + raw_url


def _assert_status(expected: int | None, actual: int) -> bool | None:
    if expected is None:
        return None
    return expected == actual


def _assert_field(field: str, value: str, resp_json: dict) -> bool | None:
    if not field:
        return None
    if not isinstance(resp_json, dict):
        return False
    actual = resp_json.get(field)
    if actual is None:
        return False
    return str(actual) == str(value)


def _assert_time(max_ms: int | None, actual_ms: int) -> bool | None:
    if max_ms is None:
        return None
    return actual_ms <= max_ms


def _save_error_result(user_id: int, case_id: int, error_msg: str) -> ApiTestResult:
    """Save a result with an error message."""
    result = ApiTestResult(
        user_id=user_id,
        case_id=case_id,
        actual_status_code=None,
        actual_response="",
        response_time=None,
        status_assert=None,
        field_assert=None,
        time_assert=None,
        is_passed=False,
        error_message=error_msg,
    )
    db.session.add(result)
    db.session.commit()
    return result


def _parse_int(value) -> int | None:
    """Parse a value to int, return None if empty or invalid."""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None
