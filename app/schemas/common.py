from pydantic import BaseModel, Field


class MessageResult(BaseModel):
    user_id: int = Field(..., description="ID пользователя")
    text: str = Field(..., description="Текст запроса пользователя")
    processing_time: float | None = Field(default=None, ge=0, description="Время обработки в секундах")
