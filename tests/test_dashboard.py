"""Tests for dashboard statistics (service + routes)."""

import re

import pytest

from app import create_app, db as _db
from app.models import (
    AnswerRecord,
    ApiTestCase,
    ApiTestResult,
    Chapter,
    Course,
    LearningRecord,
    Question,
    TrainingTask,
    User,
    WrongQuestion,
)
from app.services.dashboard_service import get_user_stats


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
def other_user(app):
    """A second user for isolation tests."""
    with app.app_context():
        user = User(username="other", role="student")
        user.set_password("password123")
        _db.session.add(user)
        _db.session.commit()
        user_id = user.id
    return user_id


@pytest.fixture()
def sample_course(app):
    """Create a course with 4 chapters."""
    with app.app_context():
        course = Course(title="测试课程", description="简介", sort_order=1)
        _db.session.add(course)
        _db.session.flush()
        chapters = []
        for i in range(1, 5):
            ch = Chapter(
                course_id=course.id,
                title=f"第{i}章",
                content=f"<p>内容{i}</p>",
                sort_order=i,
            )
            chapters.append(ch)
        _db.session.add_all(chapters)
        _db.session.commit()
        return course.id, [ch.id for ch in chapters]


@pytest.fixture()
def sample_questions(app):
    """Create 3 questions."""
    with app.app_context():
        questions = []
        for i, (answer, diff) in enumerate(
            [("A", "easy"), ("B", "medium"), ("C", "hard")], start=1
        ):
            q = Question(
                question_type="single",
                title=f"题目{i}",
                option_a="选项A",
                option_b="选项B",
                option_c="选项C",
                option_d="选项D",
                correct_answer=answer,
                explanation=f"解析{i}",
                difficulty=diff,
            )
            questions.append(q)
        _db.session.add_all(questions)
        _db.session.commit()
        return [q.id for q in questions]


@pytest.fixture()
def sample_task(app):
    """Create a training task."""
    with app.app_context():
        task = TrainingTask(
            title="登录测试",
            description="测试登录接口",
            method="POST",
            endpoint="/mock/login",
            request_example="{}",
            expected_example="{}",
            sort_order=1,
        )
        _db.session.add(task)
        _db.session.commit()
        return task.id


# ============================================================
# Route tests – anonymous vs logged-in
# ============================================================


class TestIndexAnonymous:
    """Anonymous user sees landing page, not stats."""

    def test_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_shows_platform_intro(self, client):
        html = client.get("/").get_data(as_text=True)
        assert "面向软件测试学习与实践的一体化平台" in html

    def test_shows_feature_cards(self, client):
        html = client.get("/").get_data(as_text=True)
        assert "核心功能模块" in html
        assert "课程学习" in html
        assert "题库练习" in html
        assert "接口实训" in html

    def test_shows_system_status(self, client):
        html = client.get("/").get_data(as_text=True)
        assert "系统运行状态" in html

    def test_does_not_show_stats(self, client):
        html = client.get("/").get_data(as_text=True)
        assert "我的学习统计" not in html
        assert "stat-card" not in html


class TestIndexLoggedIn:
    """Logged-in user sees stats on index, not the anonymous intro."""

    def test_returns_200(self, client, sample_user):
        login(client)
        resp = client.get("/")
        assert resp.status_code == 200

    def test_shows_welcome_back(self, client, sample_user):
        login(client)
        html = client.get("/").get_data(as_text=True)
        assert "欢迎回来" in html
        assert "testuser" in html

    def test_shows_stats_section(self, client, sample_user):
        login(client)
        html = client.get("/").get_data(as_text=True)
        assert "我的学习统计" in html
        assert "stat-card" in html

    def test_shows_all_three_stat_groups(self, client, sample_user):
        login(client)
        html = client.get("/").get_data(as_text=True)
        assert "课程学习" in html
        assert "题库练习" in html
        assert "接口实训" in html

    def test_shows_stat_labels(self, client, sample_user):
        login(client)
        html = client.get("/").get_data(as_text=True)
        assert "已完成章节" in html
        assert "总章节数" in html
        assert "学习进度" in html
        assert "答题总数" in html
        assert "答对数量" in html
        assert "错题数量" in html
        assert "正确率" in html
        assert "执行次数" in html
        assert "通过次数" in html
        assert "通过率" in html

    def test_does_not_show_anonymous_sections(self, client, sample_user):
        login(client)
        html = client.get("/").get_data(as_text=True)
        assert "核心功能模块" not in html
        assert "系统运行状态" not in html

    def test_empty_stats_shows_zeros(self, client, sample_user):
        login(client)
        html = client.get("/").get_data(as_text=True)
        # All stat values should be 0
        assert ">0<" in html  # multiple zeros for counts
        assert "0%" in html  # progress / accuracy / pass_rate


