"""
Avatar integration for HeyGen / D-ID streaming avatars.
Triggers speech, expressions, and streams during voice calls.
"""

import httpx
import json
import logging
from typing import Optional

logger = logging.getLogger("avatar")


class AvatarFunctions:
    """HeyGen streaming avatar API wrapper."""

    def __init__(self, api_key: str, avatar_id: str, voice_id: str, base_url: str = "https://api.heygen.com/v1"):
        self.api_key = api_key
        self.enabled = bool(api_key and avatar_id)
        self.avatar_id = avatar_id
        self.voice_id = voice_id
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"X-Api-Key": api_key},
            timeout=30.0,
        )

    async def trigger_speech(self, text: str, expression: str = "friendly") -> dict:
        """
        Send a speech task to the avatar.

        Args:
            text: Text to speak
            expression: Facial expression preset
        Returns:
            Task info with stream URL
        """
        if not self.enabled:
            raise RuntimeError("Paid avatar fallback is not configured")
        payload = {
            "avatar_id": self.avatar_id,
            "text": text,
            "voice_id": self.voice_id,
            "expression": expression,
            "quality": "high",
            "language": "en",
        }
        resp = await self.client.post("/streaming/task", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return {
            "task_id": data.get("task_id"),
            "stream_url": data.get("stream_url"),
            "status": data.get("status", "pending"),
        }

    async def trigger_expression(self, expression: str, duration_seconds: float = 2.0) -> dict:
        """
        Trigger a facial expression without speech.

        Args:
            expression: Expression type (nod, smile, thinking, concerned, surprised)
            duration_seconds: How long to hold the expression
        Returns:
            Status dict
        """
        if not self.enabled:
            raise RuntimeError("Paid avatar fallback is not configured")
        payload = {
            "avatar_id": self.avatar_id,
            "text": ".",  # Minimal text to trigger expression
            "voice_id": self.voice_id,
            "expression": expression,
            "duration": duration_seconds,
        }
        resp = await self.client.post("/streaming/task", json=payload)
        resp.raise_for_status()
        return {"status": "success", "expression": expression}

    async def start_stream(self, session_id: str) -> dict:
        """Start a real-time avatar stream session."""
        if not self.enabled:
            raise RuntimeError("Paid avatar fallback is not configured")
        payload = {
            "avatar_id": self.avatar_id,
            "voice_id": self.voice_id,
            "session_id": session_id,
            "quality": "high",
        }
        resp = await self.client.post("/streaming/start", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return {
            "session_id": data.get("session_id"),
            "webrtc_url": data.get("webrtc_url"),
            "status": data.get("status"),
        }

    async def stop_stream(self, session_id: str) -> dict:
        """Stop an avatar stream session."""
        if not self.enabled:
            raise RuntimeError("Paid avatar fallback is not configured")
        resp = await self.client.post("/streaming/stop", json={"session_id": session_id})
        resp.raise_for_status()
        return {"status": "stopped", "session_id": session_id}

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
