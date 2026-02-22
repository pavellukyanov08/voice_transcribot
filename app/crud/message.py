import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models import Message
from app.schemas import MessageCreate


logger = logging.getLogger(__name__)


class AudioRepository:
    def __init__(
        self,
        session: AsyncSession
    ) -> None:
        self._session = session

    async def create_message(self, message_data: MessageCreate) -> None:
        try:
            new_message = Message(**message_data.model_dump())
            self._session.add(new_message)
            await self._session.commit()
            logger.info(
                f"Created new message={new_message.id} for user={new_message.user_id}"
            )
        except Exception as e:
            logger.error(
                f"Failed to create message for user={message_data.user_id}:{e}", exc_info=True
            )
            await self._session.rollback()
            raise
    
    async def get_user_messages(
        self, 
        user_id: int,
        limit: int = 50, 
        offset: int = 0
    ) -> list[Message]:
        result = await self._session.execute(
            select(Message)
            .where(Message.user_id == user_id)
            .order_by(desc(Message.created_at))
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())