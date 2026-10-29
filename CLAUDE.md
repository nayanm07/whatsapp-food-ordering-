# WhatsApp Food Order System

## What is this project?
A multi-tenant WhatsApp-based food ordering platform. Restaurants get onboarded by a Platform Admin, customers order food through WhatsApp chatbot, and delivery is managed through WhatsApp notifications.

## Architecture

```
WhatsApp Food Order System/
├── Backend/           → Python FastAPI API server
├── Mobile App/        → Restaurant owner admin app (React Native)
├── Platform App/      → Platform admin web panel (React)
```

## Three User Roles

1. **Platform Admin (Web)** — onboards restaurants, assigns WhatsApp Business number to each restaurant
2. **Restaurant Admin (Mobile)** — manages menu, orders, delivery staff, offers, delivery distance
3. **Customer (WhatsApp)** — sends message to restaurant's WhatsApp number, AI chatbot takes the order

## Tech Stack

- **Backend**: Python 3.12+, FastAPI, SQLAlchemy, Alembic (migrations), PostgreSQL
- **AI Chatbot**: OpenAI API (gpt-4o) with function calling (tools) — no LangChain, no vector DB, no agent framework
- **WhatsApp**: Meta Cloud API (WhatsApp Business)
- **Auth**: JWT tokens
- **Mobile App**: React Native (Expo)
- **Platform App**: React + Vite

## Key Design Decisions

- One FastAPI webhook handles ALL restaurants — identifies restaurant by `phone_number_id` from Meta
- Each restaurant has its own `whatsapp_phone_number_id` and `whatsapp_access_token` in the database (set by Platform Admin)
- No global WhatsApp token in env — tokens are per-restaurant
- AI agent is just direct OpenAI API call with function calling tools (add_to_cart, place_order, show_menu, etc.) — no complex frameworks needed
- Customer conversation state (cart, session) tracked in DB by customer phone number

## Backend Structure

```
Backend/
├── app/
│   ├── main.py              — FastAPI app entry point
│   ├── config.py            — settings from env vars
│   ├── database.py          — DB engine + session
│   ├── models/              — SQLAlchemy ORM models
│   ├── schemas/             — Pydantic request/response schemas
│   ├── routers/             — API route handlers
│   ├── services/            — Business logic
│   └── utils/               — Helpers
├── alembic/                 — DB migrations
├── requirements.txt
├── .env
└── README.md
```

## Commands

- Run backend: `cd Backend && uvicorn app.main:app --reload`
- Run migrations: `cd Backend && alembic upgrade head`
- Install deps: `cd Backend && pip install -r requirements.txt`

## Environment Variables (Backend/.env)

```
DATABASE_URL=postgresql://user:pass@localhost:5432/foodorder
WHATSAPP_VERIFY_TOKEN=your_webhook_verify_token
OPENAI_API_KEY=sk-your-key
JWT_SECRET=your_jwt_secret
```
