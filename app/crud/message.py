import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.models import Message
from app.schemas import MessageCreate


logger = logging.getLogger(__name__)


class AudioRepository:
    def __init__(
        self,
        postgres_session: AsyncSession
    ) -> None:
        self._session = postgres_session

    async def create_message(self, message_data: MessageCreate) -> None:
        try:
            new_message = Message(**message_data.model_dump())
            self._session.add(new_message)
            await self._session.commit()
            await self._session.refresh(new_message)
            logger.info(
                f"Created new message={new_message.id} for user={new_message.user_id}"
            )
        except Exception as e:
            logger.error(
                f"Failed to create message for user={message_data.user_id}:{e}", exc_info=True
            )
            await self._session.rollback()
            raise
    
    async def get_by_id(self, message_id: int) -> Message | None:
        result = await self._session.execute(
            select(Message)
            .options(selectinload(Message.user))
            .where(Message.id == message_id)
        )
        result = result.scalar_one_or_none()
        if not result:
            return None
        return result
    
    async def get_user_messages(
        self, 
        user_id: int,
        limit: int = 50, 
        offset: int = 0
    ) -> list[Message]:
        """Получает сообщения пользователя"""
        result = await self._session.execute(
            select(Message)
            .options(selectinload(Message.user))
            .where(Message.user_id == user_id)
            .order_by(desc(Message.created_at))
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def count_user_messages(self, user_id: int) -> int:
        """Подсчитывает количество сообщений пользователя"""
        result = await self._session.execute(
            select(Message.id).where(Message.user_id == user_id)
        )
        return len(list(result.scalars().all()))