import pytest
from app.models.user import User, UserCreate
from app.api.routes import create_user, get_user
from app.store.memory import user_db


def setup_function():
    # Reset the in-memory DB before each test
    user_db.clear()


def test_create_user():
    user_data = UserCreate(name="Test User", email="test@example.com")
    new_user = create_user(user_data)

    assert new_user.id == 1
    assert new_user.name == "Test User"
    assert new_user.email == "test@example.com"
    assert user_db[1] == new_user


def test_get_user_success():
    # Arrange: create a user first
    user = create_user(UserCreate(name="Jane", email="jane@example.com"))

    # Act
    fetched = get_user(user.id)

    # Assert
    assert fetched.id == user.id
    assert fetched.name == "Jane"


def test_get_user_not_found():
    with pytest.raises(Exception) as exc_info:
        get_user(999)  # user doesn't exist

    assert exc_info.value.status_code == 404
    assert "User not found" in str(exc_info.value.detail)
