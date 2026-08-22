"""CPU-compatible local Whisper STT adapter."""

from __future__ import annotations

import asyncio
import io
from typing import Any, Callable, Optional


class LocalWhisperSTTEngine:
    """Small contract-compatible adapter around faster-whisper.

    Model loading is lazy and injectable so imports and CI do not require a GPU or
    download model weights.
    """

    def __init__(self, model: str = "base", device: str = "cpu", compute_type: str = "int8", *, model_factory: Optional[Callable[..., Any]] = None) -> None:
        if model_factory is None:
            try:
                from faster_whisper import WhisperModel
            except ImportError as exc:
                raise RuntimeError("Local Whisper is optional. Install faster-whisper to enable it.") from exc
            model_factory = WhisperModel
        self.model = model_factory(model, device=device, compute_type=compute_type)

    async def transcribe(self, audio: bytes, language: str = "en") -> str:
        if not audio:
            return ""
        segments, _ = await asyncio.to_thread(self.model.transcribe, io.BytesIO(audio), language=language)
        return " ".join(segment.text.strip() for segment in segments).strip()

    async def connect(self, on_transcript: Callable[[str, bool], Any]) -> None:
        self._on_transcript = on_transcript

    async def send_audio(self, audio: bytes) -> None:
        transcript = await self.transcribe(audio)
        if transcript:
            result = self._on_transcript(transcript, True)
            if hasattr(result, "__await__"):
                await result

    async def close(self) -> None:
        return None
