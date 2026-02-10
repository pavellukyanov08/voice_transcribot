from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey

from app.core.db import Base
from app.utils import DateTimeManager


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, comment="ID записи транскрипции")
    text: Mapped[str] = mapped_column(comment="Распознанный текст")
    processing_time: Mapped[float] = mapped_column(comment="Время обработки в секундах")
    
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.telegram_id", ondelete="CASCADE", onupdate="CASCADE"),
        comment="ID пользователя"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=DateTimeManager.get_now_utc(),
        comment="Время создания записи",
    )
    user = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="messages",
    )
