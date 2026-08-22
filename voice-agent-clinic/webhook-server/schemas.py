"""Strict, dependency-light validation for inbound third-party webhooks."""

from __future__ import annotations

import re
from typing import Any, Mapping

from fastapi import HTTPException

_SID = re.compile(r"^[A-Za-z0-9_-]{1,128}$")
_PHONE = re.compile(r"^\+?[1-9][0-9]{6,14}$")
_CALCOM_EVENTS = {"BOOKING_CREATED", "BOOKING_CANCELLED", "BOOKING_RESCHEDULED"}


def validate_twilio(form: Mapping[str, Any], *, require_status: bool = False) -> dict[str, str]:
    call_sid = str(form.get("CallSid", ""))
    if not _SID.fullmatch(call_sid):
        raise HTTPException(422, "CallSid is required and must be <= 128 safe characters")
    if require_status:
        status = str(form.get("CallStatus", ""))
        if status not in {"queued", "ringing", "in-progress", "completed", "busy", "failed", "no-answer"}:
            raise HTTPException(422, "CallStatus is invalid")
        return {"CallSid": call_sid, "CallStatus": status, "CallDuration": str(form.get("CallDuration", "0"))}
    from_phone, to_phone = str(form.get("From", "")), str(form.get("To", ""))
    if not _PHONE.fullmatch(from_phone) or not _PHONE.fullmatch(to_phone):
        raise HTTPException(422, "From and To must be phone numbers")
    return {"CallSid": call_sid, "From": from_phone, "To": to_phone}


def validate_calcom(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise HTTPException(422, "Webhook payload must be a JSON object")
    event = payload.get("triggerEvent")
    if event not in _CALCOM_EVENTS:
        raise HTTPException(422, "Unsupported Cal.com triggerEvent")
    body = payload.get("payload")
    if not isinstance(body, dict) or not isinstance(body.get("booking"), dict):
        raise HTTPException(422, "Cal.com booking payload is required")
    return payload
