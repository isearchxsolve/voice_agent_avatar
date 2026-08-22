"""
Free SOTA engine package.
All engines are zero-cost, self-hostable, with optional GPU acceleration.
"""

from .llm import GeminiEngine, GroqEngine, OllamaEngine
from .tts import KokoroTTSEngine, XTTSEngine
from .f5_tts import F5TTSEngine
from .stt import DeepgramSTTEngine
from .local_stt import LocalWhisperSTTEngine
from .avatar import LivePortraitEngine
from .core import VoiceAgent

__all__ = [
    # LLM
    "GeminiEngine",
    "GroqEngine",
    "OllamaEngine",
    # TTS
    "KokoroTTSEngine",
    "F5TTSEngine",
    "XTTSEngine",
    # STT
    "DeepgramSTTEngine",
    "LocalWhisperSTTEngine",
    # Avatar
    "LivePortraitEngine",
    # Core
    "VoiceAgent",
]
