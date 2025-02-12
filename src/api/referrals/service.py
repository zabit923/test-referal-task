import json
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.referrals.schemas import ReferralCodeRead
from config import redis_client
from core.database.models import Referral, ReferralCode, User


class ReferralService:
    @staticmethod
    async def get_referral_code(code: str, session: AsyncSession):
        cached_referral = await redis_client.get(f"referral_code:{code}")
        if cached_referral:
            return ReferralCodeRead.model_validate(json.loads(cached_referral))

        statement = select(ReferralCode).where(ReferralCode.code == code)
        result = await session.execute(statement)
        referral_code = result.scalars().first()

        if referral_code:
            expires_in = (referral_code.expires_at - datetime.now()).total_seconds()
            referral_code_data = ReferralCodeRead.model_validate(
                referral_code
            ).model_dump(mode="json")
            await redis_client.setex(
                f"referral_code:{code}", int(expires_in), json.dumps(referral_code_data)
            )

        return referral_code

    @staticmethod
    async def get_active_referral_code(user_id: int, session: AsyncSession):
        cached_referral = await redis_client.get(f"active_referral_code:{user_id}")
        if cached_referral:
            return ReferralCodeRead.model_validate(json.loads(cached_referral))

        statement = select(ReferralCode).where(
            ReferralCode.owner_id == user_id,
            ReferralCode.is_active.is_(True),
            ReferralCode.expires_at > datetime.now(),
        )
        result = await session.execute(statement)
        referral_code = result.scalars().first()

        if referral_code:
            expires_in = (referral_code.expires_at - datetime.now()).total_seconds()
            referral_code_data = ReferralCodeRead.model_validate(
                referral_code
            ).model_dump(mode="json")
            await redis_client.setex(
                f"active_referral_code:{user_id}",
                int(expires_in),
                json.dumps(referral_code_data),
            )

        return referral_code

    @staticmethod
    async def create_referral_code(user_id: int, referral_data, session: AsyncSession):
        if referral_data.expires_at <= datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Дата окончания не может быть меньше или равна текущему времени.",
            )
        new_code = ReferralCode(
            owner_id=user_id,
            code=referral_data.code,
            expires_at=referral_data.expires_at,
            is_active=True,
        )
        session.add(new_code)
        await session.commit()

        expires_in = (referral_data.expires_at - datetime.now()).total_seconds()
        referral_code_data = ReferralCodeRead.model_validate(new_code).model_dump(
            mode="json"
        )
        await redis_client.setex(
            f"referral_code:{referral_data.code}",
            int(expires_in),
            json.dumps(referral_code_data),
        )
        await redis_client.setex(
            f"active_referral_code:{user_id}",
            int(expires_in),
            json.dumps(referral_code_data),
        )

        return new_code

    @staticmethod
    async def delete_referral_code(user_id: int, session: AsyncSession):
        statement = select(ReferralCode).where(
            ReferralCode.owner_id == user_id, ReferralCode.is_active.is_(True)
        )
        result = await session.execute(statement)
        referral_code = result.scalars().first()
        if not referral_code:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        if referral_code:
            await redis_client.delete(f"referral_code:{referral_code.code}")
            await redis_client.delete(f"active_referral_code:{user_id}")

        await session.delete(referral_code)
        await session.commit()

    @staticmethod
    async def get_referral_code_by_email(email: str, session: AsyncSession):
        statement = (
            select(ReferralCode)
            .join(User)
            .where(
                User.email == email,
                ReferralCode.is_active.is_(True),
                ReferralCode.expires_at > datetime.now(),
            )
        )
        result = await session.execute(statement)
        return result.scalars().first()

    @staticmethod
    async def get_referrer_by_code(code: str, session: AsyncSession):
        statement = (
            select(User)
            .join(ReferralCode)
            .where(
                ReferralCode.code == code,
                ReferralCode.is_active.is_(True),
                ReferralCode.expires_at > datetime.now(),
            )
        )
        result = await session.execute(statement)
        return result.scalars().first()

    @staticmethod
    async def add_referral(referrer_id: int, referred_id: int, session: AsyncSession):
        referral = Referral(referrer_id=referrer_id, referred_id=referred_id)
        session.add(referral)
        await session.commit()

    @staticmethod
    async def get_referrals_by_referrer(referrer_id: int, session: AsyncSession):
        statement = (
            select(User)
            .join(Referral, User.id == Referral.referred_id)
            .where(Referral.referrer_id == referrer_id)
        )
        result = await session.execute(statement)
        return result.scalars().all()
