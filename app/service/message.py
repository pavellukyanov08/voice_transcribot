import asyncio
import logging
import time
from pathlib import Path
from pydub import AudioSegment

from app.core import voice_transcribot, settings, WhisperSTT
from app.schemas import (
    VoiceMessageRequest, 
    AudioProcessingResult, 
    TranscriptionMetadata,
    AudioFileInfo,
    MessageCreate
)
from app.crud import MessageRepository


logger = logging.getLogger(__name__)


class MessageService:
    def __init__(self, message_repo: MessageRepository):
        self.logger = logger
        self._message_repo = message_repo
        self.audio_dir = Path(settings.AUDIO_DIR)
        self.audio_dir.mkdir(exist_ok=True)
        self.whisper = WhisperSTT(model_size=settings.WHISPER_MODEL_SIZE)

    async def process_voice_message(
        self, 
        voice_request: VoiceMessageRequest, 
        user_id: int,
        save_to_db: bool = True
    ) -> AudioProcessingResult:
        """
        Полная обработка голосового сообщения: скачивание, конвертация, транскрипция
        
        Args:
            voice_request: Запрос с данными голосового сообщения
            user_id: ID пользователя
            save_to_db: Сохранять ли результат в БД
            
        Returns:
            Результат обработки с текстом или ошибкой
        """
        start_time = time.time()
        ogg_path = None
        mp3_path = None
        
        try:
            ogg_path = await self._download_voice_file(voice_request.file_id)
            if not ogg_path:
                return AudioProcessingResult(
                    success=False,
                    error_message="Не удалось скачать голосовой файл"
                )

            mp3_path, metadata = await self._convert_audio(ogg_path)
            if not mp3_path:
                return AudioProcessingResult(
                    success=False,
                    error_message="Не удалось конвертировать аудиофайл"
                )

            text = await self.whisper.transcribe(mp3_path)
            processing_time = time.time() - start_time
            
            if text:
                result = AudioProcessingResult(
                    success=True,
                    text=text,
                    processing_time=processing_time,
                    confidence=0.95
                )
                
                if save_to_db:
                    await self._save_transcription_to_db(
                        voice_request, user_id, text, processing_time, 0.95
                    )
                
                return result
            else:
                return AudioProcessingResult(
                    success=False,
                    error_message="Не удалось распознать речь в аудиофайле",
                    processing_time=processing_time
                )

        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.exception(f"Ошибка при обработке голосового сообщения {voice_request.file_id}")
            return AudioProcessingResult(
                success=False,
                error_message=f"Внутренняя ошибка: {str(e)}",
                processing_time=processing_time
            )
            
        finally:
            self._cleanup_files([ogg_path, mp3_path])

    async def _download_voice_file(self, file_id: str) -> Path | None:
        """Скачивает голосовой файл из Telegram"""
        try:
            file = await voice_transcribot.get_file(file_id)
            ogg_path = self.audio_dir / f"{file_id}.ogg"
            
            await voice_transcribot.download_file(file.file_path, destination=ogg_path)
            self.logger.info(f"Файл скачан: {ogg_path}")
            
            return ogg_path
            
        except Exception as e:
            self.logger.exception(f"Ошибка при скачивании файла {file_id}")
            return None

    async def _convert_audio(self, ogg_path: Path) -> tuple[Path | None, TranscriptionMetadata | None]:
        try:
            mp3_path = ogg_path.with_suffix(".mp3")
            
            original_info = self._get_audio_info(ogg_path)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._convert_sync, ogg_path, mp3_path)
            
            converted_info = self._get_audio_info(mp3_path)
            
            metadata = TranscriptionMetadata(
                original_format="ogg",
                converted_format="mp3",
                sample_rate=converted_info.sample_rate,
                channels=converted_info.channels,
                duration=converted_info.duration,
                file_size_original=original_info.size,
                file_size_converted=converted_info.size
            )
            
            self.logger.info(f"Файл сконвертирован: {mp3_path}")
            return mp3_path, metadata
            
        except Exception as e:
            self.logger.exception(f"Ошибка при конвертации файла {ogg_path}")
            return None, None

    def _convert_sync(self, ogg_path: Path, mp3_path: Path):
        audio = AudioSegment.from_file(ogg_path, format="ogg")
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(mp3_path, format="mp3")

    def _cleanup_files(self, file_paths: list[Path | None]):
        """Удаляет временные файлы"""
        for path in file_paths:
            if path and path.exists():
                try:
                    path.unlink()
                    self.logger.debug(f"Удален временный файл: {path}")
                except Exception as e:
                    self.logger.warning(f"Не удалось удалить файл {path}: {e}")

    def _get_audio_info(self, audio_path: Path) -> AudioFileInfo:
        try:
            audio = AudioSegment.from_file(audio_path)
            return AudioFileInfo(
                path=audio_path,
                format=audio_path.suffix[1:],
                size=audio_path.stat().st_size,
                duration=len(audio) / 1000.0,
                sample_rate=audio.frame_rate,
                channels=audio.channels
            )
        except Exception as e:
            self.logger.exception(f"Ошибка при получении информации о файле {audio_path}")
            return AudioFileInfo(
                path=audio_path,
                format=audio_path.suffix[1:],
                size=audio_path.stat().st_size if audio_path.exists() else 0,
                duration=0.0,
                sample_rate=16000,
                channels=1
            )

    async def _save_transcription_to_db(
        self, 
        voice_request: VoiceMessageRequest, 
        user_id: int, 
        text: str, 
        processing_time: float, 
        confidence: float
    ):
        try:
            message_data = MessageCreate(
                file_id=voice_request.file_id,
                file_unique_id=voice_request.file_unique_id,
                text=text,
                confidence=confidence,
                processing_time=processing_time,
                user_id=user_id
            )
            await self._message_repo.create_message(message_data=message_data)
            self.logger.info(f"Транскрипция сохранена в БД для пользователя {user_id}")
                
        except Exception as e:
            self.logger.exception(f"Ошибка при сохранении транскрипции в БД: {e}")
