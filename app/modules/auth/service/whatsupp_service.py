from twilio.rest import Client

class WhatsAppService:
    def __init__(self, sid: str, token: str):
        self.client = Client(sid, token)

    async def send_message(self, to_phone: str, message: str):
        self.client.messages.create(
            from_='whatsapp:+14155238886',
            body=message,
            to=f'whatsapp:{to_phone}'
        )
