import httpx
import asyncio
from app.config.settings import WEBHOOK_HOST_URL


class TelegramService:
    def __init__(self, bot_token: str):
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    async def send_message(self, chat_id: int, text: str, reply_markup=None):
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
        if reply_markup:
            payload["reply_markup"] = reply_markup

        async with httpx.AsyncClient() as client:
            await client.post(f"{self.base_url}/sendMessage", json=payload)

    async def send_sticker(self, chat_id: int, sticker_id: str):
        payload = {"chat_id": chat_id, "sticker": sticker_id}
        async with httpx.AsyncClient() as client:
            await client.post(f"{self.base_url}/sendSticker", json=payload)



    async def set_webhook(self, webhook_url: str):
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/setWebhook",
                params={"url": webhook_url}
            )
            return resp.json()
    
    async def answer_callback(self, callback_query_id: str, text: str = None, show_alert: bool = False):
        """Respond to a callback query (inline button press)"""
        payload = {
            "callback_query_id": callback_query_id,
            "show_alert": show_alert
        }
        if text:
            payload["text"] = text

        async with httpx.AsyncClient() as client:
            await client.post(f"{self.base_url}/answerCallbackQuery", json=payload)