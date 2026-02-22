from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor

import torch
import asyncio
import logging
from pathlib import Path
from faster_whisper import WhisperModel

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

    def shutdown(self) -> None:
        pass

class FasterWhisperSTT(BaseSTTTranscriber):
    def __init__(self, model_size: str = settings.MODEL_SIZE):
        super().__init__()
        self._model_size = model_size
        self._model = None
        self._device = None
        self._compute_type = None
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="whisper")
        self._load_model()
        self._is_initialized = True

    def _load_model(self):
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        self._compute_type = "int8_float16"

        self.logger.info(
            f"Загружаем модель faster-whisper '{self._model_size}' "
            f"на устройство: {self._device} с типом: {self._compute_type}"
        )

        self._model = WhisperModel(
            self._model_size,
            device=self._device,
            compute_type=self._compute_type,
            download_root='models',
            num_workers=3,
            cpu_threads=4
        )

    async def transcribe(self, audio_path: Path) -> str | None:
        if not self._validate_audio_file(audio_path):
            return None

        try:
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                self._executor,
                self._transcribe_sync,
                str(audio_path)
            )

            if result:
                self.logger.info("Транскрипция через faster-whisper завершена успешно")
                return result
            else:
                self.logger.warning("faster-whisper не смог распознать речь")
                return None

        except Exception:
            self.logger.exception("Ошибка при транскрибации через faster-whisper")
            return None

    def _transcribe_sync(self, audio_path: str) -> str | None:
        try:
            segments, info = self._model.transcribe(
                audio_path,
                language=settings.WHISPER_LANGUAGE,
                beam_size=1,
                vad_filter=True,
                vad_parameters={
                    "threshold": 0.5,
                    "min_speech_duration_ms": 250,
                    "min_silence_duration_ms": 500
                },
                condition_on_previous_text=False,
                temperature=0.0
            )

            text_parts = [segment.text.strip() for segment in segments if segment.text.strip()]
            full_text = ' '.join(text_parts).strip()

            if full_text:
                self.logger.debug(
                    f"faster-whisper: язык={info.language} "
                    f"длительность={info.duration:.2f}с"
                )
                return full_text
            else:
                return None

        except Exception:
            self.logger.exception("Ошибка в _transcribe_sync (faster-whisper)")
            return None

    def shutdown(self) -> None:
        self._executor.shutdown(wait=True)