# ============================================================
# Service tests – get_user_stats with no data
# ============================================================


class TestStatsEmpty:
    """When the user has no activity, all values are zero."""

    def test_returns_all_keys(self, app, sample_user):
        with app.app_context():
            stats = get_user_stats(sample_user)
        expected_keys = {
            "completed_chapters",
            "total_chapters",
            "course_progress",
            "total_answers",
            "correct_answers",
            "wrong_count",
            "accuracy",
            "total_tests",
            "passed_tests",
            "pass_rate",
        }
        assert set(stats.keys()) == expected_keys

    def test_no_chapters(self, app, sample_user):
        with app.app_context():
            stats = get_user_stats(sample_user)
        assert stats["total_chapters"] == 0
        assert stats["completed_chapters"] == 0
        assert stats["course_progress"] == 0

    def test_no_answers(self, app, sample_user):
        with app.app_context():
            stats = get_user_stats(sample_user)
        assert stats["total_answers"] == 0
        assert stats["correct_answers"] == 0
        assert stats["wrong_count"] == 0
        assert stats["accuracy"] == 0

    def test_no_tests(self, app, sample_user):
        with app.app_context():
            stats = get_user_stats(sample_user)
        assert stats["total_tests"] == 0
        assert stats["passed_tests"] == 0
        assert stats["pass_rate"] == 0

    def test_no_division_by_zero(self, app, sample_user):
        """Percentages must be 0, not raise ZeroDivisionError."""
        with app.app_context():
            stats = get_user_stats(sample_user)
        assert isinstance(stats["course_progress"], (int, float))
        assert isinstance(stats["accuracy"], (int, float))
        assert isinstance(stats["pass_rate"], (int, float))


# ============================================================
# Service tests – course stats
# ============================================================


class TestStatsCourse:
    """Course learning statistics."""

    def test_total_chapters(self, app, sample_user, sample_course):
        with app.app_context():
            stats = get_user_stats(sample_user)
        assert stats["total_chapters"] == 4

    def test_completed_chapters_zero(self, app, sample_user, sample_course):
        with app.app_context():
            stats = get_user_stats(sample_user)
        assert stats["completed_chapters"] == 0
        assert stats["course_progress"] == 0

    def test_completed_chapters_partial(self, app, sample_user, sample_course):
        _, chapter_ids = sample_course
        with app.app_context():
            # Complete 1 of 4 chapters
            record = LearningRecord(
                user_id=sample_user,
                chapter_id=chapter_ids[0],
                is_completed=True,
            )
            _db.session.add(record)
            _db.session.commit()

            stats = get_user_stats(sample_user)
        assert stats["completed_chapters"] == 1
        assert stats["total_chapters"] == 4
        assert stats["course_progress"] == 25.0

    def test_completed_chapters_all(self, app, sample_user, sample_course):
        _, chapter_ids = sample_course
        with app.app_context():
            for ch_id in chapter_ids:
                _db.session.add(
                    LearningRecord(
                        user_id=sample_user,
                        chapter_id=ch_id,
                        is_completed=True,
                    )
                )
            _db.session.commit()

            stats = get_user_stats(sample_user)
        assert stats["completed_chapters"] == 4
        assert stats["course_progress"] == 100.0

    def test_incomplete_record_not_counted(self, app, sample_user, sample_course):
        _, chapter_ids = sample_course
        with app.app_context():
            _db.session.add(
                LearningRecord(
                    user_id=sample_user,
                    chapter_id=chapter_ids[0],
                    is_completed=False,
                )
            )
            _db.session.commit()

            stats = get_user_stats(sample_user)
        assert stats["completed_chapters"] == 0


# ============================================================
# Service tests – quiz stats
# ============================================================


