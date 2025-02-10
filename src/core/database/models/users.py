from datetime import datetime

from sqlalchemy import VARCHAR, false, BOOLEAN, func, TIMESTAMP, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models import Base, TableNameMixin


class User(TableNameMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        VARCHAR(128), unique=True, index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(VARCHAR(255), unique=True)
    password: Mapped[str] = mapped_column(String)
    is_superuser: Mapped[bool] = mapped_column(BOOLEAN, server_default=false())
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )

    referral_code = relationship("ReferralCode", back_populates="owner", uselist=False)
    referrals = relationship("Referral", back_populates="referrer")

    def __repr__(self):
        return f"{self.username}"
