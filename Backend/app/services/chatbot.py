import json
from openai import OpenAI
from sqlalchemy.orm import Session

from app.config import settings
from app.models.category import Category
from app.models.menu import MenuItem
from app.models.session import CustomerSession
from app.models.order import Order, OrderItem
from app.models.restaurant import Restaurant
from app.services.whatsapp import (
    send_interactive_list,
    send_interactive_buttons,
    send_location_request,
)

client = OpenAI(api_key=settings.OPENAI_API_KEY)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "show_menu",
            "description": "Show the restaurant menu to the customer as an interactive list they can tap to select items",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Filter by category: veg, non-veg, drinks, desserts, snacks, or all",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_to_cart",
            "description": "Add a menu item to the customer's cart",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_name": {"type": "string", "description": "Name of the menu item"},
                    "quantity": {"type": "integer", "description": "Number of items to add"},
                },
                "required": ["item_name", "quantity"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remove_from_cart",
            "description": "Remove an item from the customer's cart",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_name": {"type": "string", "description": "Name of the item to remove"},
                },
                "required": ["item_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "view_cart",
            "description": "Show what is currently in the customer's cart with total",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "place_order",
            "description": "Confirm and place the order from the cart",
            "parameters": {
                "type": "object",
                "properties": {
                    "delivery_address": {"type": "string", "description": "Delivery address"},
                    "customer_name": {"type": "string", "description": "Customer name"},
                },
                "required": ["delivery_address", "customer_name"],
            },
        },
    },
]


class InteractiveAction:
    def __init__(self, action_type: str, **kwargs):
        self.action_type = action_type
        self.kwargs = kwargs


