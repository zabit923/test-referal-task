from datetime import timedelta
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.referrals.service import ReferralService
from core.database.db import get_async_session

from .schemas import Token, UserCreate, UserRead
from .service import UserService
from .utils import create_access_token, verify_email_with_hunter, verify_password

router = APIRouter(prefix="/users")
user_service = UserService()
referral_service = ReferralService()


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserRead)
async def register_user(
    user_data: UserCreate,
    referral_code: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_async_session),
):
    username_exist = await user_service.get_user_by_username(
        user_data.username, session
    )
    email_exist = await user_service.get_user_by_email(user_data.email, session)
    is_valid_email = await verify_email_with_hunter(user_data.email)
    if username_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Этот username уже занят.",
        )
    if email_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Этот email уже занят.",
        )
    if not is_valid_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Недействительный email."
        )
    if referral_code:
        code = await referral_service.get_referral_code(referral_code, session)
        if not code.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        referrer = await referral_service.get_referrer_by_code(referral_code, session)
        if not referrer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный реферальный код.",
            )
        new_user = await user_service.create_user(user_data, session)
        await referral_service.add_referral(referrer.id, new_user.id, session)
        return new_user
    new_user = await user_service.create_user(user_data, session)
    return new_user


@router.post("/login", status_code=status.HTTP_201_CREATED, response_model=Token)
async def login_user(
    login_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_async_session),
):
    user = await user_service.get_user_by_username(login_data.username, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    password_valid = verify_password(
        password=login_data.password, password_hash=user.password
    )
    if password_valid:
        access_token = create_access_token(
            username=user.username, user_id=user.id, expires_delta=timedelta(hours=24)
        )
        refresh_token = create_access_token(
            username=user.username,
            user_id=user.id,
            expires_delta=timedelta(days=2),
            refresh=True,
        )
        return {"access_token": access_token, "refresh_token": refresh_token}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
