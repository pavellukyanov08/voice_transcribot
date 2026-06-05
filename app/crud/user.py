import logging

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import UserCreate
from app.models import User


logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(
        self,
        session: AsyncSession
    ) -> None:
        self._session = session

    async def get_user_by_tg_id(self, telegram_id: int) -> User | None:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, user_data: UserCreate) -> None:
        try:
            stmt = (
                insert(User)
                .values(
                    telegram_id=user_data.telegram_id,
                    name=user_data.name
                )
                .on_conflict_do_nothing(
                    index_elements=['telegram_id']
                )
            )
            await self._session.execute(stmt)
            await self._session.commit()
        except Exception as e:
            logger.error(
                f"Failed to create user={user_data.telegram_id}: {e}", exc_info=True)
            await self._session.rollback()
            raise

