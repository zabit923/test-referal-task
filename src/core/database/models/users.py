from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import TIMESTAMP, VARCHAR, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models import Base, TableNameMixin

if TYPE_CHECKING:
    from .refferals import Referral, ReferralCode


class User(TableNameMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        VARCHAR(128), unique=True, index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(VARCHAR(255), unique=True)
    password: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )

    referral_code: Mapped["ReferralCode"] = relationship(
        "ReferralCode", back_populates="owner", uselist=False
    )
    referrals: Mapped[List["Referral"]] = relationship(
        "Referral", back_populates="referrer", foreign_keys="[Referral.referrer_id]"
    )
    invited_by: Mapped[Optional["Referral"]] = relationship(
        "Referral",
        back_populates="referred",
        foreign_keys="[Referral.referred_id]",
        uselist=False,
    )

    def __repr__(self):
        return f"{self.username}"
