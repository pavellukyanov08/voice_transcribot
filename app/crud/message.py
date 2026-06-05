import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Message
from app.schemas import MessageResult


logger = logging.getLogger(__name__)


class MessageRepository:
    def __init__(
        self,
        session: AsyncSession
    ) -> None:
        self._session = session

    async def create_message(self, message_data: MessageResult) -> None:
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