from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.order import Order
from app.models.delivery import DeliveryStaff
from app.schemas.order import OrderOut, OrderStatusUpdate, AssignDelivery
from app.services.whatsapp import send_whatsapp_message
from app.utils.auth import get_current_user

router = APIRouter()


def _get_restaurant_id(user: dict) -> int:
    if user.get("role") != "restaurant_admin":
        raise HTTPException(status_code=403, detail="Restaurant admin only")
    return int(user["restaurant_id"])


@router.get("/", response_model=List[OrderOut])
def list_orders(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    rid = _get_restaurant_id(user)
    query = db.query(Order).filter(Order.restaurant_id == rid)
    if status:
        query = query.filter(Order.status == status)
    return query.order_by(Order.created_at.desc()).all()


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    rid = _get_restaurant_id(user)
    order = db.query(Order).filter(Order.id == order_id, Order.restaurant_id == rid).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.patch("/{order_id}/status", response_model=OrderOut)
def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    rid = _get_restaurant_id(user)
    order = db.query(Order).filter(Order.id == order_id, Order.restaurant_id == rid).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = data.status
    db.commit()
    db.refresh(order)

    status_messages = {
        "accepted": "Your order #{} has been accepted! The restaurant is getting it ready.",
        "preparing": "Your order #{} is being prepared!",
        "ready": "Your order #{} is ready for pickup!",
        "picked": "Your order #{} is on the way!",
        "delivered": "Your order #{} has been delivered! Thank you.",
        "cancelled": "Sorry, your order #{} has been cancelled.",
    }
    msg = status_messages.get(data.status)
    if msg:
        send_whatsapp_message(
            restaurant_id=rid,
            to_phone=order.customer_phone,
            message=msg.format(order.id),
            db=db,
        )

    return order


@router.patch("/{order_id}/assign", response_model=OrderOut)
def assign_delivery(
    order_id: int,
    data: AssignDelivery,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    rid = _get_restaurant_id(user)
    order = db.query(Order).filter(Order.id == order_id, Order.restaurant_id == rid).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    staff = db.query(DeliveryStaff).filter(
        DeliveryStaff.id == data.delivery_staff_id, DeliveryStaff.restaurant_id == rid
    ).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Delivery staff not found")

    order.delivery_staff_id = staff.id
    staff.is_available = False
    db.commit()
    db.refresh(order)

    send_whatsapp_message(
        restaurant_id=rid,
        to_phone=staff.phone,
        message=f"New delivery! Order #{order.id}. Pickup from restaurant. Deliver to: {order.delivery_address or 'N/A'}",
        db=db,
    )

    return order
