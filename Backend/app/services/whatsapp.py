import logging
import httpx
from sqlalchemy.orm import Session

from app.models.restaurant import Restaurant

logger = logging.getLogger(__name__)


def _get_restaurant_api(db: Session, restaurant_id: int):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant or not restaurant.whatsapp_phone_number_id:
        return None, None, None
    url = f"https://graph.facebook.com/v21.0/{restaurant.whatsapp_phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {restaurant.whatsapp_access_token}",
        "Content-Type": "application/json",
    }
    return url, headers, restaurant


def _send(url: str, headers: dict, payload: dict):
    try:
        response = httpx.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        logger.error(f"WhatsApp API error: {e}")
        return None


def send_whatsapp_message(restaurant_id: int, to_phone: str, message: str, db: Session):
    url, headers, restaurant = _get_restaurant_api(db, restaurant_id)
    if not url:
        return
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {"body": message},
    }
    _send(url, headers, payload)


def send_interactive_buttons(restaurant_id: int, to_phone: str, body_text: str,
                              buttons: list[dict], db: Session, header: str = None, footer: str = None):
    url, headers, restaurant = _get_restaurant_api(db, restaurant_id)
    if not url:
        return
    interactive = {
        "type": "button",
        "body": {"text": body_text},
        "action": {
            "buttons": [
                {"type": "reply", "reply": {"id": btn["id"], "title": btn["title"][:20]}}
                for btn in buttons[:3]
            ]
        },
    }
    if header:
        interactive["header"] = {"type": "text", "text": header}
    if footer:
        interactive["footer"] = {"text": footer}
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "interactive",
        "interactive": interactive,
    }
    _send(url, headers, payload)


def send_interactive_list(restaurant_id: int, to_phone: str, body_text: str,
                           button_label: str, sections: list[dict], db: Session,
                           header: str = None, footer: str = None):
    url, headers, restaurant = _get_restaurant_api(db, restaurant_id)
    if not url:
        return
    interactive = {
        "type": "list",
        "body": {"text": body_text},
        "action": {
            "button": button_label[:20],
            "sections": sections,
        },
    }
    if header:
        interactive["header"] = {"type": "text", "text": header}
    if footer:
        interactive["footer"] = {"text": footer}
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "interactive",
        "interactive": interactive,
    }
    _send(url, headers, payload)


def send_location_request(restaurant_id: int, to_phone: str, body_text: str, db: Session):
    url, headers, restaurant = _get_restaurant_api(db, restaurant_id)
    if not url:
        return
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "interactive",
        "interactive": {
            "type": "location_request_message",
            "body": {"text": body_text},
            "action": {"name": "send_location"},
        },
    }
    _send(url, headers, payload)
