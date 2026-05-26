import logging

from .config import settings
from .transcriber import BaseSTTTranscriber
from app.api import OpenRouterClient


logger = logging.getLogger(__name__)


def get_stt_service() -> BaseSTTTranscriber:
    provider = settings.STT_PROVIDER.lower()

    if provider == "faster_whisper":
        transcriber = FasterWhisperSTT(model_size=settings.MODEL_SIZE)
    elif provider == "open_router":
        transcriber = OpenRouterClient(api_key=settings.OPEN_ROUTER_API_KEY)
    else:
        raise ValueError(
            f"Неподдерживаемый STT провайдер: '{provider}'. "
            f"Доступные: faster_whisper, open_router"
        )

    logger.info(f"STT провайдер инициализирован: {provider}")
    return transcriber
