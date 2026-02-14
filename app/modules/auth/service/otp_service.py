import random
from redis.asyncio import Redis
from fastapi import HTTPException, status



class OtpService:
    def __init__(self, redis: Redis):
        self.redis = redis

    def _generate_otp(self) -> str:
        return str(random.randint(100000, 999999))

    async def create_otp(self, phone: str) -> str:
        cooldown_key = f"otp_cooldown:{phone}"
        cooldown_exists = await self.redis.get(cooldown_key)

        if cooldown_exists:
            raise HTTPException(
                status_code=429,
                detail="Please wait before requesting another OTP"
            )

        otp = self._generate_otp()
        
        await self.redis.setex(
            f"otp:{phone}",
            300,
            otp
        )

        await self.redis.setex(
            cooldown_key,
            60,
            "1"
        )

        stored_otp = await self.redis.get(f"otp:{phone}")
        print(f"Generated OTP for {phone}: {stored_otp.decode() if stored_otp else None}")
        return otp
    

    async def verify_otp(self, phone: str, otp: str) -> bool:
        stored_otp = await self.redis.get(f"otp:{phone}")

        print(f"Stored OTP for {phone}: {stored_otp.decode() if stored_otp else None}, Provided OTP: {otp}")

        if not stored_otp:
            return False

        # Convert both to integers for comparison
        if int(stored_otp.decode()) != int(otp):
            return False

        await self.redis.delete(f"otp:{phone}")
        return True


    async def get_cooldown(self, phone: str) -> int:
        """Return remaining cooldown seconds, 0 if none"""
        cooldown_key = f"otp_cooldown:{phone}"
        ttl = await self.redis.ttl(cooldown_key)
        return max(ttl, 0)