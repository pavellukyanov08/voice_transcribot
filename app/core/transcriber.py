from abc import ABC, abstractmethod

import logging
from pathlib import Path
from app.api import OpenRouterClient


logger = logging.getLogger(__name__)


class BaseSTTTranscriber(ABC):
    def __init__(self):
        self.logger = logger
        self._is_initialized = False

    @abstractmethod
    async def transcribe(self, audio_path: Path) -> str | None:
        pass

    def _validate_audio_file(self, audio_path: Path) -> bool:
        if not audio_path.exists():
            self.logger.error(f"Аудиофайл не найден: {audio_path}")
            return False

        if audio_path.stat().st_size == 0:
            self.logger.error(f"Аудиофайл пустой: {audio_path}")
            return False

        return True


class OpenRouterWhisperLargeV3Turbo(BaseSTTTranscriber):
    def __init__(self, open_router_client: OpenRouterClient):
        super().__init__()
        self._open_router_client = open_router_client

    async def transcribe(self, audio_path: Path) -> str | None:
        if not self._validate_audio_file(audio_path):
            return None

        try:
            result = await self._open_router_client.transcribe(audio_path=audio_path)

            if not result:
                self.logger.warning("OpenRouter didn't return transcription result")
                return None

            self.logger.info("Transcription through OpenRouter successfully ended")
            return result

        except Exception as e:
            self.logger.exception("Error while transcribing through OpenRouter =%s", e)
            return None