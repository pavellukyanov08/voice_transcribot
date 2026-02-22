import logging
import time
from pathlib import Path

from app.core import voice_transcribot, settings
from app.core.transcriber import BaseSTTTranscriber
from app.schemas import (
    AudioProcessingResult,
    AudioMessageRequest,
    MessageCreate
)
from app.crud import AudioRepository


logger = logging.getLogger(__name__)
_audio_dir = Path(settings.AUDIO_DIR)


class AudioService:
    def __init__(self, audio_repo: AudioRepository, stt_service: BaseSTTTranscriber):
        self._audio_repo = audio_repo
        self.stt_service = stt_service
        _audio_dir.mkdir(exist_ok=True)

    async def process_audio_message(
        self,
        voice_request: AudioMessageRequest,
        user_id: int,
    ) -> AudioProcessingResult:
        start_time = time.time()
        ogg_path = None

        try:
            ogg_path = await self._download_audio_file(voice_request.file_id)
            if not ogg_path:
                return AudioProcessingResult(
                    success=False,
                    error_message="Не удалось скачать голосовой файл"
                )

            text = await self.stt_service.transcribe(ogg_path)
            processing_time = time.time() - start_time
            if text:
                saved = await self._save_transcription_to_db(
                    text=text,
                    user_id=user_id,
                    processing_time=processing_time
                )

                return AudioProcessingResult(
                    success=True,
                    text=text,
                    processing_time=processing_time,
                    saved_to_db=saved,
                )
            else:
                return AudioProcessingResult(
                    success=False,
                    error_message="Не удалось распознать речь в аудиофайле",
                    processing_time=processing_time
                )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.exception(f"Ошибка при обработке голосового сообщения {voice_request.file_id}")
            return AudioProcessingResult(
                success=False,
                error_message=f"Внутренняя ошибка: {str(e)}",
                processing_time=processing_time
            )

        finally:
            self._cleanup_files(ogg_path)

    @staticmethod
    async def _download_audio_file(file_id: str) -> Path | None:
        try:
            file = await voice_transcribot.get_file(file_id)
            ogg_path = _audio_dir / f"{file_id}.ogg"
            await voice_transcribot.download_file(file.file_path, destination=ogg_path)
            logger.info(f"Файл скачан: {ogg_path}")
            return ogg_path
        except Exception:
            logger.exception(f"Ошибка при скачивании файла {file_id}")
            return None

    @staticmethod
    def _cleanup_files(file_path: Path | None):
        if file_path.exists():
            try:
                file_path.unlink()
                logger.debug(f"Удален временный файл: {file_path}")
            except Exception as e:
                logger.warning(f"Не удалось удалить файл {file_path}: {e}")

    async def _save_transcription_to_db(
        self,
        text: str,
        user_id: int,
        processing_time: float,
    ) -> bool:
        try:
            message_data = MessageCreate(
                text=text,
                processing_time=processing_time,
                user_id=user_id
            )
            await self._audio_repo.create_message(message_data=message_data)
            logger.info(f"Транскрипция сохранена в БД для пользователя {user_id}")
            return True
        except Exception:
            logger.exception("Ошибка при сохранении транскрипции в БД")
            return False
