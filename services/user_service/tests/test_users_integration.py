from fastapi.testclient import TestClient
from app.main import app
from app.store.memory import user_db

client = TestClient(app)


def setup_function():
    # Reset in-memory DB before each test
    user_db.clear()


def test_create_user_endpoint():
    response = client.post("/users/", json={
        "name": "Integration Tester",
        "email": "test@example.com"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Integration Tester"
    assert data["email"] == "test@example.com"


def test_get_user_success():
    # First, create a user
    client.post("/users/", json={
        "name": "Fetch Me",
        "email": "fetch@example.com"
    })

    # Then fetch it
    response = client.get("/users/1")
    assert response.status_code == 200
    user = response.json()
    assert user["id"] == 1
    assert user["name"] == "Fetch Me"


def test_get_user_not_found():
    response = client.get("/users/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_create_user_invalid_email():
    response = client.post("/users/", json={
        "name": "Invalid Email",
        "email": "not-an-email"
    })

    assert response.status_code == 422  # Unprocessable Entity
    assert "value is not a valid email address" in response.text


def test_create_user_empty_name():
    response = client.post("/users/", json={
        "name": "",
        "email": "valid@example.com"
    })

    assert response.status_code == 422
    assert "String should have at least 1 character" in response.text
