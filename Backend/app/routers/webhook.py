import logging
import time

from fastapi import APIRouter, Request, HTTPException, Response

from app.config import settings
from app.database import SessionLocal
from app.models.restaurant import Restaurant
from app.services.chatbot import handle_customer_message
from app.services.whatsapp import send_whatsapp_message

logger = logging.getLogger(__name__)
router = APIRouter()

# Simple in-memory dedup: message_id -> timestamp
_processed_messages: dict[str, float] = {}
DEDUP_TTL = 60


def _is_duplicate(message_id: str) -> bool:
    now = time.time()
    # Clean old entries
    expired = [k for k, v in _processed_messages.items() if now - v > DEDUP_TTL]
    for k in expired:
        del _processed_messages[k]
    if message_id in _processed_messages:
        return True
    _processed_messages[message_id] = now
    return False


@router.get("/whatsapp")
def verify_webhook(request: Request):
    params = dict(request.query_params)
    hub_mode = params.get("hub.mode") or params.get("hub_mode")
    hub_verify_token = params.get("hub.verify_token") or params.get("hub_verify_token")
    hub_challenge = params.get("hub.challenge") or params.get("hub_challenge")

    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        return Response(content=hub_challenge, media_type="text/plain")
    raise HTTPException(status_code=403, detail="Verification failed")


def _extract_message_text(message: dict) -> str | None:
    msg_type = message.get("type")
    if msg_type == "text":
        return message["text"]["body"]
    if msg_type == "interactive":
        interactive = message.get("interactive", {})
        if interactive.get("type") == "button_reply":
            return interactive["button_reply"]["id"]
        if interactive.get("type") == "list_reply":
            return interactive["list_reply"]["id"]
    if msg_type == "location":
        loc = message.get("location", {})
        lat = loc.get("latitude")
        lng = loc.get("longitude")
        name = loc.get("name", "")
        addr = loc.get("address", "")
        return f"LOCATION:{lat},{lng}|{name}|{addr}"
    return None


@router.post("/whatsapp")
async def receive_whatsapp(request: Request):
    body = await request.json()

    try:
        entry = body["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        if "messages" not in value:
            return {"status": "no message"}

        phone_number_id = value["metadata"]["phone_number_id"]
        message = value["messages"][0]
        from_phone = message["from"]
        message_id = message.get("id", "")

        if message_id and _is_duplicate(message_id):
            logger.info(f"Duplicate message {message_id} — skipping")
            return {"status": "duplicate"}

        logger.info(f"Message from {from_phone}, type={message.get('type')}, id={message_id}")

        message_text = _extract_message_text(message)
        if not message_text:
            db = SessionLocal()
            try:
                restaurant = (
                    db.query(Restaurant)
                    .filter(Restaurant.whatsapp_phone_number_id == phone_number_id)
                    .first()
                )
                if restaurant:
                    send_whatsapp_message(
                        restaurant_id=restaurant.id,
                        to_phone=from_phone,
                        message="Sorry, abhi hum sirf text messages samajh sakte hain. Please apna order type karein. 🙏",
                        db=db,
                    )
            finally:
                db.close()
            return {"status": "unsupported type"}

        logger.info(f"Parsed: {message_text[:100]}")

        db = SessionLocal()
        try:
            restaurant = (
                db.query(Restaurant)
                .filter(Restaurant.whatsapp_phone_number_id == phone_number_id)
                .first()
            )
            if not restaurant:
                logger.warning(f"No restaurant for phone_number_id={phone_number_id}")
                return {"status": "restaurant not found"}

            logger.info(f"Restaurant: {restaurant.name} (id={restaurant.id})")
            try:
                reply = handle_customer_message(db, restaurant.id, from_phone, message_text)
                logger.info(f"Reply: {reply[:100]}")
            except Exception as ai_err:
                logger.error(f"AI error: {ai_err}")
                reply = "Sorry, abhi kuch technical problem aa rahi hai. Thodi der baad try karein. 🙏"

            send_whatsapp_message(
                restaurant_id=restaurant.id,
                to_phone=from_phone,
                message=reply,
                db=db,
            )
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)

    return {"status": "ok"}
