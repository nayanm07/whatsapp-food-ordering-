from pydantic import BaseModel
from typing import Optional


class MenuItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    category_id: Optional[int] = None
    category: str = "other"
    is_veg: bool = True


class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    category_id: Optional[int] = None
    category: Optional[str] = None
    is_veg: Optional[bool] = None
    is_available: Optional[bool] = None


class MenuItemOut(BaseModel):
    id: int
    restaurant_id: int
    category_id: Optional[int]
    name: str
    description: Optional[str]
    price: float
    image_url: Optional[str]
    category: str
    is_veg: bool
    is_available: bool

    class Config:
        from_attributes = True
