from typing import Optional

import torch
import whisper
import asyncio
import logging
from pathlib import Path

from app.core import settings


logger = logging.getLogger(__name__)


class WhisperSTT:
    _instance: Optional['WhisperSTT'] = None
    _model = None

    def __new__(cls, model_size: str = settings.MODEL_SIZE):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, model_size: str = settings.MODEL_SIZE):
        if self._model is None:
            self.model_size = model_size
            self.logger = logger
            self._load_model()

    def _load_model(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.logger.info(f"Загружаем модель Whisper '{self.model_size}' на устройство: {device}")
        
        self._model = whisper.load_model(
            self.model_size,
            device=device,
            download_root=None,
            in_memory=True
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
        )