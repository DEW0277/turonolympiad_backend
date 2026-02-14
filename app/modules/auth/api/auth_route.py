from fastapi import APIRouter, Request, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.auth.service.otp_service import OtpService
from app.modules.auth.service.auth_service import AuthService
from app.modules.auth.schemas.user import UserRegister, UserLogin
from app.dependencies.database_dependecy import get_session

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")




@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister, db: AsyncSession = Depends(get_session)):
    """User registration endpoint."""
    service = AuthService(db)
    return await service.register_user(user)


@router.post("/login")
async def login(user: UserLogin, db = Depends(get_session)):
    """User login endpoint."""
    service = AuthService(db)
    return await service.login_user(user.email, user.password)


@router.post("/refresh")
async def refresh(request: Request):
    """Refresh access token endpoint."""
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token provided")
    return await AuthService.refresh_access_token(refresh_token)


@router.post("/logout")
async def logout():
    """User logout endpoint."""
    return await AuthService.logout_user()