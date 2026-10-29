"""
Seed script: creates 1 platform admin + 3 restaurants with categories & menu items.

Run from Backend/:
    python seed.py
"""

from app.database import Base, engine, SessionLocal
from app.models.user import PlatformAdmin
from app.models.restaurant import Restaurant
from app.models.category import Category
from app.models.menu import MenuItem
from app.utils.auth import hash_password

# ensure all models are imported so create_all picks them up
import app.models  # noqa: F401


RESTAURANTS = [
    {
        "name": "Spice Garden",
        "address": "123 MG Road, Bangalore",
        "phone": "9876543210",
        "opening_time": "10:00",
        "closing_time": "23:00",
        "categories": [
            {"name": "Main Course", "icon": "🍛", "sort_order": 1, "items": [
                ("Butter Chicken", "Creamy tomato-based chicken curry", 280, False),
                ("Paneer Tikka", "Marinated cottage cheese grilled in tandoor", 220, True),
                ("Dal Makhani", "Slow-cooked black lentils in butter cream", 180, True),
                ("Chicken Biryani", "Fragrant basmati rice with spiced chicken", 250, False),
                ("Veg Biryani", "Fragrant basmati rice with mixed vegetables", 200, True),
            ]},
            {"name": "Breads", "icon": "🫓", "sort_order": 2, "items": [
                ("Garlic Naan", "Freshly baked naan with garlic", 50, True),
                ("Butter Naan", "Soft buttered naan bread", 40, True),
                ("Tandoori Roti", "Whole wheat bread from tandoor", 30, True),
            ]},
            {"name": "Sides", "icon": "🥗", "sort_order": 3, "items": [
                ("Raita", "Yogurt with cucumber and spices", 60, True),
                ("Papad", "Crispy roasted papad", 20, True),
                ("Green Salad", "Fresh seasonal salad", 50, True),
            ]},
            {"name": "Desserts", "icon": "🍰", "sort_order": 4, "items": [
                ("Gulab Jamun", "Deep-fried milk dumplings in sugar syrup", 80, True),
                ("Rasmalai", "Cottage cheese dumplings in sweet milk", 100, True),
            ]},
            {"name": "Drinks", "icon": "🍹", "sort_order": 5, "items": [
                ("Masala Chai", "Spiced Indian tea", 30, True),
                ("Lassi", "Sweet yogurt drink", 60, True),
                ("Mango Lassi", "Mango flavored yogurt drink", 80, True),
            ]},
        ],
    },
    {
        "name": "Pizza Palace",
        "address": "456 Brigade Road, Bangalore",
        "phone": "9876543211",
        "opening_time": "11:00",
        "closing_time": "23:30",
        "categories": [
            {"name": "Pizza", "icon": "🍕", "sort_order": 1, "items": [
                ("Margherita Pizza", "Classic tomato sauce and mozzarella", 250, True),
                ("Pepperoni Pizza", "Loaded with spicy pepperoni", 350, False),
                ("BBQ Chicken Pizza", "BBQ sauce with grilled chicken", 380, False),
                ("Veggie Supreme", "Loaded with fresh vegetables", 300, True),
                ("Paneer Tikka Pizza", "Indian style paneer pizza", 320, True),
            ]},
            {"name": "Snacks", "icon": "🍟", "sort_order": 2, "items": [
                ("Garlic Bread", "Crispy bread with garlic butter", 120, True),
                ("Chicken Wings", "Spicy fried chicken wings (6 pcs)", 220, False),
                ("French Fries", "Crispy golden fries", 100, True),
                ("Cheese Fries", "Fries loaded with melted cheese", 140, True),
            ]},
            {"name": "Burger", "icon": "🍔", "sort_order": 3, "items": [
                ("Classic Veg Burger", "Veggie patty with fresh lettuce", 120, True),
                ("Chicken Burger", "Crispy chicken with special sauce", 160, False),
                ("Cheese Burger", "Double cheese with grilled patty", 180, True),
            ]},
            {"name": "Desserts", "icon": "🍰", "sort_order": 4, "items": [
                ("Chocolate Brownie", "Warm fudge brownie with ice cream", 130, True),
                ("Choco Lava Cake", "Molten chocolate cake", 150, True),
            ]},
            {"name": "Drinks", "icon": "🥤", "sort_order": 5, "items": [
                ("Cold Coffee", "Iced coffee with cream", 90, True),
                ("Coca Cola", "330ml can", 40, True),
                ("Mojito", "Virgin mint mojito", 80, True),
            ]},
        ],
    },
    {
        "name": "Dragon Wok",
        "address": "789 Indiranagar, Bangalore",
        "phone": "9876543212",
        "opening_time": "12:00",
        "closing_time": "22:30",
        "categories": [
            {"name": "Rice", "icon": "🍚", "sort_order": 1, "items": [
                ("Veg Fried Rice", "Wok-tossed rice with vegetables", 180, True),
                ("Chicken Fried Rice", "Wok-tossed rice with chicken", 220, False),
                ("Schezwan Fried Rice", "Spicy Schezwan style rice", 200, True),
            ]},
            {"name": "Noodles", "icon": "🍜", "sort_order": 2, "items": [
                ("Hakka Noodles", "Stir-fried noodles with vegetables", 170, True),
                ("Chicken Noodles", "Stir-fried noodles with chicken", 210, False),
                ("Chow Mein", "Crispy fried noodles", 190, True),
            ]},
            {"name": "Starters", "icon": "🥟", "sort_order": 3, "items": [
                ("Veg Manchurian", "Crispy veg balls in spicy sauce", 190, True),
                ("Chilli Chicken", "Spicy Indo-Chinese chicken", 240, False),
                ("Spring Rolls", "Crispy rolls with veggie filling (4 pcs)", 140, True),
                ("Momos (Veg)", "Steamed dumplings (8 pcs)", 120, True),
                ("Momos (Chicken)", "Steamed dumplings (8 pcs)", 150, False),
                ("Paneer Chilli", "Crispy paneer in chilli sauce", 200, True),
            ]},
            {"name": "Soup", "icon": "🍲", "sort_order": 4, "items": [
                ("Hot & Sour Soup", "Spicy tangy vegetable soup", 100, True),
                ("Manchow Soup", "Crispy noodle topped soup", 110, True),
                ("Chicken Corn Soup", "Creamy chicken and corn soup", 120, False),
            ]},
            {"name": "Drinks", "icon": "🍹", "sort_order": 5, "items": [
                ("Iced Lemon Tea", "Refreshing cold lemon tea", 60, True),
                ("Cold Coffee", "Iced coffee with cream", 90, True),
            ]},
        ],
    },
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if db.query(PlatformAdmin).first():
            print("Database already seeded -- skipping.")
            return

        admin = PlatformAdmin(
            email="admin@foodorder.com",
            password_hash=hash_password("admin123"),
            name="Platform Admin",
        )
        db.add(admin)

        total_items = 0
        total_cats = 0
        for r_data in RESTAURANTS:
            restaurant = Restaurant(
                name=r_data["name"],
                address=r_data["address"],
                phone=r_data["phone"],
                opening_time=r_data["opening_time"],
                closing_time=r_data["closing_time"],
            )
            db.add(restaurant)
            db.flush()

            for cat_data in r_data["categories"]:
                category = Category(
                    restaurant_id=restaurant.id,
                    name=cat_data["name"],
                    icon=cat_data["icon"],
                    sort_order=cat_data["sort_order"],
                )
                db.add(category)
                db.flush()
                total_cats += 1

                for name, desc, price, is_veg in cat_data["items"]:
                    db.add(MenuItem(
                        restaurant_id=restaurant.id,
                        category_id=category.id,
                        name=name,
                        description=desc,
                        price=price,
                        category=cat_data["name"].lower(),
                        is_veg=is_veg,
                    ))
                    total_items += 1

        db.commit()
        print("Seeded successfully!")
        print(f"  Platform Admin: admin@foodorder.com / admin123")
        print(f"  Restaurants: {', '.join(r['name'] for r in RESTAURANTS)}")
        print(f"  Categories: {total_cats}")
        print(f"  Menu items: {total_items}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
