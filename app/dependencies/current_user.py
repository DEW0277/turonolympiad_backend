from fastapi import Depends, HTTPException, status
from app.dependencies.database_dependecy import get_session
from app.modules.auth.api.auth_route import oauth2_scheme
from app.modules.auth.service.auth_service import AuthService
from app.modules.auth.models.orm import UserRole


def get_auth_service(db=Depends(get_session)):
    return AuthService(db)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.get_current_user(token)


async def get_current_admin(
    current_user = Depends(get_current_user),
):
    """Dependency to ensure user is admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access this resource"
        )
    return current_user


async def require_active_user(
    current_user = Depends(get_current_user),
):
    """Dependency to ensure user is active"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated"
        )
    return current_user


async def get_current_active_user(
    current_user = Depends(require_active_user),
):
    """Get current active user (combination of auth + active check)"""
    return current_user


async def get_current_admin_active(
    admin_user = Depends(get_current_admin),
    active_user = Depends(require_active_user),
):
    """Get current admin user that is also active"""
    if admin_user.id != active_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User mismatch"
        )
    return admin_user