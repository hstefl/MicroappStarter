from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    user_id: int = Field(..., gt=0, description="Must be a positive integer")
    product_id: int = Field(..., gt=0, description="Must be a positive integer")

class Order(OrderCreate):
    id: int
