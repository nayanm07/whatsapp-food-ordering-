from pydantic import BaseModel
from typing import Optional


class RestaurantCreate(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    logo_url: Optional[str] = None


class RestaurantWhatsAppConfig(BaseModel):
    whatsapp_phone_number_id: str
    whatsapp_access_token: str


class RestaurantUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    logo_url: Optional[str] = None
    free_delivery_distance_km: Optional[float] = None
    delivery_charge_per_km: Optional[float] = None
    opening_time: Optional[str] = None
    closing_time: Optional[str] = None
    is_active: Optional[bool] = None


class RestaurantOut(BaseModel):
    id: int
    name: str
    address: Optional[str]
    phone: Optional[str]
    logo_url: Optional[str]
    whatsapp_phone_number_id: Optional[str]
    free_delivery_distance_km: float
    delivery_charge_per_km: float
    opening_time: str
    closing_time: str
    is_active: bool

    class Config:
        from_attributes = True
