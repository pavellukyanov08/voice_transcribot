from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    file_id: str = Field(..., description="ID файла в Telegram")
    file_unique_id: str = Field(..., description="Уникальный ID файла")
    text: str = Field(..., description="Распознанный текст")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Уверенность модели")
    processing_time: float = Field(..., ge=0, description="Время обработки в секундах")


class MessageCreate(MessageBase):
    user_id: int = Field(..., description="ID пользователя")
    text: str = Field(..., description="Распознанный текст")


class MessageUpdate(BaseModel):
    text: Optional[str] = Field(None, description="Обновленный текст")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Обновленная уверенность")


class MessageRead(MessageBase):
    id: int = Field(..., description="ID записи")
    user_id: int = Field(..., description="ID пользователя")
    text: str = Field(..., description="Распознанный текст")
    created_at: datetime = Field(..., description="Время создания")
    updated_at: datetime = Field(..., description="Время обновления")
