from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from app.config.settings import TELEGRAM_BOT_TOKEN, WEBHOOK_HOST_URL
from app.modules.telegram.telegram_service import TelegramService


@asynccontextmanager
async def lifespan(app:FastAPI) -> AsyncGenerator[None, None]:
    print("Starting up...")
    tg = TelegramService(TELEGRAM_BOT_TOKEN)
    await tg.set_webhook(f"{WEBHOOK_HOST_URL}/telegram/webhook")
    
    yield
    print("Shutting down...")