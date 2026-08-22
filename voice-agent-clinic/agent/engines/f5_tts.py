"""Dependency-lazy F5-TTS adapter with a CPU-safe interface.

The production image deliberately does not install model weights.  Installing the
optional ``f5-tts`` extra and pointing ``F5_TTS_REF_AUDIO`` at a reference sample
enables the same adapter without changing application code.
"""

from __future__ import annotations

import asyncio
import base64
import io
import logging
from pathlib import Path
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class F5TTSEngine:
    """Synthesize WAV bytes with F5-TTS; CUDA is optional, never required."""

    def __init__(
        self,
        model_path: str = "SWivid/F5-TTS_v1",
        ref_audio_path: str | Path | None = None,
        ref_text: str = "Welcome to our clinic. How can I help you today?",
        device: str = "cuda",
        *,
        load_model_fn: Optional[Callable[..., tuple[Any, Any]]] = None,
        preprocess_fn: Optional[Callable[..., tuple[Any, str]]] = None,
        infer_fn: Optional[Callable[..., tuple[Any, int, Any]]] = None,
        wav_writer: Optional[Callable[[io.BytesIO, Any, int], None]] = None,
        cuda_available: Optional[Callable[[], bool]] = None,
    ) -> None:
        if load_model_fn is None or preprocess_fn is None or infer_fn is None or wav_writer is None:
            try:
                import torch
                import torchaudio
                from f5_tts.infer.utils_infer import infer_process, load_model, preprocess_ref_audio_text
            except ImportError as exc:
                raise RuntimeError(
                    "F5-TTS is optional. Install the f5-tts extra to enable it."
                ) from exc

            cuda_available = cuda_available or torch.cuda.is_available
            load_model_fn = load_model
            preprocess_fn = preprocess_ref_audio_text
            infer_fn = infer_process

            def _write(buffer: io.BytesIO, waveform: Any, sample_rate: int) -> None:
                torchaudio.save(buffer, torch.as_tensor(waveform).unsqueeze(0), sample_rate, format="wav")

            wav_writer = _write

        self.device = device if (cuda_available or (lambda: False))() else "cpu"
        self.model, self.vocoder = load_model_fn(model_path, device=self.device)
        self.ref_audio_path = str(ref_audio_path or "assets/clinic_voice.wav")
        self.ref_text = ref_text
        self._preprocess = preprocess_fn
        self._infer = infer_fn
        self._write_wav = wav_writer
        self._reference: Optional[tuple[Any, str]] = None
        logger.info("F5-TTS initialized on %s", self.device)

    def _get_reference(self) -> tuple[Any, str]:
        if self._reference is None:
            self._reference = self._preprocess(self.ref_audio_path, self.ref_text)
        return self._reference

    async def synthesize(self, text: str, speed: float = 1.0) -> bytes:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("text must be a non-empty string")
        if speed <= 0:
            raise ValueError("speed must be greater than zero")
        reference_audio, reference_text = self._get_reference()
        waveform, sample_rate, _ = await asyncio.to_thread(
            self._infer,
            reference_audio,
            reference_text,
            text,
            model=self.model,
            vocoder=self.vocoder,
            mel_spec_type="vocos",
            speed=speed,
            device=self.device,
        )
        buffer = io.BytesIO()
        self._write_wav(buffer, waveform, sample_rate)
        return buffer.getvalue()

    async def synthesize_base64(self, text: str, speed: float = 1.0) -> str:
        return base64.b64encode(await self.synthesize(text, speed)).decode("ascii")