class TestStatsQuiz:
    """Quiz / answer statistics."""

    def test_total_answers(self, app, sample_user, sample_questions):
        q_ids = sample_questions
        with app.app_context():
            # Answer 2 questions
            _db.session.add(
                AnswerRecord(
                    user_id=sample_user,
                    question_id=q_ids[0],
                    user_answer="A",
                    is_correct=True,
                )
            )
            _db.session.add(
                AnswerRecord(
                    user_id=sample_user,
                    question_id=q_ids[1],
                    user_answer="A",
                    is_correct=False,
                )
            )
            _db.session.commit()

            stats = get_user_stats(sample_user)
        assert stats["total_answers"] == 2

    def test_correct_answers(self, app, sample_user, sample_questions):
        q_ids = sample_questions
        with app.app_context():
            _db.session.add(
                AnswerRecord(
                    user_id=sample_user,
                    question_id=q_ids[0],
                    user_answer="A",
                    is_correct=True,
                )
            )
            _db.session.add(
                AnswerRecord(
                    user_id=sample_user,
                    question_id=q_ids[1],
                    user_answer="A",
                    is_correct=False,
                )
            )
            _db.session.commit()

            stats = get_user_stats(sample_user)
        assert stats["correct_answers"] == 1

    def test_accuracy_half(self, app, sample_user, sample_questions):
        q_ids = sample_questions
        with app.app_context():
            _db.session.add(
                AnswerRecord(
                    user_id=sample_user,
                    question_id=q_ids[0],
                    user_answer="A",
                    is_correct=True,
                )
            )
            _db.session.add(
                AnswerRecord(
                    user_id=sample_user,
                    question_id=q_ids[1],
                    user_answer="A",
                    is_correct=False,
                )
            )
            _db.session.commit()

            stats = get_user_stats(sample_user)
        assert stats["accuracy"] == 50.0

    def test_accuracy_all_correct(self, app, sample_user, sample_questions):
        q_ids = sample_questions
        with app.app_context():
            for q_id in q_ids[:2]:
                _db.session.add(
                    AnswerRecord(
                        user_id=sample_user,
                        question_id=q_id,
                        user_answer="A",
                        is_correct=True,
                    )
                )
            _db.session.commit()

            stats = get_user_stats(sample_user)
        assert stats["accuracy"] == 100.0

    def test_wrong_count(self, app, sample_user, sample_questions):
        q_ids = sample_questions
        with app.app_context():
            _db.session.add(
                WrongQuestion(
                    user_id=sample_user,
                    question_id=q_ids[0],
                    wrong_count=1,
                )
            )
            _db.session.add(
                WrongQuestion(
                    user_id=sample_user,
                    question_id=q_ids[1],
                    wrong_count=2,
                )
            )
            _db.session.commit()

            stats = get_user_stats(sample_user)
        # WrongQuestion count = number of rows (not wrong_count sum)
        assert stats["wrong_count"] == 2


# ============================================================
# Service tests – training stats
# ============================================================


class TestStatsTraining:
    """API training statistics."""

    def _create_case_and_result(
        self, app, user_id, task_id, is_passed
    ):
        with app.app_context():
            case = ApiTestCase(
                user_id=user_id,
                task_id=task_id,
                case_name="测试用例",
                method="GET",
                url="/mock/user/1",
            )
            _db.session.add(case)
            _db.session.flush()

            result = ApiTestResult(
                user_id=user_id,
                case_id=case.id,
                is_passed=is_passed,
            )
            _db.session.add(result)
            _db.session.commit()

    def test_total_tests(self, app, sample_user, sample_task):
        self._create_case_and_result(app, sample_user, sample_task, True)
        self._create_case_and_result(app, sample_user, sample_task, False)

        with app.app_context():
            stats = get_user_stats(sample_user)
        assert stats["total_tests"] == 2

    def test_passed_tests(self, app, sample_user, sample_task):
        self._create_case_and_result(app, sample_user, sample_task, True)
        self._create_case_and_result(app, sample_user, sample_task, False)

        with app.app_context():
            stats = get_user_stats(sample_user)
        assert stats["passed_tests"] == 1

    def test_pass_rate_half(self, app, sample_user, sample_task):
        self._create_case_and_result(app, sample_user, sample_task, True)
        self._create_case_and_result(app, sample_user, sample_task, False)

        with app.app_context():
            stats = get_user_stats(sample_user)
        assert stats["pass_rate"] == 50.0

    def test_pass_rate_all_pass(self, app, sample_user, sample_task):
        self._create_case_and_result(app, sample_user, sample_task, True)
        self._create_case_and_result(app, sample_user, sample_task, True)

        with app.app_context():
            stats = get_user_stats(sample_user)
        assert stats["pass_rate"] == 100.0

    def test_pass_rate_none_pass(self, app, sample_user, sample_task):
        self._create_case_and_result(app, sample_user, sample_task, False)
        self._create_case_and_result(app, sample_user, sample_task, False)

        with app.app_context():
            stats = get_user_stats(sample_user)
        assert stats["pass_rate"] == 0


# ============================================================
# Service tests – user isolation
# ============================================================


