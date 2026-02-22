import logging

from .config import settings
from .transcriber import BaseSTTTranscriber, FasterWhisperSTT


logger = logging.getLogger(__name__)


def get_stt_service() -> BaseSTTTranscriber:
    provider = settings.STT_PROVIDER.lower()

    if provider == "faster_whisper":
        transcriber = FasterWhisperSTT(model_size=settings.MODEL_SIZE)
    else:
        raise ValueError(
            f"Неподдерживаемый STT провайдер: '{provider}'. "
            f"Доступные: faster_whisper"
        )

    logger.info(f"STT провайдер инициализирован: {provider}")
    return transcriber
