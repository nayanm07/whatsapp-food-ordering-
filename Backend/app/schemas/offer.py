from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class OfferCreate(BaseModel):
    title: str
    discount_percent: float
    min_order_amount: float = 0
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None


class OfferUpdate(BaseModel):
    title: Optional[str] = None
    discount_percent: Optional[float] = None
    min_order_amount: Optional[float] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: Optional[bool] = None


class OfferOut(BaseModel):
    id: int
    restaurant_id: int
    title: str
    discount_percent: float
    min_order_amount: float
    valid_from: Optional[datetime]
    valid_until: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True
