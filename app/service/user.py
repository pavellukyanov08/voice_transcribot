import logging

from app.schemas import UserRead, UserCreate
from app.crud import UserRepository
from app.utils import DateTimeManager

logger = logging.getLogger(__name__)


class UserNotFoundError(Exception):
    pass


class UserAlreadyExists(Exception):
    pass


class UserServiceError(Exception):
    pass


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
    ) -> UserRead:
        created_at = DateTimeManager.get_now_utc()
        try:
            existing_user = await self._user_repo.get_user_by_tg_id(telegram_id)
            if existing_user:
                await self._user_repo.update_user_status(telegram_id)
                return existing_user

            user = await self._user_repo.create_user(
                UserCreate(
                    telegram_id=telegram_id,
                    name=name,
                    created_at=created_at,
                )
            )
            return user
        except Exception as e:
            logger.error(f"Failed to create user with TG id {telegram_id}: {e}")
            raise UserServiceError(f"Failed to create user: {str(e)}") from e

    async def get_user(
        self,
        *,
        telegram_id: int
    ) -> UserRead | None:
        return await self._user_repo.get_user_by_tg_id(telegram_id)

    async def is_user_active(self, telegram_id: int) -> bool:
        user = await self._user_repo.get_user_by_tg_id(telegram_id)
        return user.is_active if user else False
