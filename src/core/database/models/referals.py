from datetime import datetime

from sqlalchemy import String, Boolean, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models import Base, TableNameMixin


class ReferralCode(Base):
    __tablename__ = 'referral_codes'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id'), unique=True)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    owner = relationship("User", back_populates="referral_code")

    def __repr__(self):
        return f"{self.owner.username} | {self.expires_at}"


class Referral(TableNameMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    referrer_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    referred_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    referrer = relationship("User", back_populates="referrals")
    referred = relationship("User")
