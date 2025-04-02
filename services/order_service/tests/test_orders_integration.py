import time
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient
from python_on_whales import DockerClient

from app.main import app
from app.store.memory import order_db

client = TestClient(app)

USER_SERVICE_URL = "http://localhost:8001/users"
PRODUCT_SERVICE_URL = "http://localhost:8002/products"
COMPOSE_FILE = str(Path(__file__).resolve().parent) + "/docker-compose.test.yml"


@pytest.fixture(scope="session", autouse=True)
def test_environment():
    # Start Docker Compose
    docker = DockerClient(compose_files=[COMPOSE_FILE])
    docker.compose.build()
    docker.compose.up(detach=True)

    # Wait for /health endpoints
    assert wait_for_service("http://localhost:8001/health"), "User service not ready"
    assert wait_for_service("http://localhost:8002/health"), "Product service not ready"

    yield  # Run the tests

    # Teardown Docker Compose
    docker.compose.down()


@pytest.fixture(autouse=True)
def reset_order_db():
    order_db.clear()
    
    # Create default test data before each test
    response1 = httpx.post(USER_SERVICE_URL, follow_redirects=True, json={
        "name": "Test User",
        "email": "testuser@example.com"
    })
    response2 = httpx.post(PRODUCT_SERVICE_URL, follow_redirects=True, json={
        "name": "Test Product",
        "price": 100.0,
        "stock": 5
    })


def test_create_order_compensating_success():
    response = client.post("/orders/compensating", json={
        "user_id": 1,
        "product_id": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["user_id"] == 1
    assert data["product_id"] == 1


def test_create_order_compensating_failure_and_rollback():
    response = client.post("/orders/compensating", json={
        "user_id": 1,
        "product_id": 999
    })
    assert response.status_code == 500
    assert "failed" in response.json()["detail"].lower()


def test_create_order_saga_success():
    response = client.post("/orders/saga", json={
        "user_id": 1,
        "product_id": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["user_id"] == 1
    assert data["product_id"] == 1


def test_create_order_saga_failure_and_rollback():
    response = client.post("/orders/saga", json={
        "user_id": 1,
        "product_id": 999
    })
    assert response.status_code == 500
    assert "failed" in response.json()["detail"].lower()


def wait_for_service(url: str, timeout: int = 2, retries: int = 15) -> bool:
    for _ in range(retries):
        try:
            response = httpx.get(url, timeout=timeout)
            if response.status_code < 500:
                return True
        except httpx.RequestError:
            time.sleep(1)
    return False
