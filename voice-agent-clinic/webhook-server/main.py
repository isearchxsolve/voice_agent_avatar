"""
Webhook server — FastAPI app for Twilio voice webhooks and Cal.com event callbacks.
"""

import logging
import os
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse

from routes.twilio import handle_incoming_call, handle_status_callback
from routes.calcom import handle_booking_created, handle_booking_cancelled
from schemas import validate_calcom, validate_twilio

logger = logging.getLogger("webhook_server")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Webhook server starting up")
    yield
    logger.info("Webhook server shutting down")


app = FastAPI(title="Voice Agent Clinic Webhook Server", lifespan=lifespan)
_processed_events: set[str] = set()
MAX_WEBHOOK_BYTES = 64 * 1024


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    if int(request.headers.get("content-length", "0") or 0) > MAX_WEBHOOK_BYTES:
        raise HTTPException(413, "Webhook payload too large")
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/webhooks/twilio/voice")
async def twilio_voice(request: Request):
    """Incoming call webhook from Twilio."""
    form = await request.form()
    # Convert MultiDict to plain dict
    form_dict = validate_twilio({key: value for key, value in form.items()})
    if form_dict["CallSid"] in _processed_events:
        return PlainTextResponse("<?xml version=\"1.0\"?><Response/>", media_type="text/xml")
    _processed_events.add(form_dict["CallSid"])
    result = await handle_incoming_call(form_dict)
    return PlainTextResponse(result, media_type="text/xml")


@app.post("/webhooks/twilio/status")
async def twilio_status(request: Request):
    """Call status callback from Twilio."""
    form = await request.form()
    await handle_status_callback(validate_twilio(dict(form), require_status=True))
    return PlainTextResponse("OK")


@app.post("/webhooks/calcom/booking")
async def calcom_booking(request: Request):
    """Cal.com booking event webhook."""
    try:
        payload = validate_calcom(await request.json())
    except ValueError as exc:
        raise HTTPException(422, "Malformed JSON") from exc
    event_id = str(payload["payload"]["booking"].get("uid", "")) + ":" + payload["triggerEvent"]
    if event_id in _processed_events:
        return JSONResponse({"received": True, "duplicate": True})
    _processed_events.add(event_id)
    event_type = payload.get("triggerEvent")
    if event_type == "BOOKING_CREATED":
        await handle_booking_created(payload)
    elif event_type == "BOOKING_CANCELLED":
        await handle_booking_cancelled(payload)
    elif event_type == "BOOKING_RESCHEDULED":
        from routes.calcom import handle_booking_rescheduled
        await handle_booking_rescheduled(payload)
    else:
        logger.info(f"Unhandled Cal.com event: {event_type}")
    return JSONResponse({"received": True})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
