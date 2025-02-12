import uuid
from datetime import datetime, timedelta

import httpx
from fastapi import HTTPException
from jose import jwt
from passlib.context import CryptContext
from starlette import status

from config import HUNTER_API_KEY, JWT_ALGORITHM, settings

SECRET = settings.secret.secret_key
HUNTER_API_URL = "https://api.hunter.io/v2/email-verifier"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_passwd_hash(password: str) -> str:
    password_hash = bcrypt_context.hash(password)
    return password_hash


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt_context.verify(password, password_hash)


def create_access_token(
    username: str, user_id: int, expires_delta: timedelta = None, refresh: bool = False
):
    payload = {
        "username": username,
        "user_id": user_id,
        "refresh": refresh,
        "exp": datetime.now() + expires_delta,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    token_data = jwt.decode(token=token, key=SECRET, algorithms=[JWT_ALGORITHM])
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired."
        )
    return token_data


async def verify_email_with_hunter(email: str) -> bool:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            HUNTER_API_URL,
            params={"email": email, "api_key": HUNTER_API_KEY},
        )

        data = response.json().get("data", {})
        email_status = data.get("status")

        if email_status == "valid":
            return True
        elif email_status == "invalid":
            return False
        else:
            return False
