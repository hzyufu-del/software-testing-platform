from flask import Blueprint, current_app, jsonify, render_template
from flask_login import current_user
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.services.dashboard_service import get_user_stats


main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    stats = None
    if current_user.is_authenticated:
        stats = get_user_stats(current_user.id)
    return render_template("index.html", stats=stats)


@main_bp.get("/health")
def health():
    return jsonify(status="ok")


@main_bp.get("/db-check")
def db_check():
    try:
        result = db.session.execute(text("SELECT 1")).scalar_one()
        return jsonify(status="ok", database="connected", result=result)
    except SQLAlchemyError:
        current_app.logger.exception("Database connection check failed")
        return jsonify(status="error", database="disconnected"), 500

