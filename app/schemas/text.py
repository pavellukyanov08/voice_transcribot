from pydantic import BaseModel, Field


class MessageProcessingResult(BaseModel):
    success: bool = Field(..., description="Успешность генерации")
    generated_text: str | None = Field(default=None, description="Сгенерированный ответ")
    saved_to_db: bool = Field(default=False, description="Флаг успешности сохранения в БД")
    error_message: str | None = Field(default=None, description="Сообщение об ошибке")


class UserRequestText(BaseModel):
    text: str = Field(..., description="Текст запроса пользователя")
