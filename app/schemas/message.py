from datetime import datetime
from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    text: str = Field(..., description="Распознанный текст")
    processing_time: float = Field(..., ge=0, description="Время обработки в секундах")


class MessageCreate(MessageBase):
    user_id: int = Field(..., description="ID пользователя")
    text: str = Field(..., description="Распознанный текст")


class MessageRead(MessageBase):
    id: int = Field(..., description="ID записи")
    user_id: int = Field(..., description="ID пользователя")
    created_at: datetime = Field(..., description="Время создания")
    updated_at: datetime = Field(..., description="Время обновления")
