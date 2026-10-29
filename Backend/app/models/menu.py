from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    name = Column(String(200), nullable=False)
    description = Column(String(500))
    price = Column(Float, nullable=False)
    image_url = Column(String(500))
    category = Column(String(50), default="other")
    is_veg = Column(Boolean, default=True)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    restaurant = relationship("Restaurant", back_populates="menu_items")
    category_rel = relationship("Category", back_populates="menu_items")
