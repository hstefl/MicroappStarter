import httpx
from app.models.order import OrderCreate, Order
from fastapi import APIRouter, HTTPException

from app.store.memory import order_db, order_db_lock

router = APIRouter()

USER_SERVICE_URL = "http://localhost:8001/users"
PRODUCT_SERVICE_URL = "http://localhost:8002/products"


@router.post("/compensating", response_model=Order)
def create_order_compensating(order: OrderCreate):
    product_reserved = False
    order_id = None

    try:
        httpx.get(f"{USER_SERVICE_URL}/{order.user_id}").raise_for_status()

        reserve_response = httpx.post(f"{PRODUCT_SERVICE_URL}/{order.product_id}/reserve")
        if reserve_response.status_code != 200:
            raise HTTPException(status_code=409, detail="Product reservation failed")
        product_reserved = True

        if order.product_id == 999:
            raise RuntimeError("Simulated DB failure")

        with order_db_lock:
            order_id = len(order_db) + 1
            new_order = Order(id=order_id, **order.model_dump())
            order_db[order_id] = new_order

        return new_order

    except Exception as e:
        if product_reserved:
            try:
                httpx.post(f"{PRODUCT_SERVICE_URL}/{order.product_id}/release")
            except Exception:
                print(f"Order failed, and rollback also failed: {e}")

        with order_db_lock:
            if order_id:
                order_db.pop(order_id, None)

        raise HTTPException(status_code=500, detail=f"Order creation failed: {str(e)}")


@router.post("/saga", response_model=Order)
def create_order_saga(order: OrderCreate):
    steps = []
    order_id = None

    try:
        # STEP 1: Verify User Exists
        httpx.get(f"{USER_SERVICE_URL}/{order.user_id}").raise_for_status()
        steps.append("user_verified")

        # STEP 2: Reserve Product Stock
        reserve_resp = httpx.post(f"{PRODUCT_SERVICE_URL}/{order.product_id}/reserve")
        if reserve_resp.status_code != 200:
            raise HTTPException(status_code=409, detail="Product reservation failed")
        steps.append("product_reserved")

        # STEP 3: Simulate failure (for testing)
        if order.product_id == 999:
            raise RuntimeError("Simulated failure after product reservation")

        # STEP 4: Create Order
        with order_db_lock:
            order_id = len(order_db) + 1
            new_order = Order(id=order_id, **order.model_dump())
            order_db[order_id] = new_order
        steps.append("order_saved")

        return new_order

    except Exception as e:
        print(f"[SAGA ERROR] Order creation failed: {e}")
        # Rollback in reverse order
        if "order_saved" in steps and order_id:
            with order_db_lock:
                order_db.pop(order_id, None)
            print(f"[SAGA ROLLBACK] Removed order ID {order_id}")

        if "product_reserved" in steps:
            try:
                httpx.post(f"{PRODUCT_SERVICE_URL}/{order.product_id}/release")
                print(f"[SAGA ROLLBACK] Released product {order.product_id}")
            except Exception as release_err:
                print(f"[SAGA ROLLBACK] Failed to release product: {release_err}")

        # No rollback needed for "user_verified" (read-only)

        raise HTTPException(
            status_code=500,
            detail=f"Order creation failed (Saga): {str(e)}"
        )


@router.get("/{order_id}", response_model=Order)
def get_order(order_id: int):
    # Still worth locking if reads and writes can happen simultaneously
    with order_db_lock:
        order = order_db.get(order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order

