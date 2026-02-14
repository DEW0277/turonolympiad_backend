from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.modules.telegram.telegram_service import TelegramService
from app.modules.auth.service.otp_service import OtpService
from app.config.settings import TELEGRAM_BOT_TOKEN
from app.modules.redis import redis_service
import asyncio


router = APIRouter()
otp_service = OtpService(redis_service.redis)
telegram_service = TelegramService(TELEGRAM_BOT_TOKEN)


@router.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
    except Exception as e:
        return JSONResponse({"ok": False, "error": "Invalid JSON"}, status_code=400)

    asyncio.create_task(process_update(data))
    return JSONResponse({"ok": True})


async def process_update(data: dict):
    update_id = data.get("update_id")
    message = data.get("message")
    callback_query = data.get("callback_query")  # for inline buttons

    if not (message or callback_query) or not update_id:
        return

    chat_id = None
    user_id = None
    text = None
    contact = None
    callback_data = None

    if message:
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        text = message.get("text")
        contact = message.get("contact")
    elif callback_query:
        chat_id = callback_query["message"]["chat"]["id"]
        user_id = callback_query["from"]["id"]
        callback_data = callback_query.get("data")

    # Deduplicate updates
    last_update_id = await redis_service.redis.get(f"telegram_last_update_{chat_id}")
    if last_update_id and int(last_update_id) >= update_id:
        return
    await redis_service.redis.set(f"telegram_last_update_{chat_id}", update_id, ex=3600)

    # /start command
    if text == "/start":
        contact_keyboard = {
            "keyboard": [[{"text": "📱 Share Phone Number", "request_contact": True}]],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }

        await send_multilang_message(
            chat_id,
            "👋 Welcome!\nPlease share your phone number to receive a verification code.",
            "👋 Xush kelibsiz!\nIltimos, tasdiqlash kodini olish uchun telefon raqamingizni ulashing.",
            "👋 Добро пожаловать!\nПожалуйста, поделитесь номером телефона, чтобы получить код подтверждения.",
            contact_keyboard
        )
        return

    # Contact shared
    if contact:
        if contact["user_id"] != message["from"]["id"]:
            return

        phone_number = contact["phone_number"]
        await send_otp_with_button(chat_id, phone_number)

    # Handle inline button press
    if callback_data == "request_otp":
        # Retrieve phone number from Redis
        phone_number_bytes = await redis_service.redis.get(f"telegram_phone_{user_id}")
        if not phone_number_bytes:
            # Multilingual "phone not found" modal
            text_en = "Phone number not found. Send /start first."
            text_uz = "Telefon raqami topilmadi. Avvalo /start yuboring."
            text_ru = "Номер телефона не найден. Сначала отправьте /start."
            await telegram_service.answer_callback(
                callback_query["id"],
                text=f"🇬🇧 {text_en}\n\n🇺🇿 {text_uz}\n\n🇷🇺 {text_ru}",
                show_alert=True
            )
            return

        # Decode bytes to string
        phone_number = phone_number_bytes.decode('utf-8')

        # Check cooldown
        cooldown = await otp_service.get_cooldown(phone_number)
        if cooldown > 0:
            minutes, seconds = divmod(cooldown, 60)

            # Multilingual cooldown modal
            text_en = f"⏳ Please wait {minutes}m {seconds}s before requesting a new OTP."
            text_uz = f"⏳ Yangi OTP so'rashdan oldin {minutes}m {seconds}s kuting."
            text_ru = f"⏳ Подождите {minutes}m {seconds}s перед запросом нового OTP."

            await telegram_service.answer_callback(
                callback_query["id"],
                text=f"🇬🇧 {text_en}\n\n🇺🇿 {text_uz}\n\n🇷🇺 {text_ru}",
                show_alert=True
            )
            return

        # Send new OTP
        await send_otp_with_button(chat_id, phone_number)


async def send_otp_with_button(chat_id: int, phone_number: str):
    # Normalize phone number (remove any extra '+' if present)
    
    normalized_phone = phone_number.lstrip('+')
    if not normalized_phone.startswith('+'):
        normalized_phone = '+' + normalized_phone
    
    # Save phone number for callback queries
    await redis_service.redis.set(f"telegram_phone_{chat_id}", normalized_phone, ex=600)
    
    # Create OTP
    otp = await otp_service.create_otp(normalized_phone)
    otp_code_message = f"Code:\n```{otp}```"
    await telegram_service.send_message(chat_id, otp_code_message)

    # 3-language button text
    resend_keyboard = {
        "inline_keyboard": [[
            {"text": "🔄 Request New OTP / Yangi OTP / Новый OTP", "callback_data": "request_otp"}
        ]]
    }

    await send_multilang_message(
        chat_id,
        "If you didn’t receive the OTP or it expired, press the button below to get a new one.",
        "Agar OTP kelmasa yoki muddati tugasa, yangi OTP olish uchun quyidagi tugmani bosing.",
        "Если вы не получили OTP или он истёк, нажмите кнопку ниже, чтобы получить новый.",
        reply_markup=resend_keyboard
    )



async def send_multilang_message(chat_id: int, en: str, uz: str, ru: str, reply_markup: dict = None, sticker_id: str = None, code: str = None):
    """Send messages in 3 languages, but if `code` is provided, send it as a copy-ready code snippet only."""

    if code:
        code_message = f"```{code}```"
        await telegram_service.send_message(chat_id, code_message)
        return

    # Normal multilingual message if no code
    text_message = f"🇬🇧 {en}\n\n🇺🇿 {uz}\n\n🇷🇺 {ru}"

    if sticker_id:
        await telegram_service.send_sticker(chat_id, sticker_id)

    await telegram_service.send_message(chat_id, text_message, reply_markup=reply_markup)

