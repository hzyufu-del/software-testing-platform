"""Authentication service: registration, login, user lookup."""

from app import db
from app.models import User


def get_user_by_id(user_id: int) -> User | None:
    """Return a User by primary key, or None."""
    return db.session.get(User, user_id)


def get_user_by_username(username: str) -> User | None:
    """Return a User by username, or None."""
    return User.query.filter_by(username=username).first()


def register_user(username: str, password: str, role: str = "student") -> User:
    """Create a new user with a hashed password and commit to DB.

    Raises ValueError if the username is already taken.
    """
    if get_user_by_username(username):
        raise ValueError("用户名已存在")

    user = User(username=username, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def authenticate(username: str, password: str) -> User | None:
    """Verify credentials and return the User on success, None on failure."""
    user = get_user_by_username(username)
    if user is not None and user.check_password(password):
        return user
    return None
