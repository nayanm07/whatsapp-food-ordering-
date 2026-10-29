from pydantic import BaseModel


class AdminLogin(BaseModel):
    email: str
    password: str


class RestaurantAdminLogin(BaseModel):
    phone: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
