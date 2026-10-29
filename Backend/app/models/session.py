from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func

from app.database import Base


class CustomerSession(Base):
    __tablename__ = "customer_sessions"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    cart = Column(JSON, default=list)  # [{"item_id": 1, "name": "...", "qty": 2, "price": 250}]
    conversation_history = Column(JSON, default=list)  # OpenAI messages format
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
