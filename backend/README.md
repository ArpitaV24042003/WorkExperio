# WorkExperio
Revolutionizing Project Management with AI-Driven Team Formation &amp; Performance Analysis

## Backend Quickstart

### Environment

Copy the example environment and adjust as needed:

```bash
cd backend
cp env.example .env
```

Important variables:

- `DATABASE_URL` – defaults to `sqlite:///./dev.db` for local development (persistent file-based SQLite).
- `SECRET_KEY` – JWT signing key.
- `OPENAI_API_KEY` – optional, only needed if you wire a real LLM provider.

### Database

The development environment uses a persistent on-disk SQLite database by default:

```env
DATABASE_URL=sqlite:///./dev.db
```

To (re)create any missing tables locally after schema changes, run:

```bash
python -c "from app.db import create_all_tables; create_all_tables()"
```

For production, point `DATABASE_URL` at Postgres and run Alembic migrations instead.
