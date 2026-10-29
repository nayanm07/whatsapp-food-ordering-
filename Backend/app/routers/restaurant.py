from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.category import Category
from app.models.menu import MenuItem
from app.models.delivery import DeliveryStaff
from app.models.offer import Offer
from app.models.restaurant import Restaurant
from app.models.user import RestaurantAdmin
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut
from app.schemas.menu import MenuItemCreate, MenuItemUpdate, MenuItemOut
from app.schemas.delivery import DeliveryStaffCreate, DeliveryStaffOut
from app.schemas.offer import OfferCreate, OfferUpdate, OfferOut
from app.schemas.restaurant import RestaurantUpdate, RestaurantOut
from app.schemas.user import RestaurantAdminLogin, TokenOut
from app.utils.auth import verify_password, create_token, get_current_user

router = APIRouter()


def _get_restaurant_id(user: dict) -> int:
    if user.get("role") != "restaurant_admin":
        raise HTTPException(status_code=403, detail="Restaurant admin only")
    return int(user["restaurant_id"])


# --- Auth ---

@router.post("/login", response_model=TokenOut)
def restaurant_login(data: RestaurantAdminLogin, db: Session = Depends(get_db)):
    admin = db.query(RestaurantAdmin).filter(RestaurantAdmin.phone == data.phone).first()
    if not admin or not verify_password(data.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({
        "sub": str(admin.id),
        "role": "restaurant_admin",
        "restaurant_id": admin.restaurant_id,
    })
    return {"access_token": token}


# --- Categories ---

@router.get("/categories", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    rid = _get_restaurant_id(user)
    return db.query(Category).filter(Category.restaurant_id == rid).order_by(Category.sort_order).all()


@router.post("/categories", response_model=CategoryOut)
def create_category(data: CategoryCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    rid = _get_restaurant_id(user)
    cat = Category(restaurant_id=rid, **data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.put("/categories/{cat_id}", response_model=CategoryOut)
def update_category(cat_id: int, data: CategoryUpdate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    rid = _get_restaurant_id(user)
    cat = db.query(Category).filter(Category.id == cat_id, Category.restaurant_id == rid).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(cat, key, value)
    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/categories/{cat_id}")
def delete_category(cat_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    rid = _get_restaurant_id(user)
    cat = db.query(Category).filter(Category.id == cat_id, Category.restaurant_id == rid).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(cat)
    db.commit()
    return {"detail": "Deleted"}


# --- Menu ---

@router.get("/menu", response_model=List[MenuItemOut])
def list_menu(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    rid = _get_restaurant_id(user)
    return db.query(MenuItem).filter(MenuItem.restaurant_id == rid).all()


@router.post("/menu", response_model=MenuItemOut)
def add_menu_item(data: MenuItemCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    rid = _get_restaurant_id(user)
    item = MenuItem(restaurant_id=rid, **data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/menu/{item_id}", response_model=MenuItemOut)
def update_menu_item(item_id: int, data: MenuItemUpdate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    rid = _get_restaurant_id(user)
    item = db.query(MenuItem).filter(MenuItem.id == item_id, MenuItem.restaurant_id == rid).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/menu/{item_id}")
def delete_menu_item(item_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    rid = _get_restaurant_id(user)
    item = db.query(MenuItem).filter(MenuItem.id == item_id, MenuItem.restaurant_id == rid).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    db.delete(item)
    db.commit()
    return {"detail": "Deleted"}


# --- Delivery Staff ---

@router.get("/delivery-staff", response_model=List[DeliveryStaffOut])
def list_delivery_staff(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    rid = _get_restaurant_id(user)
    return db.query(DeliveryStaff).filter(DeliveryStaff.restaurant_id == rid).all()


@router.post("/delivery-staff", response_model=DeliveryStaffOut)
def add_delivery_staff(data: DeliveryStaffCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    rid = _get_restaurant_id(user)
    staff = DeliveryStaff(restaurant_id=rid, **data.model_dump())
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return staff


# --- Offers ---

@router.get("/offers", response_model=List[OfferOut])
def list_offers(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    rid = _get_restaurant_id(user)
    return db.query(Offer).filter(Offer.restaurant_id == rid).all()


@router.post("/offers", response_model=OfferOut)
def create_offer(data: OfferCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    rid = _get_restaurant_id(user)
    offer = Offer(restaurant_id=rid, **data.model_dump())
    db.add(offer)
    db.commit()
    db.refresh(offer)
    return offer


@router.put("/offers/{offer_id}", response_model=OfferOut)
def update_offer(offer_id: int, data: OfferUpdate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    rid = _get_restaurant_id(user)
    offer = db.query(Offer).filter(Offer.id == offer_id, Offer.restaurant_id == rid).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(offer, key, value)
    db.commit()
    db.refresh(offer)
    return offer


# --- Settings ---

@router.get("/settings", response_model=RestaurantOut)
def get_settings(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    rid = _get_restaurant_id(user)
    restaurant = db.query(Restaurant).filter(Restaurant.id == rid).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant


@router.put("/settings", response_model=RestaurantOut)
def update_settings(data: RestaurantUpdate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    rid = _get_restaurant_id(user)
    restaurant = db.query(Restaurant).filter(Restaurant.id == rid).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(restaurant, key, value)
    db.commit()
    db.refresh(restaurant)
    return restaurant
