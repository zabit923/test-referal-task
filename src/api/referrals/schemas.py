from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReferralCodeCreate(BaseModel):
    code: str = Field(max_length=10)
    expires_at: datetime


class ReferralCodeRead(BaseModel):
    code: str
    expires_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
