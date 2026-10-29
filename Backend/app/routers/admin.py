from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.restaurant import Restaurant
from app.models.user import PlatformAdmin
from app.schemas.restaurant import RestaurantCreate, RestaurantOut, RestaurantWhatsAppConfig, RestaurantUpdate
from app.schemas.user import AdminLogin, TokenOut
from app.utils.auth import hash_password, verify_password, create_token, get_current_user

router = APIRouter()


@router.post("/login", response_model=TokenOut)
def admin_login(data: AdminLogin, db: Session = Depends(get_db)):
    admin = db.query(PlatformAdmin).filter(PlatformAdmin.email == data.email).first()
    if not admin or not verify_password(data.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({"sub": str(admin.id), "role": "platform_admin"})
    return {"access_token": token}


@router.post("/restaurants", response_model=RestaurantOut)
def create_restaurant(
    data: RestaurantCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    if user.get("role") != "platform_admin":
        raise HTTPException(status_code=403, detail="Platform admin only")
    restaurant = Restaurant(**data.model_dump())
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return restaurant


@router.get("/restaurants", response_model=List[RestaurantOut])
def list_restaurants(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    if user.get("role") != "platform_admin":
        raise HTTPException(status_code=403, detail="Platform admin only")
    return db.query(Restaurant).all()


@router.patch("/restaurants/{restaurant_id}", response_model=RestaurantOut)
def update_restaurant(
    restaurant_id: int,
    data: RestaurantUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    if user.get("role") != "platform_admin":
        raise HTTPException(status_code=403, detail="Platform admin only")
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(restaurant, key, value)
    db.commit()
    db.refresh(restaurant)
    return restaurant


@router.put("/restaurants/{restaurant_id}/whatsapp", response_model=RestaurantOut)
def set_whatsapp_config(
    restaurant_id: int,
    data: RestaurantWhatsAppConfig,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    if user.get("role") != "platform_admin":
        raise HTTPException(status_code=403, detail="Platform admin only")
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    restaurant.whatsapp_phone_number_id = data.whatsapp_phone_number_id
    restaurant.whatsapp_access_token = data.whatsapp_access_token
    db.commit()
    db.refresh(restaurant)
    return restaurant
