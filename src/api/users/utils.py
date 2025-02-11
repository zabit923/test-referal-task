import uuid
from datetime import datetime, timedelta

from fastapi import HTTPException
from jose import jwt
from passlib.context import CryptContext
from starlette import status

from config import JWT_ALGORITHM, settings

SECRET = settings.secret.secret_key
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
        "exp": datetime.utcnow() + expires_delta,
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
