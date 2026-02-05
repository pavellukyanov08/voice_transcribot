import asyncio
import logging
import time
from pathlib import Path

from pydub import AudioSegment

from app.core import voice_transcribot, settings, WhisperSTT
from app.schemas import (
    VoiceMessageRequest,
    AudioProcessingResult,
    MessageCreate,
)
from app.crud import MessageRepository


logger = logging.getLogger(__name__)


class MessageService:
    def __init__(self, message_repo: MessageRepository):
        self.logger = logger
        self._message_repo = message_repo
        self.audio_dir = Path(settings.AUDIO_DIR)
        self.audio_dir.mkdir(exist_ok=True)
        self.whisper = WhisperSTT(model_size=settings.MODEL_SIZE)

    async def process_voice_message(
        self, 
        voice_request: VoiceMessageRequest, 
        user_id: int,
        save_to_db: bool = True
    ) -> AudioProcessingResult:
        start_time = time.time()
        ogg_path = None
        wav_path = None

        try:
            ogg_path = await self._download_voice_file(voice_request.file_id)
            if not ogg_path:
                return AudioProcessingResult(
                    success=False,
                    error_message="Не удалось скачать голосовой файл"
                )

            audio_path = ogg_path

            text = await self.whisper.transcribe(audio_path)
            if not text:
                wav_path = await self._convert_audio(ogg_path)
                if not wav_path:
                    return AudioProcessingResult(
                        success=False,
                        error_message="Не удалось конвертировать аудиофайл"
                    )

                text = await self.whisper.transcribe(wav_path)

            processing_time = time.time() - start_time
            
            if text:
                result = AudioProcessingResult(
                    success=True,
                    text=text,
                    processing_time=processing_time,
                )
                
                if save_to_db:
                    await self._save_transcription_to_db(
                        user_id, text, processing_time
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
            self._cleanup_files([ogg_path, wav_path])

    async def _download_voice_file(self, file_id: str) -> Path | None:
        try:
            file = await voice_transcribot.get_file(file_id)
            ogg_path = self.audio_dir / f"{file_id}.ogg"
            
            await voice_transcribot.download_file(file.file_path, destination=ogg_path)
            self.logger.info(f"Файл скачан: {ogg_path}")
            
            return ogg_path
            
        except Exception as e:
            self.logger.exception(f"Ошибка при скачивании файла {file_id}")
            return None

    async def _convert_audio(self, ogg_path: Path) -> Path | None:
        try:
            wav_path = ogg_path.with_suffix(".wav")

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._convert_sync, ogg_path, wav_path)

            self.logger.info(f"Файл сконвертирован: {wav_path}")
            return wav_path

        except Exception as e:
            self.logger.exception(f"Ошибка при конвертации файла {ogg_path}")
            return None

    @staticmethod
    def _convert_sync(ogg_path: Path, wav_path: Path):
        audio = AudioSegment.from_file(ogg_path, format="ogg")
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio = audio.normalize()
        audio.export(wav_path, format="wav")

    def _cleanup_files(self, file_paths: list[Path | None]):
        """Удаляет временные файлы"""
        for path in file_paths:
            if path and path.exists():
                try:
                    path.unlink()
                    self.logger.debug(f"Удален временный файл: {path}")
                except Exception as e:
                    self.logger.warning(f"Не удалось удалить файл {path}: {e}")

    async def _save_transcription_to_db(
        self, 
        user_id: int,
        text: str, 
        processing_time: float, 
    ):
        try:
            message_data = MessageCreate(
                text=text,
                processing_time=processing_time,
                user_id=user_id
            )
            await self._message_repo.create_message(message_data=message_data)
            self.logger.info(f"Транскрипция сохранена в БД для пользователя {user_id}")
                
        except Exception as e:
            self.logger.exception(f"Ошибка при сохранении транскрипции в БД: {e}")
