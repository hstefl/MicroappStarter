from app.models.user import UserCreate, User
from fastapi import APIRouter, HTTPException

from app.store.memory import user_db, user_db_lock

# APIRouter lets us group and manage routes cleanly
router = APIRouter()


# POST /users → Create a new user
@router.post("/", response_model=User)
def create_user(user: UserCreate):
    new_user = None

    if user_db_lock:
        # Simulate auto-incrementing ID
        user_id = len(user_db) + 1

        # Construct a full User model by adding the ID
        new_user = User(id=user_id, **user.model_dump())

        # Save to the in-memory DB (just a dict)
        user_db[user_id] = new_user

    return new_user


# GET /users/{id} → Fetch a user by ID
@router.get("/{user_id}", response_model=User)
def get_user(user_id: int):
    # Still worth locking if reads and writes can happen simultaneously
    with user_db_lock:
        user = user_db.get(user_id)

    # If not found, return 404 error
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
