from abc import ABC, abstractmethod

import logging
from app.api import OpenRouterClient

logger = logging.getLogger(__name__)


class BaseTextGenerator(ABC):
    def __init__(self):
        self.logger = logger
        self._is_initialized = False

    @abstractmethod
    async def process_text(self, content: str) -> str | None:
        pass


class OpenRouterDeepSeekV4Flash(BaseTextGenerator):
    def __init__(self, open_router_client: OpenRouterClient):
        super().__init__()
        self._open_router_client = open_router_client

    async def process_text(self, content: str) -> str | None:
        try:
            result = await self._open_router_client.generate_text(content=content)
            if not result:
                self.logger.warning("OpenRouter didn't return generated text")
                return None

            self.logger.info("Generation through OpenRouter successfully ended")
            return result
        except Exception as e:
            self.logger.exception("Error while generating through OpenRouter =%s", e)
            return None
