"""Training routes: task list, detail, execute test, results."""

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.services.training_service import (
    execute_test,
    get_all_tasks,
    get_result_by_id,
    get_results_by_user,
    get_task_by_id,
    save_test_case,
)

training_bp = Blueprint("training", __name__)


@training_bp.get("/training")
def task_list():
    """Display all training tasks."""
    tasks = get_all_tasks()
    return render_template("training_tasks.html", tasks=tasks)


@training_bp.get("/training/<int:task_id>")
def task_detail(task_id: int):
    """Display a training task and test case form."""
    task = get_task_by_id(task_id)
    if task is None:
        abort(404)
    return render_template("training_detail.html", task=task)


@training_bp.post("/training/<int:task_id>/run")
@login_required
def task_run(task_id: int):
    """Save test case and execute API test."""
    task = get_task_by_id(task_id)
    if task is None:
        abort(404)

    # Collect form data
    form_data = {
        "case_name": request.form.get("case_name", "").strip(),
        "method": request.form.get("method", "GET").strip(),
        "url": request.form.get("url", "").strip(),
        "headers": request.form.get("headers", "{}").strip(),
        "params": request.form.get("params", "{}").strip(),
        "expected_status_code": request.form.get("expected_status_code", "").strip(),
        "expected_field": request.form.get("expected_field", "").strip(),
        "expected_value": request.form.get("expected_value", "").strip(),
        "max_response_time": request.form.get("max_response_time", "").strip(),
    }

    if not form_data["url"]:
        flash("请求地址不能为空", "danger")
        return redirect(url_for("training.task_detail", task_id=task_id))

    # Save case
    case = save_test_case(current_user.id, task_id, form_data)

    # Execute
    result = execute_test(current_user.id, case.id)

    if result.error_message:
        flash(f"测试执行出错: {result.error_message}", "danger")
    elif result.is_passed:
        flash("测试通过！", "success")
    else:
        flash("测试未通过，请查看断言详情。", "warning")

    return redirect(url_for("training.result_detail", result_id=result.id))


@training_bp.get("/training/results")
@login_required
def result_list():
    """Display current user's test results."""
    results = get_results_by_user(current_user.id)
    return render_template("training_results.html", results=results)


@training_bp.get("/training/results/<int:result_id>")
@login_required
def result_detail(result_id: int):
    """Display a single test result detail."""
    result = get_result_by_id(result_id)
    if result is None:
        abort(404)
    if result.user_id != current_user.id:
        abort(403)
    return render_template("training_result_detail.html", result=result)
