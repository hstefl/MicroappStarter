from pydantic import BaseModel


class OrderCreate(BaseModel):
    user_id: int
    product_id: int

class Order(OrderCreate):
    id: int
