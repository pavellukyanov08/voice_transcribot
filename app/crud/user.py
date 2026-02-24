import logging
from sqlalchemy import select, ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import UserCreate, UserRead
from app.models import User


logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(
        self,
        session: AsyncSession
    ) -> None:
        self._session = session

    async def check_user_exists(
        self,
        telegram_id: int,
    ) -> bool:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self._session.execute(stmt)
        row = result.first()
        if row is None:
            return False
        return True

    async def get_user_by_tg_id(self, telegram_id: int) -> User | None:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, user_data: UserCreate) -> None:
        try:
            if not await self.check_user_exists(user_data.telegram_id):
                new_user = User(
                    telegram_id=user_data.telegram_id,
                    name=user_data.name
                )
                self._session.add(new_user)
                await self._session.commit()
        except Exception as e:
            logger.error(
                f"Failed to create user={user_data.telegram_id}: {e}", exc_info=True)
            await self._session.rollback()
            raise

