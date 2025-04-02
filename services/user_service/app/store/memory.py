from threading import Lock

from app.models.user import User

# In-memory dictionary simulating a user table (user_id → User)
user_db: dict[int, User] = {}
user_db_lock = Lock()
