from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    address = Column(String(500))
    phone = Column(String(20))
    logo_url = Column(String(500))

    whatsapp_phone_number_id = Column(String(100), unique=True)
    whatsapp_access_token = Column(String(500))

    free_delivery_distance_km = Column(Float, default=3.0)
    delivery_charge_per_km = Column(Float, default=10.0)
    opening_time = Column(String(10), default="09:00")
    closing_time = Column(String(10), default="22:00")

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    categories = relationship("Category", back_populates="restaurant")
    menu_items = relationship("MenuItem", back_populates="restaurant")
    orders = relationship("Order", back_populates="restaurant")
    delivery_staff = relationship("DeliveryStaff", back_populates="restaurant")
    offers = relationship("Offer", back_populates="restaurant")
    admins = relationship("RestaurantAdmin", back_populates="restaurant")
