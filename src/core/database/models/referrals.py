from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, VARCHAR, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models import Base, TableNameMixin

if TYPE_CHECKING:
    from .users import User


class ReferralCode(Base):
    __tablename__ = "referral_codes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    code: Mapped[str] = mapped_column(VARCHAR(8), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    owner: Mapped["User"] = relationship(
        "User", back_populates="referral_code", lazy="selectin"
    )

    def __repr__(self):
        return f"{self.owner.username} | {self.expires_at}"


class Referral(TableNameMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    referrer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    referred_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    referrer: Mapped["User"] = relationship(
        "User", back_populates="referrals", foreign_keys=referrer_id, lazy="selectin"
    )
    referred: Mapped["User"] = relationship(
        "User", back_populates="invited_by", foreign_keys=referred_id, lazy="selectin"
    )

    def __repr__(self):
        return f"{self.referrer} | {self.referred}"
