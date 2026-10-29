from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    title = Column(String(200), nullable=False)
    discount_percent = Column(Float, nullable=False)
    min_order_amount = Column(Float, default=0)
    valid_from = Column(DateTime(timezone=True))
    valid_until = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    restaurant = relationship("Restaurant", back_populates="offers")
