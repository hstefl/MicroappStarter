from fastapi.testclient import TestClient

from app.main import app
from app.store.memory import product_db, product_stock

client = TestClient(app)


def setup_function():
    product_db.clear()
    product_stock.clear()


def test_create_product_endpoint():
    response = client.post("/products/", json={
        "name": "Monitor",
        "price": 150.00,
        "stock": 4
    })
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Monitor"
    assert data["stock"] == 4


def test_reserve_product_decreases_stock():
    client.post("/products/", json={"name": "Laptop", "price": 999.99, "stock": 2})
    reserve_resp = client.post("/products/1/reserve")
    assert reserve_resp.status_code == 200
    stock_resp = client.get("/products/1/stock")
    assert stock_resp.json()["stock"] == 1


def test_reserve_product_out_of_stock():
    client.post("/products/", json={"name": "USB Cable", "price": 5.00, "stock": 0})
    reserve_resp = client.post("/products/1/reserve")
    assert reserve_resp.status_code == 409
    assert "out of stock" in reserve_resp.text


def test_release_product_increases_stock():
    client.post("/products/", json={"name": "Charger", "price": 20.00, "stock": 1})
    client.post("/products/1/reserve")
    client.post("/products/1/release")
    stock_resp = client.get("/products/1/stock")
    assert stock_resp.json()["stock"] == 1


def test_create_product_with_negative_price():
    response = client.post("/products/", json={
        "name": "BadProduct",
        "price": -10.00,
        "stock": 5
    })
    assert response.status_code == 422
    assert "greater than 0" in response.text


def test_create_product_with_negative_stock():
    response = client.post("/products/", json={
        "name": "BadStock",
        "price": 10.00,
        "stock": -1
    })
    assert response.status_code == 422
    assert "greater than or equal to 0" in response.text


def test_reserve_nonexistent_product():
    response = client.post("/products/999/reserve")
    assert response.status_code == 404
    assert "Product not found" in response.text


def test_release_nonexistent_product():
    response = client.post("/products/999/release")
    assert response.status_code == 404
    assert "Product not found" in response.text


def test_get_stock_of_nonexistent_product():
    response = client.get("/products/999/stock")
    assert response.status_code == 404
    assert "Product not found" in response.text
