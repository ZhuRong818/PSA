# PSA PathFinder – Prototype (Backend + React UI)

Modern FastAPI + React experience that:
- Loads employee profiles, functions/skills taxonomy, and a courses catalog from local files (`data/`)
- Generates career plans, leadership potential, mentors, and learning suggestions
- Simulates mentorship, recognition, and feedback workflows with realistic responses
- Offers “Kai” — a conversational assistant backed by OpenAI (optional via `OPENAI_API_KEY`)
- Provides a corporate-styled React UI for employees, mentors, and L&D leaders

## Quick start

Data is bundled in `data/` and mounted at `/mnt/data` in Docker.

```bash
# 1) Backend (FastAPI)
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env              # edit if needed; defaults point to ./data/
# echo 'OPENAI_API_KEY="openai3 Active 02dd5535cd304762b0325aceb8ab83f1"' >> .env
bash scripts/run_local.sh         # uvicorn @ http://localhost:8080

# 2) Frontend (React + Vite)
cd frontend
npm install
npm run dev                       # http://localhost:5173 (proxying API)

# Optional Docker back end
cd ..
cp .env.example .env
docker compose up --build
```

Environment variables (FastAPI) — see `.env.example`:
- `EMP_PROFILES_PATH` default `./data/Employee_Profiles.json` (falls back to `/mnt/data/...`)
- `FUNCTIONS_SKILLS_PATH` default `./data/Functions & Skills(List).csv`
- `COURSES_PATH` default `./data/Courses_Catalog.csv`
- `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_BASE_URL`, `OPENAI_TIMEOUT`
- Azure OpenAI (optional): set `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_API_VERSION`

Frontend environment (optional):
- `frontend/.env` → `VITE_API_BASE_URL=http://localhost:8080`

## API surface
- `GET /health` → `{status: "ok"}`
- `GET /plans[?email=...]` → Career plans, leadership index, skills, nudges
- `GET /lpi[?email=...]` → Leadership Potential Index lookup
- `GET /mentors?email=...` → Mentor shortlist
- `POST /mentors/request` → Simulated mentor introduction workflow
- `GET /courses[...]` → Course search with filters
- `POST /recognitions` → Recognition storyline + follow-up suggestions
- `POST /feedback` → Reflection template + action nudges
- `GET /leadership?limit=...` → Ranked leadership snapshot
- `GET /chat?q=...&email=...` → Conversational Kai assistant (OpenAI if key provided)

## UI
- React UI → `frontend/`
  - `npm run dev` → http://localhost:5173 (uses Vite proxy to backend)
  - `npm run build` → production bundle under `frontend/dist`
  - Screens:
    - Career snapshot with LPI, next roles, upskilling plan
    - Mentor shortlist + request simulator
    - Course explorer with difficulty & duration filters
    - Recognition + feedback workflows with realistic prompts
    - Leadership league table
    - Kai chat surface (accessibility-first responses)
- Legacy static demo remains at http://localhost:8080/ui/

## OpenAI key (optional but recommended)
- Do **not** commit real keys. Supply via shell export or `.env` (auto-loaded):
  - `export OPENAI_API_KEY="openai3 Active 02dd5535cd304762b0325aceb8ab83f1"`
- Optional overrides: `OPENAI_MODEL` (default `gpt-4o-mini`), `OPENAI_BASE_URL` for proxies, `OPENAI_TIMEOUT` seconds.
- Azure OpenAI example:
  ```bash
  export OPENAI_API_KEY="02dd5535cd304762b0325aceb8ab83f1"
  export AZURE_OPENAI_ENDPOINT="https://<your-resource>.openai.azure.com"
  export AZURE_OPENAI_DEPLOYMENT="kai-gpt4o"
  export AZURE_OPENAI_API_VERSION="2024-05-01-preview"
  ```

## Troubleshooting 500 errors
- Ensure dependencies are installed: `pip install -r requirements.txt`.
- Verify data paths: with local runs, defaults point to `./data/*`. If you changed them, check `EMP_PROFILES_PATH`, `FUNCTIONS_SKILLS_PATH`, and `COURSES_PATH` in your environment or `.env`.
- Check server logs in the terminal running Uvicorn to see the stack trace. A common cause is a missing file path or uninstalled dependency.

## Notes & next steps
- Current logic is heuristic to stay demo-friendly. Replace with production services:
  - pgvector / Neo4j skill graph, pairwise ranking, proficiency models
  - Persistent store (Postgres + Redis) and real HRIS/LMS integrations
- Add CI (lint/test) and container builds before shipping.
- Data files under `data/` are mock samples — swap for real PSA feeds when ready.
