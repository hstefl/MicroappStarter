import pytest
from app.models.order import Order, OrderCreate
from pydantic import ValidationError

from app.store.memory import order_db, order_db_lock


def setup_function():
    order_db.clear()


def test_order_creation_adds_to_db():
    order = OrderCreate(user_id=1, product_id=42)

    with order_db_lock:
        order_id = len(order_db) + 1
        new_order = Order(id=order_id, **order.model_dump())
        order_db[order_id] = new_order

    assert order_id in order_db
    assert order_db[order_id].user_id == 1
    assert order_db[order_id].product_id == 42


def test_order_isolation():
    order1 = Order(id=1, user_id=10, product_id=100)
    order2 = Order(id=2, user_id=11, product_id=101)

    with order_db_lock:
        order_db[1] = order1
        order_db[2] = order2

    assert order_db[1].user_id == 10
    assert order_db[2].product_id == 101


def test_order_db_reset():
    with order_db_lock:
        order_db[1] = Order(id=1, user_id=1, product_id=1)

    assert len(order_db) == 1

    order_db.clear()
    assert len(order_db) == 0


def test_order_create_valid():
    order = OrderCreate(user_id=1, product_id=42)
    assert order.user_id == 1
    assert order.product_id == 42


def test_order_create_invalid_user_id():
    with pytest.raises(ValidationError):
        OrderCreate(user_id=None, product_id=42)


def test_order_create_invalid_product_id():
    with pytest.raises(ValidationError):
        OrderCreate(user_id=1, product_id=None)


def test_order_create_both_invalid():
    with pytest.raises(ValidationError):
        OrderCreate(user_id=None, product_id=None)