class TestStatsUserIsolation:
    """Each user's stats must only reflect their own data."""

    def test_other_user_chapters_not_counted(
        self, app, sample_user, other_user, sample_course
    ):
        _, chapter_ids = sample_course
        with app.app_context():
            # other_user completes all chapters
            for ch_id in chapter_ids:
                _db.session.add(
                    LearningRecord(
                        user_id=other_user,
                        chapter_id=ch_id,
                        is_completed=True,
                    )
                )
            _db.session.commit()

            # sample_user should see 0 completed
            stats = get_user_stats(sample_user)
        assert stats["completed_chapters"] == 0
        assert stats["course_progress"] == 0

    def test_other_user_answers_not_counted(
        self, app, sample_user, other_user, sample_questions
    ):
        q_ids = sample_questions
        with app.app_context():
            # other_user answers all questions correctly
            for q_id in q_ids:
                _db.session.add(
                    AnswerRecord(
                        user_id=other_user,
                        question_id=q_id,
                        user_answer="A",
                        is_correct=True,
                    )
                )
            _db.session.commit()

            stats = get_user_stats(sample_user)
        assert stats["total_answers"] == 0
        assert stats["correct_answers"] == 0
        assert stats["accuracy"] == 0

    def test_other_user_wrong_questions_not_counted(
        self, app, sample_user, other_user, sample_questions
    ):
        q_ids = sample_questions
        with app.app_context():
            _db.session.add(
                WrongQuestion(
                    user_id=other_user,
                    question_id=q_ids[0],
                    wrong_count=5,
                )
            )
            _db.session.commit()

            stats = get_user_stats(sample_user)
        assert stats["wrong_count"] == 0

    def test_other_user_tests_not_counted(
        self, app, sample_user, other_user, sample_task
    ):
        with app.app_context():
            case = ApiTestCase(
                user_id=other_user,
                task_id=sample_task,
                case_name="他人用例",
                method="GET",
                url="/mock/user/1",
            )
            _db.session.add(case)
            _db.session.flush()
            _db.session.add(
                ApiTestResult(
                    user_id=other_user,
                    case_id=case.id,
                    is_passed=True,
                )
            )
            _db.session.commit()

            stats = get_user_stats(sample_user)
        assert stats["total_tests"] == 0
        assert stats["passed_tests"] == 0
        assert stats["pass_rate"] == 0

    def test_mixed_data_isolation(
        self, app, sample_user, other_user, sample_course, sample_questions, sample_task
    ):
        """Both users have data; each sees only their own."""
        _, chapter_ids = sample_course
        q_ids = sample_questions
        with app.app_context():
            # sample_user: 1 chapter, 1 correct answer, 1 passed test
            _db.session.add(
                LearningRecord(
                    user_id=sample_user,
                    chapter_id=chapter_ids[0],
                    is_completed=True,
                )
            )
            _db.session.add(
                AnswerRecord(
                    user_id=sample_user,
                    question_id=q_ids[0],
                    user_answer="A",
                    is_correct=True,
                )
            )
            case_a = ApiTestCase(
                user_id=sample_user,
                task_id=sample_task,
                case_name="用例A",
                method="GET",
                url="/mock/user/1",
            )
            _db.session.add(case_a)
            _db.session.flush()
            _db.session.add(
                ApiTestResult(
                    user_id=sample_user, case_id=case_a.id, is_passed=True
                )
            )

            # other_user: 3 chapters, 2 answers (1 correct), 1 failed test
            for ch_id in chapter_ids[:3]:
                _db.session.add(
                    LearningRecord(
                        user_id=other_user,
                        chapter_id=ch_id,
                        is_completed=True,
                    )
                )
            _db.session.add(
                AnswerRecord(
                    user_id=other_user,
                    question_id=q_ids[0],
                    user_answer="A",
                    is_correct=True,
                )
            )
            _db.session.add(
                AnswerRecord(
                    user_id=other_user,
                    question_id=q_ids[1],
                    user_answer="A",
                    is_correct=False,
                )
            )
            case_b = ApiTestCase(
                user_id=other_user,
                task_id=sample_task,
                case_name="用例B",
                method="GET",
                url="/mock/user/1",
            )
            _db.session.add(case_b)
            _db.session.flush()
            _db.session.add(
                ApiTestResult(
                    user_id=other_user, case_id=case_b.id, is_passed=False
                )
            )

            _db.session.commit()

            stats_a = get_user_stats(sample_user)
            stats_b = get_user_stats(other_user)

        # sample_user
        assert stats_a["completed_chapters"] == 1
        assert stats_a["total_answers"] == 1
        assert stats_a["correct_answers"] == 1
        assert stats_a["accuracy"] == 100.0
        assert stats_a["total_tests"] == 1
        assert stats_a["passed_tests"] == 1
        assert stats_a["pass_rate"] == 100.0

        # other_user
        assert stats_b["completed_chapters"] == 3
        assert stats_b["total_answers"] == 2
        assert stats_b["correct_answers"] == 1
        assert stats_b["accuracy"] == 50.0
        assert stats_b["total_tests"] == 1
        assert stats_b["passed_tests"] == 0
        assert stats_b["pass_rate"] == 0
