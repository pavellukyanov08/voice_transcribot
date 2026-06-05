import logging

from .config import settings
from .transcriber import BaseSTTTranscriber, OpenRouterWhisperLargeV3Turbo
from .generator import BaseTextGenerator, OpenRouterDeepSeekV4Flash
from app.api import OpenRouterClient


logger = logging.getLogger(__name__)


def get_stt_transcriber() -> BaseSTTTranscriber:
    logger.info(f"STT провайдер инициализирован:")
    return OpenRouterWhisperLargeV3Turbo(
            open_router_client=OpenRouterClient(
                api_key=settings.OPEN_ROUTER_API_KEY,
            )
        )

def get_text_generator() -> BaseTextGenerator:
    logger.info(f"Провайдер генератора текста ")

    return OpenRouterDeepSeekV4Flash(
            open_router_client=OpenRouterClient(
                api_key=settings.OPEN_ROUTER_API_KEY,
            )
        )
