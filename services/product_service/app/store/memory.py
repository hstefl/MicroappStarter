from threading import Lock

from app.models.product import Product

product_db: dict[int, Product] = {}
product_stock: dict[int, int] = {}  # tracks live stock per product_id

product_db_lock = Lock()
product_stock_lock = Lock()

# Per-product locks to protect individual stock updates
product_stock_locks: dict[int, Lock] = {}
product_stock_locks_registry_lock = Lock()