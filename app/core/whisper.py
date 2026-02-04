import torch
import whisper
import asyncio
import logging
from pathlib import Path


logger = logging.getLogger(__name__)


class WhisperSTT:
    def __init__(self, model_size: str = 'small'):
        self.model_size = model_size
        self.model = None
        self.logger = logger
        self._load_model()

    def _load_model(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.logger.info(f"Загружаем модель Whisper '{self.model_size}' на устройство: {device}")
        
        self.model = whisper.load_model(
            self.model_size,
            device=device
        )

    async def transcribe(self, audio_path: Path) -> str | None:
        """
        Асинхронная транскрипция аудиофайла
        
        Args:
            audio_path: Путь к аудиофайлу
            language: Язык для распознавания
            
        Returns:
            Распознанный текст или None в случае ошибки
        """
        if not audio_path.exists():
            self.logger.error(f"Аудиофайл не найден: {audio_path}")
            return None
            
        try:
            # Выполняем транскрипцию в отдельном потоке
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self._transcribe_sync, 
                str(audio_path),
            )
            
            text = result.get("text", "").strip()
            self.logger.info(f"Транскрипция завершена. Длина текста: {len(text)} символов")
            
            return text if text else None
            
        except Exception as e:
            self.logger.exception(f"Ошибка при транскрибации файла {audio_path}")
            return None

    def _transcribe_sync(self, audio_path: str) -> dict:
        """Синхронная транскрипция для выполнения в executor"""
        return self.model.transcribe(
            audio_path,
            temperature=0.0,
            fp16=False,
        )
