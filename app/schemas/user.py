from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    telegram_id: int = Field(..., description="Telegram ID of user")
    name: str | None = Field(default=None, description="Name of user in Telegram")


class UserRead(BaseModel):
    telegram_id: int = Field(..., description="Telegram ID of user")
    name: str | None = Field(default=None, description="Name of user in Telegram")
    created_at: datetime | None = Field(default=None, description="User created at")
