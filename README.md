# HoneyShield

HoneyShield is a mini SIEM-style project focused on SSH attack telemetry. It includes:

- An SSH honeypot that records login attempts (no real shell access, fully isolated).
- A Python + FastAPI backend that ingests, normalizes, and correlates events.
- A PostgreSQL database storing raw events, IP risk scores, and alerts.
- A React + Tailwind CSS dashboard (with Chart.js) that visualizes attack activity and risk with modern UI.

## Architecture

- **SSH Honeypot (`backend/honeypot/ssh_honeypot.py`)**
  - Paramiko-based SSH server listening on a configurable port (default `2222`).
  - Never provides a real shell; it simply logs username/password attempts.
  - On each attempt, it POSTs a normalized JSON event to `POST /api/ingest/ssh` on the backend.

- **Backend API (FastAPI, `backend/app`)**
  - `main.py` exposes endpoints:
    - `POST /api/ingest/ssh` – ingest SSH events from the honeypot.
    - `GET /api/stats/overview` – KPI cards (total events, unique IPs, high-risk IPs, open alerts).
    - `GET /api/stats/timeline` – events over time for the attack timeline visualization.
    - `GET /api/stats/top-ips` – top attacking IPs with event counts and risk scores.
    - `GET /api/stats/credentials` – credential heatmap (most targeted usernames).
    - `GET /api/alerts` – current alerts.
  - `models.py` defines `Event`, `IPRiskScore`, and `Alert` tables.
  - `correlation.py` implements:
    - Classification of activity into `bruteforce`, `recon`, or `low_activity` per IP.
    - Incremental risk scoring per IP.
    - Alert generation when risk crosses a configurable threshold.

- **Frontend Dashboard (`frontend/`)**
  - React + Vite + Tailwind CSS + Chart.js UI.
  - `App.jsx` renders:
    - Overview KPI cards.
    - Attack timeline chart.
    - Top attacking IPs chart + risk scores.
    - Credential “heatmap” (username frequency chips).
    - Risk severity indicator.
    - Alerts panel for high-risk activity.
  - Uses REST polling every few seconds to keep the dashboard updated.

- **Sample Data (`backend/scripts/seed_sample_data.py`)**
  - Seeds realistic example SSH attack events for demo/testing.

## Prerequisites

- Python 3.10+
- Node.js (for the React frontend)
- PostgreSQL instance

## Backend setup

1. Create a PostgreSQL database and user (example):

   ```bash
   createdb honeyshield
   psql -c "CREATE USER honeyshield WITH PASSWORD 'honeyshield';"
   psql -c "GRANT ALL PRIVILEGES ON DATABASE honeyshield TO honeyshield;"
   ```

2. In `backend/app/config.py`, ensure `DATABASE_URL` matches your database, e.g.:

   ```python
   DATABASE_URL = "postgresql+psycopg2://honeyshield:honeyshield@localhost:5432/honeyshield"
   ```

3. Create and activate a virtualenv, then install dependencies:

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. Run the FastAPI backend:

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Health check: open `http://127.0.0.1:8000/health` in your browser.

## Seeding sample attack data

With the backend running and the DB configured:

```bash
cd backend
source .venv/bin/activate  # if not already
python -m scripts.seed_sample_data
```

This will insert a few hundred SSH login attempts across multiple IPs and trigger risk scoring + alerts so the dashboard looks interesting immediately.

## Running the SSH honeypot

**Warning:** Only run the honeypot on lab/test hosts and networks you control.

1. Ensure the backend is running on `http://127.0.0.1:8000` (default in `config.py`).
2. In another terminal:

   ```bash
   cd backend
   source .venv/bin/activate
   python -m honeypot.ssh_honeypot
   ```

3. The honeypot listens on `0.0.0.0:2222` by default. Any SSH login attempts to that port will be logged and forwarded to the backend.

## Frontend setup (React + Tailwind + Chart.js)

1. Install Node dependencies:

   ```bash
   cd frontend
   npm install
   ```

2. (Optional) Configure the API base URL for the dashboard via `.env`:

   ```bash
   echo "VITE_API_BASE_URL=http://127.0.0.1:8000/api" > .env
   ```

   By default, the frontend assumes `http://127.0.0.1:8000/api`.

3. Start the dev server:

   ```bash
   npm run dev
   ```

4. Open the URL printed by Vite (usually `http://127.0.0.1:5173`) to view the HoneyShield dashboard.

## How it fits the SIEM-style requirements

- **Log normalization/parsing:**
  - Honeypot sends structured JSON; backend stores normalized `Event` rows (IP, username, password, port, protocol, timestamp).
- **Attack correlation (bruteforce, recon):**
  - `correlation.py` classifies IP behavior based on volume and recency of events.
- **Risk scoring per IP:**
  - `IPRiskScore` table stores incremental scores; higher for brute-force patterns.
- **Timeline & event aggregation:**
  - `/api/stats/timeline` aggregates events in time buckets for the timeline chart.
- **Alerts for high-risk activity:**
  - Alerts are created when `IPRiskScore` exceeds a threshold and surfaced via `/api/alerts` and the Alerts panel in the UI.

This gives you a complete, working HoneyShield project with a modern dashboard, SSH honeypot, SIEM-style analytics, and sample attack data.
