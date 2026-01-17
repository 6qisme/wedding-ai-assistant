English | [中文](README.md)
# Wedding AI Assistant 

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-316192?logo=postgresql&logoColor=white)
![OpenAI](https://img.shields.io/badge/AI-OpenAI%20GPT--4-412991?logo=openai&logoColor=white)
![LINE](https://img.shields.io/badge/Platform-LINE%20Messaging%20API-00C300?logo=line&logoColor=white)
![Render](https://img.shields.io/badge/Deployment-Render-46E3B7?logo=render&logoColor=white)

A wedding LINE Bot backend deployed on Render:
- **Seat lookup**: Search guests and their tablemates by name / nickname (PostgreSQL)
- **General Q&A**: Load wedding info (JSON Context) and generate replies via OpenAI
- **Static seat map**: Serve seat map images via FastAPI `/static` (optionally returned when a table is found)

> Key design highlights: **layered environment variables** (local `.env` vs Render Dashboard env vars), **database connection priority**, and **asynchronous LINE webhook handling** (FastAPI `BackgroundTasks`).

---

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Quick Start (Local Development)](#quick-start-local-development)
- [Environment Variables & Layering (Important)](#environment-variables--layering-important)
- [Database (PostgreSQL) Initialization & Guest Import](#database-postgresql-initialization--guest-import)
- [LINE Developers Setup (Webhook)](#line-developers-setup-webhook)
- [Render Deployment (Web Service + PostgreSQL)](#render-deployment-web-service--postgresql)
- [Static Assets (Seat Map)](#static-assets-seat-map)
- [Keep Alive (Optional)](#keep-alive-optional)
- [Troubleshooting](#troubleshooting)

---

## Overview
1. **Health Check**
   - `GET /` → `{"status":"ok","message":"Wedding AI Assistant is alive."}`

2. **LINE Webhook**
   - `POST /webhook`
   - Verifies `X-Line-Signature` (channel secret)
   - Once verified, dispatches processing to background tasks (prevents webhook timeout)

3. **Intent Classification (`intents.py`)**
   - Currently supports `seat_lookup` only
   - If seat lookup → extract keyword → query DB → reply with seating info + (if table found) push seat map URL

4. **Wedding Info Context (`data_provider.py`)**
   - Two sources:
     - `WEDDING_CONTEXT_JSON` (JSON string in env var, recommended for Render)
     - `WEDDING_CONTEXT_PATH` (file path, default `instance/wedding_data.json`, recommended for local dev)

5. **AI Reply (`ai_core.py`)**
   - Uses OpenAI Chat Completions
   - `SYSTEM_PROMPT_PATH` can point to a custom system prompt file (default `prompts/system.txt`)

---

## Architecture

### Workflow Diagram
<p align="center">
  <img src="docs/images/workflow.png" alt="Wedding Bot Workflow" width="900">
</p>

1. User sends a message in LINE
2. LINE Platform calls `/webhook` on Render
3. Backend verifies the signature
4. Background processing: `handle_message()` → (DB lookup or OpenAI call) → `_smart_send()`
5. Reply uses reply token first (cost-efficient / instant); fallback to push on failure
6. If a table is found, also push the seat map URL (`/static/maps/...`)

### Render Environment Variables (Example)
![Render env vars example](docs/images/render-env.png)

### LINE Developers Console (Webhook)
![LINE webhook settings - endpoint](docs/images/line-webhook1.png)
![LINE webhook settings - verification](docs/images/line-webhook2.png)

### End-to-End Demo (LINE chat → Webhook → Reply)
<p align="center">
  <img src="docs/images/demo-line-oa-reply.png" alt="LINE OA Reply Demo" width="1000">
</p>

> Note: Screenshots have been redacted to remove personal data and sensitive credentials (tokens/URLs/IDs).

---

## Tech Stack
- Python + FastAPI + Uvicorn
- line-bot-sdk-python v3 (WebhookParser / MessagingApi)
- PostgreSQL + psycopg2
- OpenAI Python SDK
- Render (Web Service + PostgreSQL)

---

## Quick Start (Local Development)

### 1) Create a virtual environment and install dependencies
```bash
cd wedding-ai-assistant

python -m venv venv

# Windows (CMD):
venv\Scripts\activate.bat

# Windows (PowerShell):
# .\venv\Scripts\Activate.ps1

# macOS/Linux:
# source venv/bin/activate

pip install -r requirements.txt
```

### 2) Create `.env`
```bash
# Windows
copy .env.example .env

# macOS/Linux:
# cp .env.example .env
```

Fill in the required environment variables (at minimum LINE + OpenAI; DB settings depend on your chosen mode).

### 3) Start the local server
```bash
python main.py
# Default: http://127.0.0.1:8000
```

### 4) Test the health check
```bash
curl http://127.0.0.1:8000/
```

To receive LINE webhooks locally, you typically need a public URL (ngrok/Cloudflare Tunnel). For production, deploy on Render.

---

## Environment Variables & Layering (Important)

### Core Principle: use `.env` locally; use Render Dashboard Env Vars in production
- Local development: use `.env` (loaded via `load_dotenv()`)
- Render deployment: **do not commit/upload `.env`**, set env vars in Render Web Service settings
- `.gitignore` already excludes `.env`, `instance/wedding_data.json`, and most static/data files to prevent leaks

### Database connection priority (`db/db_connection.py`)
`get_connection()` uses:
1. `RENDER_DATABASE_URL` (Render internal connection; recommended on Render)
2. `REMOTE_DATABASE_URL` (connect from local machine to Render DB; recommended for maintenance/import)
3. `PG*` variables (local PostgreSQL)

### Wedding context priority (`data_provider.py`)
1. `WEDDING_CONTEXT_JSON` (recommended on Render: no private `wedding_data.json` on disk)
2. `WEDDING_CONTEXT_PATH` (default `instance/wedding_data.json`, recommended locally)

### Environment variables (keep in sync with `.env.example`)

#### LINE
- `LINE_CHANNEL_SECRET`: Messaging API channel secret (signature verification)
- `LINE_CHANNEL_ACCESS_TOKEN`: channel access token (reply/push)

#### OpenAI
- `OPENAI_API_KEY`: OpenAI API Key
- `MODEL_NAME`: default `gpt-4.1-nano`
- `MAX_TOKEN`: default `150`
- `SYSTEM_PROMPT_PATH`: default `prompts/system.txt`

#### Wedding Context
- `WEDDING_CONTEXT_JSON`: JSON string (list of blocks)
- `WEDDING_CONTEXT_PATH`: JSON file path (default `instance/wedding_data.json`)

#### Static
- `STATIC_BASE_URL`: base URL for static assets
  - Local: `http://127.0.0.1:8000/static`
  - Render: `https://<your-service>.onrender.com/static`
- `STATIC_FULL_SEATMAP`: seat map file name under `static/maps/`, e.g. `wedding_map.webp`

#### DB (choose one strategy)
- Render internal: `RENDER_DATABASE_URL`
- Local → Render DB: `REMOTE_DATABASE_URL`
- Local DB: `PGDATABASE`, `PGUSER`, `PGPASSWORD`, `PGHOST`, `PGPORT`

#### Tools
- `GUESTS_CSV_PATH`: guest CSV path (relative path or local absolute path recommended)
- `KEEP_ALIVE_URL`: keep-alive target URL (optional)
- `DEBUG_VERBOSE`: `true/false`

---

## Database (PostgreSQL) Initialization & Guest Import

This project provides two sets of tools:
- `*_local.py`: uses `PG*` (local DB)
- `*_render.py`: uses `RENDER_DATABASE_URL` or `REMOTE_DATABASE_URL` (Render DB)

### A. Local PostgreSQL (uses `PG*`)
Make sure `.env` has `PG*` configured.

Initialize schema + seed groups:
```bash
python tools/seed_loader_local.py
```

Import guest CSV (will truncate `guests` then re-import):
```bash
python tools/guest_loader_local.py
```

### B. Render PostgreSQL (recommended: via DB URL)

Render DB typically provides:
- **Internal Database URL**: reachable only within Render (for your deployed service)
- **External Database URL**: reachable from your local machine (for maintenance/import scripts)

Recommended setup:
- In Render Web Service: set `RENDER_DATABASE_URL = Internal Database URL`
- In local `.env`: set `REMOTE_DATABASE_URL = External Database URL`

Initialize schema + seed groups (on Render DB):
```bash
python tools/seed_loader_render.py
# or python tools/init_db.py (schema only)
```

Import guest CSV (on Render DB):
```bash
python tools/guest_loader_render.py
```

> Note: Render Web Service filesystem is not suitable for storing your real guest CSV. The correct workflow is importing from your local machine using the **External Database URL** into Render DB.

---

## LINE Developers Setup (Webhook)

### 1) Create a Messaging API Channel
In LINE Developers Console:
1. Create a Provider
2. Create a Messaging API Channel

Get:
- Channel secret → `LINE_CHANNEL_SECRET`
- Channel access token (long-lived) → `LINE_CHANNEL_ACCESS_TOKEN`

### 2) Configure Webhook URL
Assume your Render service URL is:
`https://<your-service>.onrender.com`

Set Webhook URL to:
`https://<your-service>.onrender.com/webhook`

In LINE Console:
- Webhook settings → paste URL
- Enable "Use webhook"
- Click "Verify" (requires the service to be deployed and reachable)

### 3) Recommended adjustments (avoid unexpected behavior)
- Auto-reply / Greeting messages: disable if you want full control from backend
- Bot permissions and privacy settings: adjust as needed for your event

---

## Render Deployment (Web Service + PostgreSQL)

> Render UI may change over time, but the core steps are consistent: create DB, create Web Service, set env vars, define start command.

### 1) Create Render PostgreSQL
Render → New → PostgreSQL

After creation, obtain:
- Internal Database URL (for Render Web Service)
- External Database URL (for local maintenance/import)

### 2) Create Render Web Service
Render → New → Web Service → connect your GitHub repo

- Runtime: Python
- Build Command (recommended):
```bash
pip install -r requirements.txt
```

- Start Command (recommended):
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 3) Render Web Service environment variables (Dashboard)
Minimum required:
- `LINE_CHANNEL_SECRET`
- `LINE_CHANNEL_ACCESS_TOKEN`
- `OPENAI_API_KEY`
- `RENDER_DATABASE_URL` (Internal Database URL)
- `STATIC_BASE_URL`: `https://<your-service>.onrender.com/static`
- `STATIC_FULL_SEATMAP`: e.g. `wedding_map.webp`

Wedding context (choose one):
- Recommended: `WEDDING_CONTEXT_JSON` (paste JSON string directly)
- Or: `WEDDING_CONTEXT_PATH=instance/wedding_data.json` (requires the file to exist on Render; generally not recommended for private data)

### 4) Post-deploy verification
- Open: `https://<your-service>.onrender.com/` (health check)
- Go to LINE Developers and verify webhook
- Test in LINE:
  - Seat lookup: "Find 王小明's seat" (or your preferred query text)
  - General Q&A: "What is the schedule today?"

---

## Static Assets (Seat Map)

FastAPI mounts `static/` to `/static`.

Seat map URL is built from:
`STATIC_BASE_URL + /maps/ + STATIC_FULL_SEATMAP`

Example:
`https://<your-service>.onrender.com/static/maps/wedding_map.webp`

Recommendations:
- Place seat map under `static/maps/`
- Prefer `webp` for smaller size and faster loading
- If you need to restrict public access, you will need an auth/signed-URL mechanism (not included in current version)

---

## Keep Alive (Optional)

`tools/keep_alive.py` sends a `GET` request to `KEEP_ALIVE_URL` every 5 minutes.

Usage:
1. Set in `.env`:
   - `KEEP_ALIVE_URL=https://<your-service>.onrender.com/`
2. Run:
```bash
python tools/keep_alive.py
```

> Whether you need keep-alive depends on your Render plan and sleep policy. If your service does not sleep, you can skip it.

---

## Troubleshooting

### 1) LINE webhook verification fails
- Confirm the Render service is deployed and `GET /` is reachable
- Webhook URL must be `https://.../webhook`
- Confirm `LINE_CHANNEL_SECRET` is correct in Render env vars
- Check Render logs (common causes: signature verification failure, wrong route, service not running)

### 2) Reply/push failures
- `main.py` implements reply→push fallback + retry + dead-letter logging
- `instance/dead_letters.jsonl` stores final failed pushes (note: Render filesystem may not be persistent)
- Temporarily enable `DEBUG_VERBOSE=true` to debug via Render logs (disable after you finish)

### 3) Database connection issues
- On Render: use `RENDER_DATABASE_URL` (Internal)
- On local machine: use `REMOTE_DATABASE_URL` (External)
- Internal URLs usually cannot be reached from local networks

### 4) Seat lookup returns not found / too many results
- `queries.py` protections:
  - short keyword → `too_short`
  - too many rows → `too_many`
- Ask users to input a more specific full name or a more precise nickname
