from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.database import Base, engine
from app.routers import admin, restaurant, webhook, order


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="WhatsApp Food Order System", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.router, prefix="/api/admin", tags=["Platform Admin"])
app.include_router(restaurant.router, prefix="/api/restaurant", tags=["Restaurant Admin"])
app.include_router(webhook.router, prefix="/api/webhook", tags=["WhatsApp Webhook"])
app.include_router(order.router, prefix="/api/orders", tags=["Orders"])


@app.get("/")
def health():
    return {"status": "running", "service": "WhatsApp Food Order System"}


@app.get("/privacy", response_class=HTMLResponse)
def privacy_policy():
    return """<!DOCTYPE html>
<html><head><title>Privacy Policy</title></head>
<body style="font-family:sans-serif;max-width:600px;margin:40px auto;padding:0 20px;">
<h1>Privacy Policy</h1>
<p>Last updated: October 2026</p>
<p>This application collects your phone number and order details solely to process food orders via WhatsApp.
We do not sell or share your data with third parties. Data is stored securely and used only for order fulfillment.</p>
<p>Contact: support@foodorder.com</p>
</body></html>"""
