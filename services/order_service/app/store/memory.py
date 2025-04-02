from app.models.order import Order
from threading import Lock

order_db: dict[int, Order] = {}
order_db_lock = Lock()
