"""Database models for the software testing platform."""

from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db


class User(db.Model, UserMixin):
    """User account model."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student")
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def set_password(self, password: str) -> None:
        """Hash and store the password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify a password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class Course(db.Model):
    """Course model."""

    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    cover = db.Column(db.String(500), nullable=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now)

    chapters = db.relationship(
        "Chapter", backref="course", lazy="dynamic", order_by="Chapter.sort_order"
    )

    def __repr__(self) -> str:
        return f"<Course {self.title}>"


class Chapter(db.Model):
    """Chapter model belonging to a course."""

    __tablename__ = "chapters"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(
        db.Integer, db.ForeignKey("courses.id"), nullable=False, index=True
    )
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False, default="")
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now)

    records = db.relationship("LearningRecord", backref="chapter", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Chapter {self.title}>"


class LearningRecord(db.Model):
    """Tracks a user's completion of a chapter."""

    __tablename__ = "learning_records"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    chapter_id = db.Column(
        db.Integer, db.ForeignKey("chapters.id"), nullable=False, index=True
    )
    is_completed = db.Column(db.Boolean, nullable=False, default=False)
    complete_time = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        db.UniqueConstraint("user_id", "chapter_id", name="uq_user_chapter"),
    )

    def __repr__(self) -> str:
        return f"<LearningRecord user={self.user_id} chapter={self.chapter_id}>"


class Question(db.Model):
    """Question model for the quiz bank."""

    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chapter_id = db.Column(
        db.Integer, db.ForeignKey("chapters.id"), nullable=True, index=True
    )
    question_type = db.Column(db.String(20), nullable=False, default="single")
    title = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(500), nullable=True)
    option_b = db.Column(db.String(500), nullable=True)
    option_c = db.Column(db.String(500), nullable=True)
    option_d = db.Column(db.String(500), nullable=True)
    correct_answer = db.Column(db.String(10), nullable=False)
    explanation = db.Column(db.Text, nullable=True, default="")
    difficulty = db.Column(db.String(20), nullable=False, default="medium")
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now)

    chapter = db.relationship("Chapter", backref="questions", lazy="joined")

    def __repr__(self) -> str:
        return f"<Question {self.id}>"


class AnswerRecord(db.Model):
    """Records each answer submission by a user."""

    __tablename__ = "answer_records"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    question_id = db.Column(
        db.Integer, db.ForeignKey("questions.id"), nullable=False, index=True
    )
    user_answer = db.Column(db.String(10), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    answer_time = db.Column(db.DateTime, nullable=False, default=datetime.now)

    user = db.relationship("User", backref="answer_records", lazy="joined")
    question = db.relationship("Question", backref="answer_records", lazy="joined")

    def __repr__(self) -> str:
        return f"<AnswerRecord user={self.user_id} q={self.question_id}>"


class WrongQuestion(db.Model):
    """Tracks questions a user has answered incorrectly."""

    __tablename__ = "wrong_questions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    question_id = db.Column(
        db.Integer, db.ForeignKey("questions.id"), nullable=False, index=True
    )
    wrong_count = db.Column(db.Integer, nullable=False, default=1)
    last_wrong_time = db.Column(db.DateTime, nullable=False, default=datetime.now)

    user = db.relationship("User", backref="wrong_questions", lazy="joined")
    question = db.relationship("Question", backref="wrong_questions", lazy="joined")

    __table_args__ = (
        db.UniqueConstraint("user_id", "question_id", name="uq_user_question"),
    )

    def __repr__(self) -> str:
        return f"<WrongQuestion user={self.user_id} q={self.question_id}>"


class TrainingTask(db.Model):
    """API training task model."""

    __tablename__ = "training_tasks"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    method = db.Column(db.String(10), nullable=False, default="GET")
    endpoint = db.Column(db.String(500), nullable=False)
    request_example = db.Column(db.Text, nullable=True, default="")
    expected_example = db.Column(db.Text, nullable=True, default="")
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self) -> str:
        return f"<TrainingTask {self.title}>"


class ApiTestCase(db.Model):
    """User-created API test case."""

    __tablename__ = "api_test_cases"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    task_id = db.Column(
        db.Integer, db.ForeignKey("training_tasks.id"), nullable=False, index=True
    )
    case_name = db.Column(db.String(200), nullable=False)
    method = db.Column(db.String(10), nullable=False, default="GET")
    url = db.Column(db.String(500), nullable=False)
    headers = db.Column(db.Text, nullable=True, default="{}")
    params = db.Column(db.Text, nullable=True, default="{}")
    expected_status_code = db.Column(db.Integer, nullable=True)
    expected_field = db.Column(db.String(200), nullable=True, default="")
    expected_value = db.Column(db.String(500), nullable=True, default="")
    max_response_time = db.Column(db.Integer, nullable=True)
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now)

    user = db.relationship("User", backref="api_test_cases", lazy="joined")
    task = db.relationship("TrainingTask", backref="test_cases", lazy="joined")

    def __repr__(self) -> str:
        return f"<ApiTestCase {self.case_name}>"


class ApiTestResult(db.Model):
    """Result of executing an API test case."""

    __tablename__ = "api_test_results"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    case_id = db.Column(
        db.Integer, db.ForeignKey("api_test_cases.id"), nullable=False, index=True
    )
    actual_status_code = db.Column(db.Integer, nullable=True)
    actual_response = db.Column(db.Text, nullable=True, default="")
    response_time = db.Column(db.Integer, nullable=True)
    status_assert = db.Column(db.Boolean, nullable=True)
    field_assert = db.Column(db.Boolean, nullable=True)
    time_assert = db.Column(db.Boolean, nullable=True)
    is_passed = db.Column(db.Boolean, nullable=False, default=False)
    error_message = db.Column(db.Text, nullable=True, default="")
    execute_time = db.Column(db.DateTime, nullable=False, default=datetime.now)

    user = db.relationship("User", backref="api_test_results", lazy="joined")
    case = db.relationship("ApiTestCase", backref="results", lazy="joined")

    def __repr__(self) -> str:
        return f"<ApiTestResult case={self.case_id} passed={self.is_passed}>"

