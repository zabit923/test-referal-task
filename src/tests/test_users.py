import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import Referral, User
from core.factories import ReferralCodeFactory


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    response = await client.post(
        "api/v1/users/register",
        json={
            "username": "new_user",
            "email": "velibekovalibek@gmail.com",
            "password": "securepassword",
        },
    )
    assert response.status_code == 201
    assert response.json()["username"] == "new_user"
    assert response.json()["email"] == "velibekovalibek@gmail.com"


@pytest.mark.asyncio
async def test_register_user_existing_username(client: AsyncClient, test_user: User):
    response = await client.post(
        "api/v1/users/register",
        json={
            "username": "test_username",
            "email": "velibekovalibek@gmail.com",
            "password": "securepassword",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Этот username уже занят."


@pytest.mark.asyncio
async def test_register_user_existing_email(client: AsyncClient, test_user: User):
    response = await client.post(
        "api/v1/users/register",
        json={
            "username": "test_username2",
            "email": "xaclafun1991@gmail.com",
            "password": "securepassword",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Этот email уже занят."


@pytest.mark.asyncio
async def test_login_user_success(client: AsyncClient, test_user: User):
    response = await client.post(
        "api/v1/users/login",
        data={"username": "test_username", "password": "123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_register_user_with_referral_code(
    client: AsyncClient, test_session: AsyncSession, test_user: User
):
    ReferralCodeFactory._meta.sqlalchemy_session = test_session
    referral_code = ReferralCodeFactory.create(owner=test_user)
    await test_session.commit()
    new_user_data = {
        "username": "new_test_user",
        "email": "velibekovalibek@gmail.com",
        "password": "123",
    }

    response = await client.post(
        "api/v1/users/register",
        json=new_user_data,
        params={"referral_code": referral_code.code},
    )

    assert response.status_code == 201
    user_data = response.json()
    assert user_data["username"] == new_user_data["username"]
    assert user_data["email"] == new_user_data["email"]
    referral = await test_session.execute(
        select(Referral).where(Referral.referred_id == user_data["id"])
    )
    referral = referral.scalar_one_or_none()
    assert referral is not None
    assert referral.referrer_id == test_user.id
