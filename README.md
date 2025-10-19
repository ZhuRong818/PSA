# PSA PathFinder – Prototype (Backend Monolith)

Minimal FastAPI service that:
- Loads employee profiles, functions/skills taxonomy, and a small courses catalog from local files
- Generates career plans, leadership potential, mentors, and learning suggestions
- Exposes tool-like endpoints for Kai: `get_plans`, `get_lpi`, `get_mentors`, `find_courses`

## Quick start

Data is bundled in `data/` and mounted at `/mnt/data` in Docker.

```bash
# 1) Local (no docker)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

# 2) Docker
cp .env.example .env   # optional override
docker compose up --build
```

Environment variables (see `.env.example`):
- `EMP_PROFILES_PATH` default `/mnt/data/Employee_Profiles.json`
- `FUNCTIONS_SKILLS_PATH` default `/mnt/data/Functions & Skills(List).csv`
- `COURSES_PATH` default `/mnt/data/Courses_Catalog.csv`

## Endpoints
- `GET /health` → `{status: "ok"}`
- `GET /plans[?email=email@psa]` → Career plans, next roles, upskilling, LPI
- `GET /lpi[?email=email@psa]` → Leadership Potential Index per employee
- `GET /mentors?email=email@psa[&limit=3]` → Mentor suggestions for an employee
- `GET /courses[?q=..&skill=..&difficulty=..&min_hours=..&max_hours=..&language=..&limit=10]` → Course search
- `GET /chat?q=...&email=...` → Simple “Kai” assistant stub

## Notes
- This is a minimal, heuristic prototype intended for demo. Swap heuristics with ML (pairwise LTR ranker, proficiencies, and pgvector graph) in later iterations.
- Data files live under `data/` and are small mock datasets for local use.