def get_or_create_session(db: Session, restaurant_id: int, customer_phone: str) -> CustomerSession:
    session = (
        db.query(CustomerSession)
        .filter(
            CustomerSession.restaurant_id == restaurant_id,
            CustomerSession.customer_phone == customer_phone,
        )
        .first()
    )
    if not session:
        session = CustomerSession(
            restaurant_id=restaurant_id,
            customer_phone=customer_phone,
            cart=[],
            conversation_history=[],
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    return session


def build_system_prompt(restaurant: Restaurant, menu_items: list, cart: list) -> str:
    menu_text = "\n".join(
        f"- {item.name} (₹{item.price}) [{item.category}] {'🟢 Veg' if item.is_veg else '🔴 Non-Veg'}"
        for item in menu_items
        if item.is_available
    )
    cart_text = "\n".join(
        f"- {c['name']} x{c['qty']} = ₹{c['price'] * c['qty']}" for c in cart
    ) if cart else "Empty"
    total = sum(c["price"] * c["qty"] for c in cart)

    return f"""You are a friendly food ordering assistant for {restaurant.name}.
You help customers browse the menu, add items to cart, and place orders through WhatsApp.

MENU:
{menu_text}

CURRENT CART:
{cart_text}
Cart Total: ₹{total}

LANGUAGE:
- Always respond in Hinglish (Hindi written in English script mixed with English words)
- Example: "Namaste! 🙏 Aapka order ready hai. Kya aap aur kuch add karna chahenge?"
- Use Hindi for conversational parts, English for item names and prices
- Keep it natural and friendly, like talking to a friend on WhatsApp

RULES:
- Be friendly and use short messages (WhatsApp style)
- Always use the tools to perform actions
- If customer asks for an item not on the menu, politely say it's not available
- When adding to cart, match the item name to the closest menu item
- After adding items, ask if they want to add more or place the order
- Before placing order, ask for delivery address and name if not provided
- Use ₹ for prices
- When customer sends a location, extract the address for delivery
- When customer selects an item from menu list (like "item_3"), add 1 of that item
- When customer clicks a button reply, handle it naturally"""


def _build_category_list(db_categories, menu_items, restaurant_name: str):
    cat_item_counts = {}
    cat_previews = {}
    for item in menu_items:
        if item.is_available and item.category_id:
            cat_item_counts[item.category_id] = cat_item_counts.get(item.category_id, 0) + 1
            cat_previews.setdefault(item.category_id, []).append(item.name)

    rows = []
    for cat in sorted(db_categories, key=lambda c: c.sort_order):
        if not cat.is_active:
            continue
        count = cat_item_counts.get(cat.id, 0)
        if count == 0:
            continue
        preview = ", ".join(cat_previews.get(cat.id, [])[:3])
        rows.append({
            "id": f"cat_{cat.id}",
            "title": f"{cat.icon} {cat.name} ({count})"[:24],
            "description": preview[:72],
        })

    if not rows:
        return None

    return InteractiveAction(
        "list",
        body_text=f"{restaurant_name} mein aapka swagat hai! 🙏 Category choose karein aur menu dekhein.",
        button_label="Menu Dekhein 🍽️",
        sections=[{"title": "Menu Categories", "rows": rows[:10]}],
        header=f"📋 {restaurant_name}",
        footer="Category tap karein",
    )


def _build_items_list(items, category_name: str, category_icon: str = "🍽️"):
    label = f"{category_icon} {category_name}"
    rows = [
        {
            "id": f"item_{i.id}",
            "title": i.name[:24],
            "description": f"₹{int(i.price)} - {(i.description or '')[:48]}",
        }
        for i in items[:10]
    ]
    return InteractiveAction(
        "list",
        body_text=f"Item tap karein cart mein add karne ke liye!",
        button_label=f"{label[:17]} ▶",
        sections=[{"title": label[:24], "rows": rows}],
        footer="Item select karein",
    )


def execute_tool(tool_name: str, args: dict, session: CustomerSession, db: Session):
    menu_items = (
        db.query(MenuItem)
        .filter(MenuItem.restaurant_id == session.restaurant_id, MenuItem.is_available == True)
        .all()
    )
    cart = session.cart or []

    if tool_name == "show_menu":
        category = args.get("category", "all")
        restaurant = db.query(Restaurant).filter(Restaurant.id == session.restaurant_id).first()
        r_name = restaurant.name if restaurant else "Menu"
        db_categories = (
            db.query(Category)
            .filter(Category.restaurant_id == session.restaurant_id, Category.is_active == True)
            .order_by(Category.sort_order)
            .all()
        )

        if category == "all":
            action = _build_category_list(db_categories, menu_items, r_name)
            lines = []
            for cat in db_categories:
                cat_items = [i for i in menu_items if i.category_id == cat.id and i.is_available]
                if cat_items:
                    lines.append(f"\n{cat.icon} {cat.name}:")
                    for i in cat_items:
                        lines.append(f"  {'🟢' if i.is_veg else '🔴'} {i.name} — ₹{int(i.price)}")
            return "\n".join(lines) if lines else "No menu items available.", action
        else:
            try:
                cat_id = int(category)
                cat = db.query(Category).filter(Category.id == cat_id).first()
            except ValueError:
                cat = db.query(Category).filter(
                    Category.restaurant_id == session.restaurant_id,
                    Category.name.ilike(f"%{category}%"),
                ).first()

            if not cat:
                return "Category not found.", None
            items = [i for i in menu_items if i.category_id == cat.id and i.is_available]
            if not items:
                return "No items in this category.", None
            action = _build_items_list(items, cat.name, cat.icon)
            lines = [f"{'🟢' if i.is_veg else '🔴'} {i.name} — ₹{int(i.price)}" for i in items]
            return "\n".join(lines), action

    elif tool_name == "add_to_cart":
        item_name = args["item_name"].lower()
        qty = args.get("quantity", 1)

        if item_name.startswith("item_"):
            item_id = int(item_name.replace("item_", ""))
            match = next((i for i in menu_items if i.id == item_id), None)
        else:
            match = next((i for i in menu_items if item_name in i.name.lower()), None)

        if not match:
            return f"Sorry, '{args['item_name']}' is not on the menu.", None

        for c in cart:
            if c["item_id"] == match.id:
                c["qty"] += qty
                session.cart = cart
                db.commit()
                total = sum(c["price"] * c["qty"] for c in cart)
                return f"Updated {match.name} to {c['qty']}x. Cart total: ₹{int(total)}", "cart_updated"
        cart.append({"item_id": match.id, "name": match.name, "qty": qty, "price": match.price})
        session.cart = cart
        db.commit()
        total = sum(c["price"] * c["qty"] for c in cart)
        return f"Added {qty}x {match.name} (₹{int(match.price)}). Cart total: ₹{int(total)}", "cart_updated"

    elif tool_name == "remove_from_cart":
        item_name = args["item_name"].lower()
        for c in cart:
            if item_name in c["name"].lower():
                cart.remove(c)
                session.cart = cart
                db.commit()
                return f"Removed {c['name']} from cart.", "cart_updated"
        return "Item not found in cart.", None

    elif tool_name == "view_cart":
        if not cart:
            return "Aapka cart khali hai. Menu se items add karein!", None
        lines = [f"{c['name']} x{c['qty']} = ₹{int(c['price'] * c['qty'])}" for c in cart]
        total = sum(c["price"] * c["qty"] for c in cart)
        lines.append(f"\nTotal: ₹{int(total)}")
        return "\n".join(lines), "view_cart"

    elif tool_name == "place_order":
        if not cart:
            return "Aapka cart khali hai. Pehle items add karein!", None
        total = sum(c["price"] * c["qty"] for c in cart)
        order = Order(
            restaurant_id=session.restaurant_id,
            customer_phone=session.customer_phone,
            customer_name=args.get("customer_name"),
            delivery_address=args.get("delivery_address"),
            total_amount=total,
            status="placed",
        )
        db.add(order)
        db.flush()
        for c in cart:
            db.add(OrderItem(
                order_id=order.id,
                menu_item_id=c["item_id"],
                item_name=c["name"],
                quantity=c["qty"],
                price=c["price"],
            ))
        session.cart = []
        session.conversation_history = []
        db.commit()
        return f"Order #{order.id} place ho gaya! 🎉 Total: ₹{int(total)}. Aapko updates yahi milenge.", "order_placed"

    return "Unknown action.", None


def _build_cart_summary_action(cart: list):
    lines = [f"{c['name']} x{c['qty']} = ₹{int(c['price'] * c['qty'])}" for c in cart]
    total = sum(c["price"] * c["qty"] for c in cart)
    cart_text = "\n".join(lines)
    return InteractiveAction(
        "buttons",
        body_text=f"🛒 *Aapka Cart:*\n{cart_text}\n\n*Total: ₹{int(total)}*\n\nKya karna chahenge?",
        buttons=[
            {"id": "btn_menu", "title": "Aur Add Karein"},
            {"id": "btn_cart", "title": "Cart Dekhein"},
            {"id": "btn_order", "title": "Order Karein ✅"},
        ],
    )


def handle_customer_message(db: Session, restaurant_id: int, customer_phone: str, message: str) -> str:
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        return "Restaurant not found."

    menu_items = (
        db.query(MenuItem)
        .filter(MenuItem.restaurant_id == restaurant_id, MenuItem.is_available == True)
        .all()
    )

    session = get_or_create_session(db, restaurant_id, customer_phone)
    history = session.conversation_history or []

    if message.startswith("item_"):
        item_id = int(message.replace("item_", ""))
        match = next((i for i in menu_items if i.id == item_id), None)
        if match:
            message = f"Add 1 {match.name} to my cart"

    if message.startswith("cat_"):
        cat_id = message.replace("cat_", "")
        cat = db.query(Category).filter(Category.id == int(cat_id)).first() if cat_id.isdigit() else None
        if cat:
            message = f"Show me the {cat.name} menu"
        else:
            message = f"Show me the {cat_id} menu"

    if message == "btn_menu":
        message = "Show me the menu"
    elif message == "btn_cart":
        message = "Show my cart"
    elif message == "btn_order":
        cart = session.cart or []
        if cart:
            lines = [f"{c['name']} x{c['qty']} = ₹{int(c['price'] * c['qty'])}" for c in cart]
            total = sum(c["price"] * c["qty"] for c in cart)
            cart_text = "\n".join(lines)
            send_interactive_buttons(
                restaurant_id=restaurant_id,
                to_phone=customer_phone,
                body_text=f"📋 *Order Summary:*\n{cart_text}\n\n*Total: ₹{int(total)}*\n\nConfirm karne ke liye apna location aur naam share karein.",
                buttons=[
                    {"id": "btn_menu", "title": "Aur Add Karein"},
                    {"id": "btn_cart", "title": "Cart Dekhein"},
                ],
                db=db,
            )
            send_location_request(
                restaurant_id=restaurant_id,
                to_phone=customer_phone,
                body_text="📍 Order place karne ke liye apna delivery location share karein!",
                db=db,
            )
            history = session.conversation_history or []
            history.append({"role": "user", "content": "I want to place my order"})
            history.append({"role": "assistant", "content": "Order place karne ke liye apna delivery location aur naam share karein."})
            if len(history) > 30:
                history = history[-20:]
            session.conversation_history = history
            db.commit()
            return "Order place karne ke liye apna delivery location aur naam share karein."
        message = "I want to place my order"

    if message.startswith("LOCATION:"):
        parts = message.replace("LOCATION:", "").split("|")
        coords = parts[0] if len(parts) > 0 else ""
        name = parts[1] if len(parts) > 1 else ""
        addr = parts[2] if len(parts) > 2 else ""
        location_text = addr or name or coords
        if session.cart:
            message = f"My delivery location is: {location_text}. Coordinates: {coords}"
        else:
            message = f"My location is: {location_text}"

    system_prompt = build_system_prompt(restaurant, menu_items, session.cart or [])
    history.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "system", "content": system_prompt}] + history,
        tools=TOOLS,
        tool_choice="auto",
    )

    assistant_message = response.choices[0].message
    tool_signals = []
    menu_action = None

    if assistant_message.tool_calls:
        history.append(assistant_message.model_dump())
        for tool_call in assistant_message.tool_calls:
            fn_name = tool_call.function.name
            fn_args = json.loads(tool_call.function.arguments)
            result, signal = execute_tool(fn_name, fn_args, session, db)
            if isinstance(signal, InteractiveAction):
                menu_action = signal
            elif signal:
                tool_signals.append(signal)
            history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

        followup = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "system", "content": system_prompt}] + history,
        )
        reply = followup.choices[0].message.content
        history.append({"role": "assistant", "content": reply})
    else:
        reply = assistant_message.content
        history.append({"role": "assistant", "content": reply})

    # Send ONE interactive message at the end based on what happened
    if menu_action:
        send_interactive_list(
            restaurant_id=restaurant_id,
            to_phone=customer_phone,
            body_text=menu_action.kwargs["body_text"],
            button_label=menu_action.kwargs["button_label"],
            sections=menu_action.kwargs["sections"],
            db=db,
            header=menu_action.kwargs.get("header"),
            footer=menu_action.kwargs.get("footer"),
        )
    elif "cart_updated" in tool_signals or "view_cart" in tool_signals:
        cart = session.cart or []
        if cart:
            action = _build_cart_summary_action(cart)
            send_interactive_buttons(
                restaurant_id=restaurant_id,
                to_phone=customer_phone,
                body_text=action.kwargs["body_text"],
                buttons=action.kwargs["buttons"],
                db=db,
            )
    elif "place_order_request" in tool_signals:
        send_location_request(
            restaurant_id=restaurant_id,
            to_phone=customer_phone,
            body_text="📍 Apna delivery location share karein taaki hum order deliver kar sakein!",
            db=db,
        )

    if len(history) > 30:
        history = history[-20:]
    session.conversation_history = history
    db.commit()

    return reply
