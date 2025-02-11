from datetime import datetime

from pydantic import BaseModel, Field


class ReferralCodeCreate(BaseModel):
    code: str = Field(max_length=10)
    expires_at: datetime


class ReferralCodeRead(BaseModel):
    code: str
    expires_at: datetime
    is_active: bool


class ReferralInfo(BaseModel):
    id: int
    username: str
    email: str
    referred_at: datetime
