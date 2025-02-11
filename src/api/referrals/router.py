from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.users.dependencies import get_current_user
from api.users.schemas import UserRead
from core.database import get_async_session

from .schemas import ReferralCodeCreate, ReferralCodeRead, ReferralInfo
from .service import ReferralService

router = APIRouter(prefix="/referrals")
referral_service = ReferralService()


@router.post("", response_model=ReferralCodeRead)
async def create_referral_code(
    referral_data: ReferralCodeCreate,
    current_user: UserRead = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    existing_code = await referral_service.get_active_referral_code(
        current_user.id, session
    )
    if existing_code:
        raise HTTPException(
            status_code=400, detail="У вас уже есть активный реферальный код."
        )

    new_code = await referral_service.create_referral_code(
        current_user.id, referral_data, session
    )
    return new_code


@router.delete("", status_code=204)
async def delete_referral_code(
    current_user: UserRead = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    deleted = await referral_service.delete_referral_code(current_user.id, session)
    if not deleted:
        raise HTTPException(status_code=404)
    return {"detail": "Referral code deleted successfully."}


@router.get("/by-email/{email}", response_model=ReferralCodeRead)
async def get_referral_code_by_email(
    email: str,
    session: AsyncSession = Depends(get_async_session),
):
    referral_code = await referral_service.get_referral_code_by_email(email, session)
    if not referral_code:
        raise HTTPException(status_code=404)
    return referral_code


@router.get("/{referrer_id}", response_model=list[ReferralInfo])
async def get_referrals_by_referrer(
    referrer_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    referrals = await referral_service.get_referrals_by_referrer(referrer_id, session)
    return referrals
