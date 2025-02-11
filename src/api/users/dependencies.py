from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.users.service import UserService
from api.users.utils import decode_token
from config import settings
from core.database import get_async_session

user_service = UserService()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
SECRET_KEY = settings.secret.secret_key


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
):
    payload = decode_token(token)
    user_id: int = payload.get("user_id")
    user = await user_service.get_user_by_id(user_id, session)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user
