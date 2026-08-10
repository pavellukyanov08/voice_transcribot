from pydantic import BaseModel, Field, field_validator
from app.core import settings


class AudioMessageRequest(BaseModel):
    file_id: str = Field(..., description="ID файла в Telegram")
    duration: int | None = Field(default=None, ge=1, description="Длительность в секундах")
    mime_type: str | None = Field(default=None, description="Формат файла")
    file_size: int | None = Field(None, ge=0, description="Размер файла в байтах")

    @field_validator('duration')
    def validate_duration(cls, v):
        if v > settings.MAX_MESSAGE_DURATION:
            raise ValueError('Голосовое сообщение слишком длинное (максимум 5 минут)')
        return v
    
    @field_validator('file_size')
    def validate_file_size(cls, v):
        if v and v > settings.MAX_AUDIO_SIZE_MB * 1024 * 1024:
            raise ValueError(f'Файл слишком большой (максимум {settings.MAX_AUDIO_SIZE_MB} МБ)')
        return v

    @field_validator('mime_type')
    def validate_mime_type(cls, v):
        if v not in settings.SUPPORTED_AUDIO or settings.SUPPORTED_AUDIO:
            raise ValueError(f'Неподдерживаемый формат файла')
        return v


class AudioProcessingResult(BaseModel):
    success: bool = Field(..., description="Успешность обработки")
    text: str | None = Field(default=None, description="Распознанный текст")
    saved_to_db: bool = Field(default=False, description="Флаг успешности сохранения в БД")
    error_message: str | None = Field(default=None, description="Сообщение об ошибке")
    processing_time: float | None = Field(default=None, ge=0, description="Время обработки в секундах")