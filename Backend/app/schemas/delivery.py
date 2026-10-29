from pydantic import BaseModel
from typing import Optional


class DeliveryStaffCreate(BaseModel):
    name: str
    phone: str


class DeliveryStaffOut(BaseModel):
    id: int
    restaurant_id: int
    name: str
    phone: str
    is_available: bool

    class Config:
        from_attributes = True
