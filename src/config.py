from pathlib import Path
from typing import Literal

import redis.asyncio as aioredis
from environs import Env
from pydantic import BaseModel
from pydantic_settings import BaseSettings

env = Env()
env.read_env()


DEBUG = env.bool("DEBUG")

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "sqlite3.db"


LOG_DEFAULT_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
)

DB_USERNAME = env.str("POSTGRES_USER")
DB_PASSWORD = env.str("POSTGRES_PASSWORD")
DB_HOST = env.str("DB_HOST")
DB_PORT = env.int("DB_PORT")
DB_DATABASE = env.str("POSTGRES_DB")

JWT_ALGORITHM = "HS256"

SECRET_KEY = env.str("SECRET_KEY")
RESET_PASSWORD_TOKEN_SECRET = env.str("RESET_PASSWORD_TOKEN_SECRET")
VERIFICATION_TOKEN_SECRET = env.str("VERIFICATION_TOKEN_SECRET")

HUNTER_API_KEY = env.str("HUNTER_API_KEY")


class SecretKey(BaseModel):
    secret_key: str = SECRET_KEY
    reset_password_token_secret: str = RESET_PASSWORD_TOKEN_SECRET
    verification_token_secret: str = VERIFICATION_TOKEN_SECRET


class RunConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000


class LoggingConfig(BaseModel):
    log_level: Literal[
        "debug",
        "info",
        "warning",
        "error",
        "critical",
    ] = "info"
    log_format: str = LOG_DEFAULT_FORMAT


class DbSettings(BaseModel):
    url: str = (
        f"postgresql+asyncpg://"
        f"{DB_USERNAME}:"
        f"{DB_PASSWORD}@"
        f"localhost:"
        f"{DB_PORT}/"
        f"{DB_DATABASE}"
        if DEBUG
        else f"postgresql+asyncpg://"
        f"{DB_USERNAME}:"
        f"{DB_PASSWORD}@"
        f"{DB_HOST}:"
        f"{DB_PORT}/"
        f"{DB_DATABASE}"
    )
    test_url: str = "sqlite+aiosqlite:///test.db"
    echo: bool = True


class Settings(BaseSettings):
    run: RunConfig = RunConfig()
    db: DbSettings = DbSettings()
    secret: SecretKey = SecretKey()
    logging: LoggingConfig = LoggingConfig()


redis_client = aioredis.from_url(
    "redis://localhost:6379" if DEBUG else "redis://redis:6379", decode_responses=True
)
settings = Settings()
