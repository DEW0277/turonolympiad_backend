from fastapi import Depends
from app.dependencies.database_dependecy import get_session

from app.modules.auth.api.auth_route import oauth2_scheme
from app.modules.auth.service.auth_service import AuthService


def get_auth_service(db=Depends(get_session)):
    return AuthService(db)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.get_current_user(token)