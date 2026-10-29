from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class PlatformAdmin(Base):
    __tablename__ = "platform_admins"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(200), unique=True, nullable=False)
    password_hash = Column(String(500), nullable=False)
    name = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class RestaurantAdmin(Base):
    __tablename__ = "restaurant_admins"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(500), nullable=False)
    name = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    restaurant = relationship("Restaurant", back_populates="admins")
