from typing import AsyncGenerator

from app.core.db import AsyncSessionLocal
from app.crud import UserRepository
from app.service import UserService


async def get_user_service() -> AsyncGenerator[UserService, None]:
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        yield UserService(user_repo)