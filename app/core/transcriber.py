from abc import ABC, abstractmethod

import torch
import whisper
import asyncio
import logging
from pathlib import Path
from faster_whisper import WhisperModel

from app.enum.stt_model import STTModel
from .config import settings


logger = logging.getLogger(__name__)


class BaseSTTTranscriber(ABC):
    def __init__(self):
        self.logger = logger
        self._is_initialized = False

    @abstractmethod
    async def transcribe(self, audio_path: Path) -> str | None:
        pass

    @abstractmethod
    def _load_model(self) -> None:
        pass

    @abstractmethod
    def get_model_info(self) -> dict:
        pass

    def _validate_audio_file(self, audio_path: Path) -> bool:
        if not audio_path.exists():
            self.logger.error(f"Аудиофайл не найден: {audio_path}")
            return False

        if audio_path.stat().st_size == 0:
            self.logger.error(f"Аудиофайл пустой: {audio_path}")
            return False

        return True

    @property
    def is_initialized(self) -> bool:
        return self._is_initialized


class SingletonSTTMixin:
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__new__(cls)
        return cls._instances[cls]


def create_transcriber(
    model: STTModel,
    **kwargs
) -> BaseSTTTranscriber:
    if model == STTModel.WHISPER:
        return WhisperSTT(**kwargs)
    elif model == STTModel.FASTER_WHISPER:
        return WhisperSTT(**kwargs)
    else:
        available = [b.value for b in STTModel]
        raise ValueError(
            f"Неподдерживаемая модель: {model.value}. "
            f"Доступные: {available}"
        )


class WhisperSTT(SingletonSTTMixin, BaseSTTTranscriber):
    def __init__(self, model_size: str = settings.MODEL_SIZE):
        if hasattr(self, '_initialized') and self._initialized:
            return

        super().__init__()
        self._model_size = model_size
        self._model = None
        self._load_model()
        self._initialized = True
        self._is_initialized = True

    def _load_model(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.logger.info(f"Загружаем модель Whisper '{self._model_size}' на устройство: {device}")

        self._model = whisper.load_model(
            self._model_size,
            device=device,
            download_root='models',
            in_memory=False
        )

        self._model.eval()

        for param in self._model.parameters():
            param.requires_grad = False

    async def transcribe(self, audio_path: Path) -> str | None:
        if not audio_path.exists():
            self.logger.error(f"Аудиофайл не найден: {audio_path}")
            return None

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._transcribe_sync,
                str(audio_path)
            )

            text = result.get("text", "").strip()
            self.logger.info(f"Транскрипция завершена")

            return text if text else None

        except Exception as e:
            self.logger.exception(f"Ошибка при транскрибации файла {audio_path}")
            return None

    def _transcribe_sync(self, audio_path: str) -> dict:
        return self._model.transcribe(
            audio_path,
            language=settings.WHISPER_LANGUAGE,
            task="transcribe",
            temperature=0.0,
            verbose=False,
            fp16=False,
            condition_on_previous_text=False,
            # vad_filter=True,
        )

    def get_model_info(self) -> dict:
        return {
            "provider": "OpenAI Whisper",
            "model_size": self._model_size,
            "language": "ru",
            "type": "local"
        }


class FasterWhisperSTT(SingletonSTTMixin, BaseSTTTranscriber):
    def __init__(self, model_size: str = settings.MODEL_SIZE):
        if hasattr(self, '_initialized') and self._initialized:
            return

        super().__init__()
        self._model_size = model_size
        self._model = None
        self._load_model()
        self._initialized = True
        self._is_initialized = True

    def _load_model(self):
        if torch.cuda.is_available():
            device = "cuda"
            compute_type = "float16"
        else:
            device = "cpu"
            compute_type = "int8"

        self.logger.info(
            f"Загружаем модель faster-whisper '{self._model_size}' "
            f"на устройство: {device} с типом: {compute_type}"
        )

        self._model = WhisperModel(
            self._model_size,
            device=device,
            compute_type=compute_type,
            download_root='models'
        )

    async def transcribe(self, audio_path: Path) -> str | None:
        if not self._validate_audio_file(audio_path):
            return None

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._transcribe_sync,
                str(audio_path)
            )

            if result:
                self.logger.info("Транскрипция через faster-whisper завершена успешно")
                return result
            else:
                self.logger.warning("faster-whisper не смог распознать речь")
                return None

        except Exception as e:
            self.logger.exception(f"Ошибка при транскрибации через faster-whisper: {e}")
            return None

    def _transcribe_sync(self, audio_path: str) -> str | None:
        """Синхронная транскрипция через faster-whisper."""
        try:
            segments, info = self._model.transcribe(
                audio_path,
                language=settings.WHISPER_LANGUAGE,
                beam_size=5,
                # vad_filter=True,
                vad_parameters={
                    "threshold": 0.5,
                    "min_speech_duration_ms": 250,
                    "min_silence_duration_ms": 2000
                },
                condition_on_previous_text=False,
                temperature=0.0
            )

            text_parts = []
            for segment in segments:
                if segment.text.strip():
                    text_parts.append(segment.text.strip())

            full_text = ' '.join(text_parts).strip()

            if full_text:
                self.logger.debug(
                    f"faster-whisper: язык={info.language} "
                    f"длительность={info.duration:.2f}с"
                )
                return full_text
            else:
                return None

        except Exception as e:
            self.logger.exception(f"Ошибка в _transcribe_sync (faster-whisper): {e}")
            return None

    def get_model_info(self) -> dict:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"

        return {
            "provider": "faster-whisper (CTranslate2)",
            "model_size": self._model_size,
            "language": settings.WHISPER_LANGUAGE,
            "type": "local",
            "device": device,
            "compute_type": compute_type,
            "features": ["VAD filtering", "Beam search", "Optimized inference"]
        }