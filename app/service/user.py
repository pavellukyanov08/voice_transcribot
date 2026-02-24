import logging

from app.schemas import UserRead, UserCreate
from app.crud import UserRepository

logger = logging.getLogger(__name__)


class UserService:
    def __init__(
        self,
        user_repo: UserRepository
    ) -> None:
        self._user_repo = user_repo

    async def create_user(
        self,
        telegram_id: int,
        name: str,
    ) -> None:
        try:
            await self._user_repo.create_user(
                UserCreate(
                    telegram_id=telegram_id,
                    name=name,
                )
            )
        except Exception as e:
            logger.error(f"Failed to create user with TG id {telegram_id}: {e}")
            return

    async def get_user(
        self,
        *,
        telegram_id: int
    ) -> UserRead | None:
        user = await self._user_repo.get_user_by_tg_id(telegram_id)
        if user is None:
            return None
        return UserRead.model_validate(user, from_attributes=True)