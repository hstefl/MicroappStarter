import pytest

from app.api.routes import create_product, get_product
from app.models.product import ProductCreate
from app.store.memory import product_db, product_stock


def setup_function():
    # Reset the in-memory store before each test
    product_db.clear()
    product_stock.clear()


def test_create_product_stores_data_correctly():
    product_data = ProductCreate(name="Keyboard", price=49.99, stock=5)
    product = create_product(product_data)

    assert product.id == 1
    assert product.name == "Keyboard"
    assert product.price == 49.99
    assert product.stock == 5
    assert product_db[1].id == 1
    assert product_stock[1] == 5


def test_get_product_returns_correct_data():
    product = create_product(ProductCreate(name="Mouse", price=25.00, stock=10))
    fetched = get_product(product.id)

    assert fetched.id == product.id
    assert fetched.name == "Mouse"
    assert fetched.stock == 10


def test_get_product_not_found():
    with pytest.raises(Exception) as exc_info:
        get_product(999)  # This product doesn't exist

    assert exc_info.value.status_code == 404
    assert "Product not found" in str(exc_info.value.detail)
