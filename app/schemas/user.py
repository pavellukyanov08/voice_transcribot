from datetime import datetime
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    name: str | None = Field(default=None, description="Name of user in Telegram")


class UserCreate(UserBase):
    telegram_id: int = Field(..., description="Telegram ID of user")
    created_at: datetime = Field(..., description="Created time of user")


class UserRead(UserBase):
    telegram_id: int = Field(..., description="Telegram ID of user")
    name: str | None = Field(default=None, description="Name of user in Telegram")
    created_at: datetime = Field(..., description="User created at")
    updated_at: datetime = Field(..., description="Update time of User")


