# Squad Team

> genai-summarizer-web-app

## Coordinator

| Name | Role | Notes |
|------|------|-------|
| Squad | Coordinator | Routes work, enforces handoffs and reviewer gates. |

## Members

| Name | Role | Charter | Status |
|------|------|---------|--------|
| Scribe | Documentation | `.squad/agents/scribe/charter.md` | Active |
| Ralph | Persistent Memory / Monitor | `.squad/agents/ralph/charter.md` | Active |

## Project Context

- **Project:** genai-summarizer-web-app
- **Owner:** Jim (durangogt)
- **Language:** Python 3.8+
- **Stack:** FastAPI/Starlette backend, Jinja2 templates frontend, GitHub Models API (gpt-4o)
- **Entry point:** `run.py`
- **Backend:** `backend/app/` — api.py, ui.py, summarizer/engine.py, summarizer/utils.py
- **Tests:** `backend/tests/` — run with `pytest backend/tests/`
- **Deployment target:** Azure Web App / local
- **Created:** 2026-03-24
- **Orchestrator:** JJ (OpenClaw) — decomposes tasks, monitors PRs, routes feature requests to Squad
