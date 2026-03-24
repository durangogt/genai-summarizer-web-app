# Squad Decisions

## Active Decisions

### 2026-03-24 — Stack & Architecture
**Decision:** Python monorepo — FastAPI/Starlette backend, Jinja2 frontend templates, no separate JS framework.
**Context:** Keeps deployment simple; single `run.py` entry point; targets Azure Web App / local self-host.
**Owner:** Jim (durangogt)

### 2026-03-24 — AI Provider
**Decision:** GitHub Models API for summarization (not OpenAI direct). Auth via GitHub token.
**Context:** Keeps costs on Copilot budget. Model: `gpt-4o` or `gpt-4o-mini` via `https://models.inference.ai.azure.com`.
**Owner:** Jim (durangogt)

### 2026-03-24 — Auth
**Decision:** JWT authentication on REST API endpoints. `python-jose` for token handling.
**Context:** Enables future integrations without exposing the app publicly without auth.

### 2026-03-24 — Batch Processing
**Decision:** Batch upload supports up to 10 files simultaneously, max 10MB each.
**Context:** Documented in `BATCH_PROCESSING_IMPLEMENTATION.md`.

### 2026-03-24 — Testing
**Decision:** pytest for all tests. Coverage targets: API, summarizer engine, auth, history.
**Context:** Tests live in `backend/tests/`. Run via `pytest backend/tests/`.

### 2026-03-24 — Branching & PRs
**Decision:** All feature work via feature branches → PRs. No direct pushes to `main`.
**Context:** Branch protection enabled on `main`. Jim reviews and merges.

### 2026-03-24 — JJ Orchestration
**Decision:** JJ (OpenClaw assistant) acts as high-level orchestrator — decomposes feature requests into Squad tasks, monitors PRs via `gh` CLI, and surfaces summaries to Jim. Squad agents handle implementation.
**Context:** Reduces Anthropic API token spend; Squad runs on Copilot Pro+ budget.

## Governance

- All meaningful changes require team consensus
- Document architectural decisions here
- Keep history focused on work, decisions focused on direction
