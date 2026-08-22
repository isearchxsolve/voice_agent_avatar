# Fleet Worklog

### [step 1] Audited project inputs
- Read `../AUDIT_REPORT.md` and `../instructions.txt` without reading or exposing any `.env` values.
- The initial inventory command could not use `rg` because it is unavailable in this Windows environment (PowerShell reported: `rg : The term 'rg' is not recognized`).
- Next: inventory the repository with PowerShell and implement the critical audit fixes first.

### [step 2] Established baseline
- Inventory confirmed the audit's critical webhook files, package markers, JSON onboarding file, FAQ arrays, cached retriever, and corrected dental prompt are already present in this checkout.
- Baseline suite: `python -m pytest -q` exited 0 with `14 passed in 5.25s`; collection was 14 cases, far below the required 1,000.
- Next: replace the paid default LiveKit pipeline with an optional-provider free stack and add health, validation, cleanup, and regression coverage.

### [step 3] Free-stack and webhook hardening applied
- Added the dependency-lazy CPU-safe F5-TTS adapter, local Whisper adapter, corrected bridge `VoiceAgent` wiring, and made paid avatar/LiveKit providers explicit compatibility paths.
- Added webhook payload validation, bounded request size, request IDs, in-memory idempotency, non-root containers, compose-v2 build contexts, and a health-sidecar implementation.
- Verification found a real compatibility blocker: importing `agent.main` failed with `ModuleNotFoundError: No module named 'livekit.agents'`; next is lazy LiveKit loading so the free default remains importable.

### [step 4] Regression matrix passes
- Added `tests/unit/test_production_matrix.py` and `pytest.ini`; it exercises non-trivial chunk boundaries, punctuation, PII/injection inputs, webhook contracts, vertical records, metadata, F5 CPU behavior, and local STT callbacks.
- `python -m pytest --collect-only -q` reported `1289 tests collected`; full `python -m pytest -q` exited 0 with `1289 passed in 9.01s`.
- Next: finish widget, documentation, CI, and container/deployment validation.

### [step 5] Widget dependency blocker identified
- Added a pure remote-avatar-track selector, Vitest contracts, fixed stale hook method names, and made HeyGen an explicit paid fallback flag.
- Initial `npm install --package-lock-only` failed: `@daily-co/daily-react@0.21.0` requires `@daily-co/daily-js >=0.68.0 <1`, but `package.json` specified `0.66.0`; consequently `npm ci`, test, and build could not execute.
- Next: align the Daily peer dependency, generate `package-lock.json`, then run the widget test/build gates.

### [step 6] Widget build surfaced missing transitive runtime dependency
- After aligning Daily, lockfile creation and `npm ci` succeeded; Vitest passed `2/2` avatar-track contracts.
- Vite then failed resolving `jotai/utils` from `@daily-co/daily-react`; npm also reported 3 dependency vulnerabilities (1 moderate, 1 high, 1 critical), so this is not marked complete.
- Next: add the required Jotai runtime dependency, rebuild, and review the remaining audit report without applying forced breaking upgrades.

### [step 7] Widget gate and operational artifacts completed
- Added `jotai` to satisfy Daily React's runtime import; `npm ci`, Vitest (`2/2`), and Vite production build all passed. Runtime-only npm audit returned `0 vulnerabilities`; dev-tree audit still reports 3 toolchain findings.
- Added root README, `.env.example`, CI workflow, audit-to-test `FIX_LOG.md`, pinned bridge dependencies, corrected outreach net-ROI formula, compose/container hardening, and `.dockerignore` to prevent `.env` from entering an image context.
- Next: run final Python/smoke/widget/compose validation and inspect failures without printing environment values.

### [step 8] Final Python gates passed; Compose was made clean-clone safe
- Final checks passed: import/compile gate, `1289 passed in 6.97s`, and smoke `50 passed, 1239 deselected in 1.94s`.
- `docker compose ... config --quiet` initially failed because this workspace has no `.env` file; no `.env` contents were read or printed. Compose now uses supported optional `env_file` entries, while still loading deployment credentials when present.
- Next: validate Compose again and run final widget/config gates.

### [step 9] Compose validation passed; final command-location error recorded
- `docker compose -f infra/docker-compose.yml config --quiet` completed successfully and the Python suite again passed `1289/1289` in `10.71s`.
- The combined command then ran `npm ci` from the repository root, where no `package.json` exists (`ENOENT ... voice-agent-clinic\\package.json`); this did not test the widget and is recorded as operator-command error.
- Next: run the same npm gates from `web-widget/`, then perform final source/config checks.

### [step 10] Final widget gate passed
- From `web-widget/`, `npm ci` completed, Vitest passed `2/2`, and Vite built the production ES/UMD bundles successfully in `3.61s`.
- The default bridge no longer creates a browser demo file at import/runtime; its optional demo route is disabled unless explicitly enabled.
- Next: add final HTTP endpoint regression coverage and run the complete release gates one final time.

### [step 11] Endpoint regression exposed a metrics fallback bug
- The added `/health` + `/metrics` FastAPI contract test found that missing `prometheus_client` caused `/metrics` to raise `NameError: CONTENT_TYPE_LATEST is not defined`; full suite was therefore `1 failed, 1289 passed` and smoke was `1 failed, 50 passed`.
- Added the standards-compliant plaintext Prometheus content type for the no-library fallback; production requirements still install `prometheus-client`.
- Next: rerun all release gates and confirm the fallback is actually responsive.

### [step 12] Release gates passed; Docker daemon unavailable for image build
- Final release checks passed: `1290 passed in 8.62s`, smoke `51 passed, 1239 deselected in 2.36s`, `py_compile`, and `docker compose ... config --quiet` all exited 0.
- Non-secret scan (excluding `.env*` without reading it) reported `secret-pattern-files=0` for common private-key/API-token signatures.
- `docker compose ... build` could not run because Docker Desktop's Linux engine is unavailable: `open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified`. This is an external verification blocker; images were not falsely marked built.

### [step 13] Added remaining cache, cleanup, and prompt contracts
- Added concrete checks that the retriever performs one directory load per instance, unconfigured function providers fail clearly and close every HTTP client, and all five prompts serialize safely to JSON.
- Next: rerun the final suite after these last regression additions; the Docker daemon blocker remains unchanged.

### [step 14] Final regression and configuration verification
- Final full suite passed: `1293 passed in 10.54s`; smoke passed: `51 passed, 1242 deselected in 1.79s`.
- `docker compose -f infra/docker-compose.yml config --quiet` exited 0 after the final changes.
- Delivery is complete subject only to the external Docker-engine image-build verification blocker recorded in step 12.
