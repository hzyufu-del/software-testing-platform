"""Authentication routes: register, login, logout, profile."""

from urllib.parse import unquote, urlsplit

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.services.auth_service import authenticate, register_user

auth_bp = Blueprint("auth", __name__)


def _is_safe_next_url(target: str | None) -> bool:
    """Return whether target is a local absolute path."""
    if not target:
        return False

    decoded_target = unquote(target)
    parsed = urlsplit(decoded_target)
    return (
        decoded_target.startswith("/")
        and not decoded_target.startswith("//")
        and "\\" not in decoded_target
        and not parsed.scheme
        and not parsed.netloc
    )


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        confirm = request.form.get("confirm", "").strip()

        if not username or not password:
            flash("用户名和密码不能为空", "danger")
        elif len(password) < 6:
            flash("密码长度不能少于6位", "danger")
        elif password != confirm:
            flash("两次输入的密码不一致", "danger")
        else:
            try:
                register_user(username, password)
                flash("注册成功，请登录", "success")
                return redirect(url_for("auth.login"))
            except ValueError as e:
                flash(str(e), "danger")

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        user = authenticate(username, password)
        if user is not None:
            login_user(user)
            flash("登录成功", "success")
            next_page = request.args.get("next")
            if not _is_safe_next_url(next_page):
                next_page = url_for("main.index")
            return redirect(next_page)
        else:
            flash("用户名或密码错误", "danger")

    return render_template("login.html")


@auth_bp.post("/logout")
@login_required
def logout():
    logout_user()
    flash("已退出登录", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/profile")
@login_required
def profile():
    from app.services.dashboard_service import get_user_stats

    stats = get_user_stats(current_user.id)
    return render_template("profile.html", stats=stats)
