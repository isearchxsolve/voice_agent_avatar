# Voice Agent Clinic

Production-focused AI receptionist infrastructure for dental, medical, HVAC, legal, and real-estate teams. It handles inbound voice workflows, appointment requests, CRM handoff, notifications, and an optional web avatar while keeping the default runtime on free or self-hosted components.

## Architecture

```
Web widget / telephony webhook
        |                    |
        v                    v
Free WebSocket bridge      FastAPI webhook server
 (ASR -> LLM -> F5 TTS)    (Twilio + Cal.com validation)
        |                    |
        +---- clinic functions / knowledge cache ----+
                         |
          LivePortrait / Kaggle avatar notebook
```

`websocket_bridge.py` is the default runtime. It selects Gemini Flash, F5-TTS, local Whisper, and LivePortrait through `config_free.py`; heavyweight model packages are optional and dependency-lazy so the codebase and CI stay CPU-compatible. Kaggle notebooks under `kaggle/` are the intended hosted GPU execution environment for voice and avatar models. The legacy LiveKit/OpenAI/ElevenLabs path is disabled unless `ALLOW_PAID_PROVIDERS=1` is explicitly set.

## Quick start

1. Copy `.env.example` to `.env` and populate only the environment-variable names needed for your selected providers. Do not put provider credentials in the widget build variables.
2. For the base API/test environment: `python -m pip install -r agent/requirements.txt` and `python -m pip install -r webhook-server/requirements.txt`.
3. Install heavyweight free engines only where they run: `f5-tts` for F5-TTS and `faster-whisper` for local ASR. A GPU Kaggle notebook can host F5-TTS/LivePortrait; set the corresponding notebook bridge URLs in deployment configuration.
4. Start the free bridge with `python websocket_bridge.py`. It refuses unauthenticated WebSocket access unless `VOICE_AGENT_API_KEY` is present.
5. Start webhook handling with `uvicorn main:app --app-dir webhook-server --host 0.0.0.0 --port 8000`.

## Tests and quality gates

```bash
# Full Python release gate: 1,000+ distinct tests
python -m pytest -q

# Fast smoke subset (about 50 cases)
python -m pytest -m smoke -q

# Widget contracts and production bundle
cd web-widget
npm ci
npm run test
npm run build

# Compose syntax (does not print resolved environment values)
docker compose -f infra/docker-compose.yml config --quiet
```

The Python suite is parameterized across 1,289 real inputs: chunk boundaries and overlap, punctuation, high-risk PII, injection attempts, vertical FAQ data, webhook contracts, metadata parsing, and mocked CPU engine interfaces.

## Configuration reference

| Area | Variables |
|---|---|
| Bridge access | `VOICE_AGENT_API_KEY`, `VOICE_LLM_PROVIDER`, `VOICE_TTS_PROVIDER`, `VOICE_STT_PROVIDER`, `VOICE_AVATAR_PROVIDER` |
| Free engines | `GEMINI_API_KEY`, `F5_TTS_REF_AUDIO`, `F5_TTS_DEVICE`, `WHISPER_MODEL`, `WHISPER_DEVICE`, `LIVEPORTRAIT_*` |
| Kaggle hosting | `KAGGLE_VOICE_BRIDGE_URL`, `KAGGLE_AVATAR_BRIDGE_URL` |
| Clinic functions | `CALCOM_API_KEY`, `CALCOM_EVENT_TYPE_ID`, `CRM_WEBHOOK_URL`, `CRM_API_KEY`, `CLINIC_TIMEZONE` |
| Notifications | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `SENDGRID_API_KEY`, `SENDGRID_FROM_EMAIL` |
| Explicit paid fallback | `ALLOW_PAID_PROVIDERS`, `VITE_ENABLE_PAID_HEYGEN` |

Missing optional integrations fail with a clear configured/not-configured response; startup validation reports missing selected-provider inputs by variable name only.

## Deployment

Use Compose v2 from the repository root:

```bash
docker compose -f infra/docker-compose.yml build
docker compose -f infra/docker-compose.yml up -d
```

The bridge exposes `/health`; the LiveKit compatibility worker exposes `/health` and Prometheus `/metrics` on port 8080. The webhook server exposes `/health` on port 8000. `scripts/deploy.sh` uses these probes and exits nonzero on a failed service health check.

## Security posture

- All credentials are environment variables; `.env` is never edited by project tooling.
- Webhook payloads are bounded and validated, include request IDs, and are idempotent in process.
- High-risk PII is redacted before LLM/TTS handling; names and ordinary contact details are not falsely classified as SSN/card data.
- Prompt-injection attempts are blocked before an LLM call.
- The default containers run as a non-root user. Run a secret scanner and use a durable idempotency store before multi-replica deployment.
