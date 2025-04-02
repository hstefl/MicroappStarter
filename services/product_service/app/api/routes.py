from threading import Lock

from fastapi import APIRouter, HTTPException

from app.models.product import Product, ProductCreate
from app.store.memory import product_db, product_stock, product_db_lock, product_stock_lock
from app.store.memory import product_stock_locks, product_stock_locks_registry_lock

router = APIRouter()


@router.post("/", response_model=Product)
def create_product(product: ProductCreate):
    with product_db_lock:
        product_id = len(product_db) + 1
        new_product = Product(id=product_id, **product.model_dump())
        product_db[product_id] = new_product

    with product_stock_lock:
        product_stock[product_id] = product.stock

    return new_product


@router.get("/{product_id}", response_model=Product)
def get_product(product_id: int):
    # Still worth locking if reads and writes can happen simultaneously
    with product_db_lock:
        product = product_db.get(product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@router.post("/{product_id}/reserve")
def reserve_product(product_id: int):
    with product_stock_lock:
        if product_id not in product_stock:
            raise HTTPException(status_code=404, detail="Product not found")

        # Ensure only one lock is created per product (thread-safe init)
        with product_stock_locks_registry_lock:
            if product_id not in product_stock_locks:
                product_stock_locks[product_id] = Lock()

        product_lock = product_stock_locks[product_id]

    with product_lock:
        with product_stock_lock:
            if product_stock[product_id] <= 0:
                raise HTTPException(status_code=409, detail="Product out of stock")
            product_stock[product_id] -= 1

    return {"message": "Product reserved", "stock": product_stock[product_id]}


@router.post("/{product_id}/release")
def release_product(product_id: int):
    with product_stock_lock:
        if product_id not in product_stock:
            raise HTTPException(status_code=404, detail="Product not found")

        product_stock[product_id] += 1
        return {"message": "Product stock restored", "stock": product_stock[product_id]}


@router.get("/{product_id}/stock")
def get_stock(product_id: int):
    with product_stock_lock:
        if product_id not in product_stock:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"product_id": product_id, "stock": product_stock[product_id]}
