from pydantic import BaseModel, Field, field_validator


class AudioMessageRequest(BaseModel):
    file_id: str = Field(..., description="ID файла в Telegram")
    duration: int = Field(..., ge=1, description="Длительность в секундах")
    file_size: int | None = Field(None, ge=0, description="Размер файла в байтах")
    type: str | None = Field(None, description="Тип файла")
    
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
    success: bool = Field(..., description="Успешность обработки")
    text: str | None = Field(default=None, description="Распознанный текст")
    error_message: str | None = Field(default=None, description="Сообщение об ошибке")
    processing_time: float | None = Field(default=None, ge=0, description="Время обработки в секундах")
    file_info: dict | None = Field(default=None, description="Информация о файле")