from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    customer_name = Column(String(200))
    delivery_address = Column(String(500))
    delivery_lat = Column(Float)
    delivery_lng = Column(Float)

    total_amount = Column(Float, default=0)
    delivery_fee = Column(Float, default=0)
    discount_amount = Column(Float, default=0)

    status = Column(String(20), default="placed")
    # placed → accepted → preparing → ready → picked → delivered / cancelled

    delivery_staff_id = Column(Integer, ForeignKey("delivery_staff.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    restaurant = relationship("Restaurant", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    delivery_boy = relationship("DeliveryStaff")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    item_name = Column(String(200), nullable=False)
    quantity = Column(Integer, default=1)
    price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem")
