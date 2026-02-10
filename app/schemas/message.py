from pydantic import BaseModel, Field



class MessageCreate(BaseModel):
    user_id: int = Field(..., description="ID пользователя")
    text: str = Field(..., description="Распознанный текст")
    processing_time: float = Field(..., ge=0, description="Время обработки в секундах")
