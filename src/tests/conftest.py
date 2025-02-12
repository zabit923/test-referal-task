from datetime import timedelta

import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from api.users.utils import create_access_token, generate_passwd_hash
from app import app
from core.database import get_async_session, get_test_async_session, test_engine
from core.database.models import Base, Referral, ReferralCode, User


@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def test_session(init_db) -> AsyncSession:
    async for session in get_test_async_session():
        await session.execute(delete(User))
        await session.execute(delete(Referral))
        await session.execute(delete(ReferralCode))
        await session.commit()
        yield session
        await session.close()


@pytest_asyncio.fixture
async def client(init_db) -> AsyncClient:
    async def override_get_test_session():
        async for session in get_test_async_session():
            yield session

    app.dependency_overrides[get_async_session] = override_get_test_session

    async with LifespanManager(app):
        async with AsyncClient(
            transport=ASGITransport(app), base_url="http://test"
        ) as async_client:
            yield async_client


@pytest_asyncio.fixture
async def test_user(test_session: AsyncSession) -> User:
    user = User(
        username="test_username",
        email="xaclafun1991@gmail.com",
        password=generate_passwd_hash("123"),
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest_asyncio.fixture
def authenticated_test_client(client: AsyncClient, test_user: User):
    access_token = create_access_token(
        test_user.username, test_user.id, expires_delta=timedelta(seconds=5)
    )
    client.cookies.update({"access_token": access_token})

    yield client
