"""Initialize the database: create all tables defined by SQLAlchemy models.

Usage:
    python init_db.py
"""

from app import create_app, db

# Ensure all models are imported so SQLAlchemy knows about them
import app.models  # noqa: F401

app = create_app()

with app.app_context():
    db.create_all()
    print("数据库表创建完成。")
