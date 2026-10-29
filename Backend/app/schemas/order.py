from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class OrderItemOut(BaseModel):
    id: int
    item_name: str
    quantity: int
    price: float

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: int
    restaurant_id: int
    customer_phone: str
    customer_name: Optional[str]
    delivery_address: Optional[str]
    total_amount: float
    delivery_fee: float
    discount_amount: float
    status: str
    items: List[OrderItemOut] = []
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: str  # accepted, preparing, ready, picked, delivered, cancelled


class AssignDelivery(BaseModel):
    delivery_staff_id: int
