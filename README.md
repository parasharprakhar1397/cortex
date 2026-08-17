# Cortex — The Business Brain

An autonomous strategic decision-support system for SMBs. Cortex connects to a
business's existing software stack (CRM, accounting, booking, payments, social,
website analytics) and builds a living model of the entire business. It
proactively surfaces the highest-impact decisions — identifying bottlenecks,
simulating outcomes, and estimating ROI — before the owner even knows to ask.

**This is not a chatbot.** Every recommendation answers:

- What happened?
- Why did it happen?
- What should the business do?
- Expected ROI
- Confidence level
- Supporting evidence

## Target customer (v1)

Multi-location healthcare practices in Delhi NCR (dental, physiotherapy,
diagnostic, eye-care chains with 2–10 locations, ₹1–20Cr revenue).

## Repository layout

```
api/                  FastAPI backend (Python)
  app/                application code (config)
  auth/               Clerk JWT verification, auth middleware, dependencies
  db/                 database layer (async engine, schema-per-tenant, migrations)
  routers/            API routers (GET /api/v1/me, ...)
  tests/              pytest suite + integration scripts
ui/                   React + Vite + Tailwind frontend (Task 0.4+)
docs/                 Full design library (product spec, architecture, roadmap)
docker-compose.yml    api + postgres + redis (+ ui from Task 0.4)
Dockerfile            API container
```

## Status

| Task | Title | Status |
|------|-------|--------|
| 0.1 | Project scaffolding (FastAPI + Docker Compose + CI) | ✅ merged |
| 0.2 | Database foundation (async engine, schema-per-tenant, Alembic) | ✅ merged |
| 0.3 | Authentication (Clerk JWT, tenant middleware, `GET /api/v1/me`) | ✅ merged |
| 0.4 | Web UI skeleton (React + Vite + Tailwind, auth guard) | in progress |
| 0.5 | Nginx + SSL + domain (pre-pilot critical) | queued |

See `docs/implementation-plan.md` for the full 7-phase build order and
`docs/risk-review.md` for known risks and mitigations.

## Quick start (local dev)

```bash
# backend (needs Docker for postgres/redis)
cd api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd .. && sudo docker compose up -d   # postgres + redis + api
cd api && alembic upgrade head && uvicorn main:app --reload --port 8000

# tests
cd api && pytest tests/
python tests/test_db.py   # standalone DB integration script
```

Backend runs on port 8000; the UI (once built) runs on port 3000 and proxies
`/api` to 8000.

## Configuration

Copy `.env.example` to `.env` and fill in:

- `DATABASE_URL`, `REDIS_URL`
- Clerk auth: `CLERK_SECRET_KEY`, `CLERK_JWKS_URL`, `CLERK_ISSUER`,
  `CLERK_PUBLISHABLE_KEY` (from the Clerk dashboard; the founder provisions
  the Clerk app)

## Docs index

The design library in `docs/` covers product strategy, system & AI
architecture, data pipelines, agents, memory systems, integrations,
monetization, scaling, security, infrastructure, implementation roadmap,
hiring roadmap, and investor pitch. Start with `docs/INDEX.md`.
