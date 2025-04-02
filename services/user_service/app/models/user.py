from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr  # Automatically validates email format


class User(UserCreate):
    id: int
