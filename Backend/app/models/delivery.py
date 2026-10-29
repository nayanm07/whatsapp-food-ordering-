from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class DeliveryStaff(Base):
    __tablename__ = "delivery_staff"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    name = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=False)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    restaurant = relationship("Restaurant", back_populates="delivery_staff")
