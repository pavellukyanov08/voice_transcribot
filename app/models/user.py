from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, BigInteger

from app.core.db import Base
from app.utils import DateTimeManager


class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        comment="Telegram ID of user"
    )
    name: Mapped[str] = mapped_column(nullable=True, comment="Name of user")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=DateTimeManager.get_now_utc(),
        comment="User created date",
    )

    messages = relationship(
        "Message",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __str__(self):
        return self.name