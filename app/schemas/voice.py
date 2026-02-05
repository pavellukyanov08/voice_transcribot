from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field, field_validator

from app.core import settings


class VoiceMessageRequest(BaseModel):
    """Схема для входящего голосового сообщения"""
    file_id: str = Field(..., description="ID файла в Telegram")
    file_unique_id: str = Field(..., description="Уникальный ID файла")
    duration: int = Field(..., ge=1, description="Длительность в секундах")
    mime_type: str | None = Field(None, description="MIME тип файла")
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


class AudioProcessingRequest(BaseModel):
    """Схема для запроса обработки аудио"""
    file_id: str = Field(..., description="ID файла для обработки")
    user_id: int = Field(..., description="ID пользователя")

    class Config:
        json_schema_extra = {
            "example": {
                "file_id": "BAADBAADrwADBREAAYdaJge0bJsWAg",
                "user_id": 123456789,
            }
        }


class AudioProcessingResult(BaseModel):
    """Схема результата обработки аудио"""
    success: bool = Field(..., description="Успешность обработки")
    text: str | None = Field(default=None, description="Распознанный текст")
    error_message: str | None = Field(default=None, description="Сообщение об ошибке")
    processing_time: float | None = Field(default=None, ge=0, description="Время обработки в секундах")
    confidence: float | None = Field(default=None, ge=0, le=1, description="Уверенность модели (0-1)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "text": "Привет, как дела?",
                "error_message": None,
                "processing_time": 2.5,
                "confidence": 0.95
            }
        }

class VoiceTranscriptionRecord(BaseModel):
    """Полная запись транскрипции голосового сообщения"""
    id: int| None = Field(default=None, description="ID записи в БД")
    user_id: int = Field(..., description="ID пользователя")
    file_id: str = Field(..., description="ID файла в Telegram")
    original_text: str = Field(..., description="Распознанный текст")
    confidence: float | None = Field(default=None, ge=0, le=1, description="Уверенность модели")
    processing_time: float = Field(..., ge=0, description="Время обработки")
    created_at: datetime = Field(..., description="Время создания записи")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 123456789,
                "file_id": "BAADBAADrwADBREAAYdaJge0bJsWAg",
                "original_text": "Привет, как дела?",
                "confidence": 0.95,
                "processing_time": 2.5,
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


class AudioFileInfo(BaseModel):
    """Информация об аудиофайле"""
    path: Path = Field(..., description="Путь к файлу")
    format: str = Field(..., description="Формат файла")
    size: int = Field(..., ge=0, description="Размер файла в байтах")
    duration: float = Field(..., ge=0, description="Длительность в секундах")
    sample_rate: int = Field(..., description="Частота дискретизации")
    channels: int = Field(..., description="Количество каналов")
    
    class Config:
        arbitrary_types_allowed = True


class WhisperModelConfig(BaseModel):
    """Конфигурация для Whisper модели"""
    size: str = Field(default="small", description="Размер модели Whisper")
    temperature: float = Field(default=0.0, ge=0, le=1, description="Температура для генерации")
    fp16: bool = Field(default=False, description="Использовать FP16")
    device: str | None = Field(default=None, description="Устройство для вычислений")
    
    @field_validator('size')
    def validate_size(cls, v):
        allowed_sizes = settings.MODEL_SIZE
        if v not in allowed_sizes:
            raise ValueError(f'Размер модели должен быть одним из: {allowed_sizes}')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "size": "small",
                "temperature": 0.0,
                "fp16": False,
                "device": "cuda"
            }
        }