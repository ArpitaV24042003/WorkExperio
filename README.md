# WorkExperio

AI-driven student collaboration platform featuring resume parsing, skill-based team formation, AI project ideation, live chat, and performance analytics.

## Project Structure

```
WorkExperio_Backend/
├── backend/            # FastAPI application and tests
├── frontend/           # React + Vite + Tailwind client
└── README.md
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- Poetry or pip for Python dependencies

## Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # or source venv/bin/activate
pip install -r requirements.txt
cp env.example .env
uvicorn app.main:app --reload
```

### Database

The development environment uses SQLite by default. To run against Postgres, set `DATABASE_URL` in `.env` (e.g. `postgresql+psycopg2://user:pass@localhost:5432/workexperio`).

### Running Tests

```bash
pytest
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The client expects an API at `http://localhost:8000`. Configure `VITE_API_URL` and `VITE_WS_URL` in a `.env` file inside the `frontend` directory if different.

## Key Features

- **Auth & Profiles:** JWT auth, resume-powered profile setup, education/experience/skill management.
- **AI Modules:** Resume parser (pdfplumber), project idea generator, team selection heuristics, performance analytics, AI assistant chat.
- **Projects & Teams:** Manual or AI-generated projects, waitlist logic with 7-day solo fallback, team assignment workflows.
- **Collaboration:** WebSocket chat per project, AI assistant summaries, XP and review engine.
- **Frontend Experience:** Tailwind + Shadcn-inspired UI, Zustand state, real-time chat, project dashboards.

## Environment Variables

Refer to `backend/env.example` for backend configuration and create `frontend/.env` for client overrides, for example:

```
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## Deployment Notes

- Update `ALLOW_ORIGINS` for production domains.
- Swap SQLite for Postgres by updating `DATABASE_URL`.
- Use a persistent websocket gateway (e.g. Uvicorn with `--ws websockets`) in production.
