from datetime import datetime, timedelta, timezone
from email import message
import email
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.repository.auth_repository import AuthRepository
from app.config.settings import pwd_context, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.modules.auth.schemas import user
from app.modules.auth.service import otp_service
from app.modules.auth.service.otp_service import OtpService
from app.modules.redis import redis_service
import jwt
from jwt import PyJWTError


class AuthService:
    def __init__(self, db: AsyncSession):
        self.auth_repository = AuthRepository(db)


    def _hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)


    def _create_access_token(self, user_id: int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {"sub": str(user_id), "exp": expire}
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token


    def _create_refresh_token(self, user_id: int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(days=30)
        payload = {"sub": str(user_id), "exp": expire}
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token


    async def get_current_user(self, token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = int(payload.get("sub"))
        except (PyJWTError, TypeError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

        user = await self.auth_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return user


    async def register_user(self, user):
        user = user.model_dump()
        existing_user = await self.auth_repository.get_user_by_phone(user['phone_number'])
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this phone number already exists"
            )
        
        
        otp_service = OtpService(redis_service.redis)
        is_valid_otp = await otp_service.verify_otp(user['phone_number'], user['otp'])
        if not is_valid_otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP"
        )
        
       
        hashed_password = self._hash_password(user['password'])
        new_user = await self.auth_repository.create_user(user['phone_number'], hashed_password, user['first_name'], user['last_name'])
        await self.login_user(new_user.phone_number, user['password'])


    async def login_user(self, phone: str, password: str):
        user = await self.auth_repository.get_user_by_phone(phone)
        if not user or not self._verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid phone or password"
            )

        access_token = self._create_access_token(user.id)
        refresh_token = self._create_refresh_token(user.id)

        response = JSONResponse(
            content={
                "access_token": access_token,
                "token_type": "bearer"
            },
            status_code=status.HTTP_200_OK
        )


        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,     
            samesite="strict",
            max_age=30*24*60*60 
        )

        return response


    async def refresh_access_token(self, refresh_token: str):
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = int(payload.get("sub"))
        except (PyJWTError, TypeError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired or invalid. Please log in again."
            )

        user = await self.auth_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        new_access_token = self._create_access_token(user.id)

        return JSONResponse(
            content={"access_token": new_access_token, "token_type": "bearer"},
            status_code=status.HTTP_200_OK
        )


    async def logout_user(self):
        response = JSONResponse(
            content={"message": "Logged out successfully"},
            status_code=status.HTTP_200_OK
        )
        response.delete_cookie("refresh_token")
        return response
