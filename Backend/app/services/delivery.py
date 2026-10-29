from sqlalchemy.orm import Session

from app.models.delivery import DeliveryStaff
from app.services.whatsapp import send_whatsapp_message


def notify_delivery_boy(db: Session, restaurant_id: int, staff_id: int, order_id: int, address: str):
    staff = db.query(DeliveryStaff).filter(DeliveryStaff.id == staff_id).first()
    if not staff:
        return
    send_whatsapp_message(
        restaurant_id=restaurant_id,
        to_phone=staff.phone,
        message=f"New delivery! Order #{order_id}. Deliver to: {address}",
        db=db,
    )


def notify_customer_picked(db: Session, restaurant_id: int, customer_phone: str, order_id: int, delivery_name: str):
    send_whatsapp_message(
        restaurant_id=restaurant_id,
        to_phone=customer_phone,
        message=f"Your order #{order_id} has been picked up by {delivery_name}. On the way!",
        db=db,
    )
