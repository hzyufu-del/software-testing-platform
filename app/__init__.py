from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from config import Config


db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    csrf.init_app(app)

    # Flask-Login setup
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "请先登录"
    login_manager.login_message_category = "warning"

    # Register blueprints
    from app.mock_api.routes import mock_bp
    from app.routes.auth import auth_bp
    from app.routes.course import course_bp
    from app.routes.main import main_bp
    from app.routes.question import question_bp
    from app.routes.training import training_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(question_bp)
    app.register_blueprint(training_bp)
    app.register_blueprint(mock_bp)

    # Exempt mock API from CSRF (these are programmatic endpoints)
    csrf.exempt(mock_bp)

    return app


@login_manager.user_loader
def load_user(user_id: str):
    from app.models import User

    return db.session.get(User, int(user_id))
