from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    telegram_id: int = Field(..., description="Telegram ID of user")
    name: str | None = Field(default=None, description="Name of user in Telegram")


class UserRead(BaseModel):
    telegram_id: int = Field(..., description="Telegram ID of user")
    name: str | None = Field(default=None, description="Name of user in Telegram")
