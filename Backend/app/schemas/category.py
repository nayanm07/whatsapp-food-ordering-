from pydantic import BaseModel
from typing import Optional


class CategoryCreate(BaseModel):
    name: str
    icon: str = "🍽️"
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryOut(BaseModel):
    id: int
    restaurant_id: int
    name: str
    icon: str
    sort_order: int
    is_active: bool

    class Config:
        from_attributes = True
