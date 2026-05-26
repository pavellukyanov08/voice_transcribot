import base64
from pathlib import Path

import httpx


class OpenRouterClient:
    def __init__(self, *, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url="https://openrouter.ai/api/v1",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=120,
            http2=True,
        )

    async def transcribe(self, audio_path: Path):
        audio_bytes = audio_path.read_bytes()
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

        payload = {
            "input_audio": {
                "data": audio_b64,
                "format": audio_path.suffix.replace(".", ""),
            },
            "model": "openai/whisper-large-v3-turbo",
            "language": "ru",
        }
        response = await self.client.post(
            "/audio/transcriptions",
            json=payload,
        )
        response.raise_for_status()
        result = response.json()
        return result.get("text")