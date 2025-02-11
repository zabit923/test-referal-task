from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import Referral, ReferralCode, User


class ReferralService:
    @staticmethod
    async def get_active_referral_code(user_id: int, session: AsyncSession):
        statement = select(ReferralCode).where(
            ReferralCode.owner_id == user_id,
            ReferralCode.is_active == True,
            ReferralCode.expires_at > datetime.utcnow(),
        )
        result = await session.execute(statement)
        return result.scalars().first()

    @staticmethod
    async def create_referral_code(user_id: int, referral_data, session: AsyncSession):
        new_code = ReferralCode(
            owner_id=user_id,
            code=referral_data.code,
            expires_at=referral_data.expires_at,
            is_active=True,
        )
        session.add(new_code)
        await session.commit()
        return new_code

    @staticmethod
    async def delete_referral_code(user_id: int, session: AsyncSession):
        statement = delete(ReferralCode).where(
            ReferralCode.owner_id == user_id, ReferralCode.is_active == True
        )
        await session.execute(statement)
        await session.commit()

    @staticmethod
    async def get_referral_code_by_email(email: str, session: AsyncSession):
        statement = (
            select(ReferralCode)
            .join(User)
            .where(
                User.email == email,
                ReferralCode.is_active == True,
                ReferralCode.expires_at > datetime.utcnow(),
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
                ReferralCode.is_active == True,
                ReferralCode.expires_at > datetime.utcnow(),
            )
        )
        result = await session.execute(statement)
        return result.scalars().first()

    @staticmethod
    async def add_referral(
        referrer_id: int, referred_user_id: int, session: AsyncSession
    ):
        referral = Referral(referrer_id=referrer_id, referred_user_id=referred_user_id)
        session.add(referral)
        await session.commit()

    @staticmethod
    async def get_referrals_by_referrer(referrer_id: int, session: AsyncSession):
        statement = select(Referral).where(Referral.referrer_id == referrer_id)
        result = await session.execute(statement)
        return result.scalars().all()
