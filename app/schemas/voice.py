from pydantic import BaseModel, Field, field_validator


class VoiceMessageRequest(BaseModel):
    """Схема для входящего голосового сообщения"""
    file_id: str = Field(..., description="ID файла в Telegram")
    duration: int = Field(..., ge=1, description="Длительность в секундах")
    file_size: int | None = Field(None, ge=0, description="Размер файла в байтах")
    
    @field_validator('duration')
    def validate_duration(cls, v):
        if v > 300:
            raise ValueError('Голосовое сообщение слишком длинное (максимум 5 минут)')
        return v
    
    @field_validator('file_size')
    def validate_file_size(cls, v):
        if v and v > 20 * 1024 * 1024:
            raise ValueError('Файл слишком большой (максимум 20 МБ)')
        return v


class AudioProcessingResult(BaseModel):
    """Схема результата обработки аудио"""
    success: bool = Field(..., description="Успешность обработки")
    text: str | None = Field(default=None, description="Распознанный текст")
    error_message: str | None = Field(default=None, description="Сообщение об ошибке")
    processing_time: float | None = Field(default=None, ge=0, description="Время обработки в секундах")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "text": "Привет, как дела?",
                "error_message": None,
                "processing_time": 2.5,
            }
        }
