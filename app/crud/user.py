import logging
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import UserCreate, UserRead
from app.models import User
from app.utils import DateTimeManager


logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(
            self,
            postgres_session: AsyncSession
    ) -> None:
        self._session = postgres_session

    async def get_user_by_tg_id(self, telegram_id: int) -> UserRead | None:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            return None
        return UserRead.model_validate(user, from_attributes=True)

    async def create_user(self, user_data: UserCreate) -> UserRead:
        try:
            new_user = User(**user_data.model_dump())
            self._session.add(new_user)
            await self._session.commit()
            await self._session.refresh(new_user)
            logger.info(
                f"Created new user={user_data.telegram_id}"
            )
            return UserRead.model_validate(new_user, from_attributes=True)
        except Exception as e:
            logger.error(
                f"Failed to create user={user_data.telegram_id}: {e}", exc_info=True)
            await self._session.rollback()
            raise

    async def update_user_status(
        self,
        telegram_id: int,
        is_active: bool = True
    ) -> None:
        updated_at = DateTimeManager.get_now_utc()
        stmt = (
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(is_registered=is_active, updated_at=updated_at)
        )
        await self._session.execute(stmt)
        await self._session.commit()

