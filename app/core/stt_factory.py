import logging

from .config import settings
from .transcriber import BaseSTTTranscriber, WhisperSTT, FasterWhisperSTT


logger = logging.getLogger(__name__)


def get_stt_service() -> BaseSTTTranscriber:
    provider = settings.STT_PROVIDER.lower()

    try:
        if provider == "whisper":
            kwargs = {'model_size': settings.MODEL_SIZE}
            transcriber = WhisperSTT(**kwargs)
        elif provider == "faster_whisper":
            kwargs = {'model_size': settings.MODEL_SIZE}
            transcriber = FasterWhisperSTT(**kwargs)
        else:
            available_providers = ["whisper", "faster_whisper"]
            raise ValueError(
                f"Неподдерживаемый STT провайдер: {settings.STT_PROVIDER}. "
                f"Доступные провайдеры: {available_providers}"
            )

        logger.info(f"Используется {transcriber.get_model_info()['provider']}")
        return transcriber

    except Exception as e:
        logger.error(f"Ошибка создания STT сервиса: {e}")
        raise