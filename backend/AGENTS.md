# Backend AGENTS.md

## Overview

- This directory contains the FastAPI backend for the portfolio application.
- The project requires Python 3.12.
- The FastAPI application is defined in `app/main.py`.
- LangGraph and retrieval/LLM logic is defined in `app/agent.py`.

## Environment

- Always use the backend virtual environment at `backend/.venv`.
- Run backend commands from the `backend/` directory.
- Activate the environment before running Python, Uvicorn, or dependency commands:

  ```bash
  source .venv/bin/activate
  ```

- Never read, expose, or commit secrets from `.env.local`.
- Use `.env.example` as the reference for required environment variables.

## Dependencies

- Use the existing `.venv` for all development and verification.
- Keep `pyproject.toml` and `requirements.txt` synchronized when changing dependencies.
- Use Python 3.12 for dependency installation and execution.

## Development

- Start the backend directly with:

  ```bash
  source .venv/bin/activate
  uvicorn app.main:app --reload
  ```

- `dev.sh` builds the frontend and starts Uvicorn on port `8080` with reload enabled.
- The application exposes `GET /health` for a basic health check.
- The primary API endpoint is `POST /api/v1/chat/completions`.

## Code Changes

- Keep backend changes scoped to `backend/` unless the task explicitly requires cross-area changes.
- Preserve the FastAPI application entry point: `app.main:app`.
- Treat changes to `app/agent.py` as changes to the LLM and LangGraph flow.
- Load configuration through environment variables; do not hardcode credentials, API keys, or database settings.

## Verification

- Activate `backend/.venv` before verification.
- Confirm the application imports and starts successfully with Uvicorn.
- Check the health endpoint, for example:

  ```bash
  curl http://localhost:8000/health
  ```

- When relevant, also verify the frontend build performed by `dev.sh`.
