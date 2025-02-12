import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import Referral, User
from core.factories import ReferralCodeFactory, UserFactory


@pytest.mark.asyncio
async def test_create_referral_code(
    authenticated_test_client: AsyncClient, test_session: AsyncSession, test_user: User
):
    referral_data = {"code": "TEST", "expires_at": "2027-02-14 12:00:00"}
    response = await authenticated_test_client.post(
        "api/v1/referrals", json=referral_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "TEST"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_create_referral_code_already_exists(
    authenticated_test_client: AsyncClient, test_session: AsyncSession, test_user: User
):
    ReferralCodeFactory._meta.sqlalchemy_session = test_session
    ReferralCodeFactory.create(owner=test_user)
    await test_session.commit()
    referral_data = {"code": "TEST", "expires_at": "2027-02-14 12:00:00"}
    response = await authenticated_test_client.post(
        "api/v1/referrals", json=referral_data
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "У вас уже есть активный реферальный код."


@pytest.mark.asyncio
async def test_delete_referral_code(
    authenticated_test_client: AsyncClient, test_session: AsyncSession, test_user: User
):
    ReferralCodeFactory._meta.sqlalchemy_session = test_session
    ReferralCodeFactory.create(owner=test_user)
    await test_session.commit()
    response = await authenticated_test_client.delete("api/v1/referrals")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_get_referral_code_by_email(
    authenticated_test_client: AsyncClient, test_session: AsyncSession, test_user: User
):
    ReferralCodeFactory._meta.sqlalchemy_session = test_session
    referral_code = ReferralCodeFactory.create(owner=test_user)
    await test_session.commit()
    response = await authenticated_test_client.get(
        f"api/v1/referrals/code-by-email/{test_user.email}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == referral_code.code


@pytest.mark.asyncio
async def test_get_referral_code_by_email_not_found(
    authenticated_test_client: AsyncClient,
):
    response = await authenticated_test_client.get(
        "api/v1/referrals/code-by-email/nonexistent@example.com"
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_referrals_by_referrer(
    authenticated_test_client: AsyncClient, test_session: AsyncSession, test_user: User
):
    UserFactory._meta.sqlalchemy_session = test_session
    referred_users = [UserFactory.create() for _ in range(3)]
    await test_session.commit()
    for referred_user in referred_users:
        referral = Referral(referrer_id=test_user.id, referred_id=referred_user.id)
        test_session.add(referral)
    await test_session.commit()
    response = await authenticated_test_client.get(
        f"api/v1/referrals/get-referrals/{test_user.id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert set(user["id"] for user in data) == set(user.id for user in referred_users)
