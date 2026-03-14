# Current Active Backlog

Date: March 14, 2026

This document summarizes the remaining high-value work in the repository based on the current live codebase, recent documentation cleanup, and the latest validated test baseline.

## Validated Current State

- Active backend runtime is the modular Flask application under `app/`.
- Active async/runtime task path is `app/celery_config.py` plus `app/tasks.py`.
- Historical split-service material under `services/` is mostly archival/reference documentation.
- Latest strong test baseline: `146 passed, 1 skipped`.

## Priority 1: Production Deployment Readiness

Status: Not code-complete, mostly operations work.

What remains:
- Execute the deployment and infrastructure steps in `PRE_LAUNCH_IMPLEMENTATION_CHECKLIST.md`.
- Finalize production secrets, TLS, web server configuration, logging, monitoring, backups, and rollback procedures.
- Choose and verify one real deployment path instead of keeping multiple unverified options in parallel.

Evidence:
- `PRE_LAUNCH_IMPLEMENTATION_CHECKLIST.md` is effectively an unexecuted checklist rather than a completed deployment record.

Why this matters:
- The repo has substantial backend capability already, but production readiness still depends on environment setup and operational verification rather than additional feature coding.

## Priority 2: Fix Phase 15 Integration Gaps

Status: Partially implemented, not fully wired through the active runtime.

### 2.1 WebSocket startup wiring

Status: Core runtime integration completed on March 14, 2026.

Completed:
- `app/__init__.py` now initializes the Flask-SocketIO path from `websocket_events.py` during `create_app()`.
- The initialized Socket.IO server is attached to the Flask app for runtime use and test access.
- Legacy job-watch handling now lives directly in `websocket_events.py`, so `services/websocket.py` has been removed as a duplicate module.
- `websocket_events.py` now owns both collaboration events and job-update watch events inside the active Socket.IO runtime.
- Dependency declarations now include `Flask-SocketIO` in both `requirements.txt` and `pyproject.toml` extras.

Validated:
- Focused pytest results:
- `6 passed in 3.51s` for the initial runtime wiring plus nearby Phase 15 route registration coverage.
- `4 passed in 3.13s` for shared Socket.IO runtime coverage plus API docs smoke tests after attaching legacy job-update handlers.
- `11 passed in 3.84s` for WebSocket, API docs, active upload routes, and active email service coverage after duplicate-file removal.

Remaining follow-up:
- The active runtime now covers both collaboration events and legacy job-update watch events; the remaining work here is documentation depth rather than runtime wiring.

### 2.2 Outbound email service/task path

Status: Core interface cleanup completed on March 14, 2026.

Completed:
- `app/services/email_service.py` now exposes a real `send(...)` interface while preserving `send_email(...)` compatibility.
- The service now resolves both `MAIL_FROM` and `MAIL_FROM_ADDRESS` and supports SMTP configuration when present.
- `app/tasks.py` now calls the real email service interface instead of a missing method.
- `app/services/reports.py` now implements `send_daily_report(...)`, which unblocks the scheduled daily report task path.

Validated:
- Focused pytest result: `4 passed in 2.20s` for `test_email_service_integration.py`.

Remaining follow-up:
- Collaboration notification events still create persisted in-app notifications in `app/services/phase15_service.py`, but they do not yet enqueue outbound email for those events.
- Real provider configuration and delivery policy decisions are still part of production deployment work.

### 2.3 Root prototype duplicates removed from active runtime

Status: Duplicate helper files removed on March 14, 2026.

Completed:
- `services/websocket.py` has been removed after merging job-update watch logic into `websocket_events.py`.
- `file_upload_handler.py` has been removed instead of being kept as a parallel upload implementation.
- `email_notifications.py` has been removed instead of being kept as a second notification delivery path.

Why this matters:
- The active runtime is now clearer: real-time events live in `websocket_events.py`, uploads live in `app/api/routes/uploads.py`, and outbound email lives in `app/services/email_service.py`.

Remaining follow-up:
- Keep future work on the modular `app/` runtime only and avoid reintroducing root-level alternative implementations.

## Priority 3: Package Upload Route Drift

Status: Core cleanup completed on March 14, 2026.

Completed:
- `app/api/routes/uploads.py` no longer depends on `server.py` helpers for upload status, API key checks, or chunk directory resolution.
- Temporary download responses are now buffered before cleanup so the route no longer depends on on-disk files surviving after the response is returned.
- Direct test coverage now exists for `upload-chunk`, `convert-uploaded`, `upload-status`, and `admin/purge-uploads` in `test_upload_routes_package.py`.

Validated:
- Focused pytest result: `3 passed in 2.36s` for `test_upload_routes_package.py`.

Follow-up:
- Keep package upload flows on the modular `app/` path and avoid reintroducing `server.py` dependencies into these endpoints.

## Priority 4: Add Real API Documentation

Status: Core OpenAPI and Swagger integration completed on March 14, 2026.

Completed:
- `app/api/routes/docs.py` now generates a live OpenAPI 3.0 document from the active Flask route map.
- The active app factory now serves the generated spec at `/api/openapi.json`.
- Swagger UI is now registered at `/api/docs` against the live spec rather than a stale static artifact.
- The generated spec now includes reusable component schemas, tag descriptions, route-specific request bodies, richer response content, and explicit parameter metadata for key auth, analytics, upload, admin, health, and Phase 15 endpoints.

Validated:
- Focused pytest results:
- `3 passed in 2.54s` for the initial docs integration.
- `11 passed in 3.84s` for the enriched OpenAPI generator together with recent WebSocket, upload, and email coverage.

Remaining follow-up:
- The generated spec now has real structure; the remaining improvement is breadth, meaning more route-specific schemas and examples across the larger admin and collaboration surface.

## Priority 5: Reduce Runtime Duplication

Status: Major structural cleanup completed on March 14, 2026.

Completed:
- The old multi-route legacy `server.py` implementation has been removed.
- `server.py` is now only a thin compatibility launcher that re-exports `app.main.app` and runs that modular app under `__main__`.
- The modular `app/` runtime is now the only supported application implementation surface.

Validated:
- Focused pytest result: `12 passed in 3.27s` for the launcher compatibility path together with recent WebSocket, docs, upload, and email integration coverage.

Why this matters:
- Runtime duplication no longer centers on a second top-level Flask app, which reduces regression risk and makes the modular `app/` runtime the clear source of truth.

Remaining follow-up:
- Keep future runtime changes on the modular `app/` path only.
- Clean up any stale documentation or operator habits that still assume `server.py` contains independent route logic.

## Priority 6: Normalize Stale Status Docs

Status: Documentation debt, not core code debt.

Evidence:
- Some older review and roadmap docs still claim missing models, middleware, migrations, or rate limiting even though those now exist in `app/`.
- Recent cleanup fixed high-signal runtime docs, but status/roadmap docs still contain stale implementation claims.

Why this matters:
- These files can mislead future maintenance work and duplicate already-completed effort.

Recommended next step:
- Update or archive stale review/roadmap docs so they no longer conflict with the validated runtime and test baseline.

## Suggested Execution Order

1. Execute a real deployment track from the pre-launch checklist.
2. Expand OpenAPI coverage across more of the admin and collaboration surface.
3. Clean up stale roadmap and status docs.
