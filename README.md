# PSA PathFinder – Prototype

AI-powered career assistant for PSA employees. See your skill gaps, get course suggestions, simulate mentorship, and chat with Kai for tailored coaching.

## Requirements
- macOS/Linux/Windows with Python 3.9+ or Docker
- Internet access (for OpenAI/Azure replies)
- OpenAI API key **or** Azure OpenAI key/endpoint/deployment

## Setup

### 1. Clone / Download
```bash
git clone https://github.com/ZhuRong818/PSA.git
cd PSA
```

### 2. Environment variables
Copy the template and fill in your own keys (do **not** commit real keys):
```bash
cp .env.example .env
```
Edit `.env` or export in your shell:

#### Azure OpenAI (recommended)
```bash
export OPENAI_API_KEY="<your-azure-key>" # We used 02dd5535cd304762b0325aceb8ab83f1
export AZURE_OPENAI_ENDPOINT="https://psacodesprint2025.azure-api.net"     
export AZURE_OPENAI_DEPLOYMENT="gpt-4.1-nano"
export AZURE_OPENAI_API_VERSION="2025-01-01-preview"
```

#### Standard OpenAI
```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_MODEL="gpt-4o-mini"                # optional
# export OPENAI_BASE_URL="https://your-proxy"   # optional
```

If you want to bake them into `.env`, update the same keys there and restart the server.

### 3. Install & Run (Local Python)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
bash scripts/run_local.sh               # uvicorn on http://localhost:8080
```

### 4. Frontend (React UI, optional)
```bash
cd frontend
npm install
npm run dev                               # http://localhost:5173
```
The built-in FastAPI demo UI remains available at http://localhost:8080/ui/.

### Docker option
The current Dockerfile only runs the API:
```bash
docker build -t psa-pathfinder:local .
docker run --rm -p 8080:8080 \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  -e AZURE_OPENAI_ENDPOINT="$AZURE_OPENAI_ENDPOINT" \
  -e AZURE_OPENAI_DEPLOYMENT="$AZURE_OPENAI_DEPLOYMENT" \
  -e AZURE_OPENAI_API_VERSION="$AZURE_OPENAI_API_VERSION" \
  psa-pathfinder:local
```
Then open http://localhost:8080/ui/. (The React dev server still needs to run separately if you want the richer UI.)

## Features

- **Career Plans** (`GET /plans`)
  - Leadership Potential Index, next roles (with fit & skill gaps), real course suggestions per upskilling skill, recognition nudges.
- **Courses Search** (`GET /courses`)
  - Filter by skill, difficulty, hours, language.
- **Mentorship & Recognition** (`POST /mentors/request`, `/recognitions`, `/feedback`)
  - Simulated workflows using the same plan data.
- **Kai Chat** (`GET /chat`)
  - Detects career-growth intent, surfaces skill gaps + course recommendations; falls back to OpenAI/Azure responses for other queries.
- **Leadership League** (`GET /leadership`)
  - Shows top emerging leaders based on sample LPI scores.

## Common issues

| Symptom | Fix |
| --- | --- |
| Chat says “I can help with roles…” | API key not detected. Re-export or update `.env`, restart the server. |
| Azure returns 404 | Endpoint must exclude `/openai`; use `https://psacodesprint2025.azure-api.net`. |
| `/plans` or `/courses` 500 | Ensure `data/Courses_Catalog.csv` and other sample CSVs remain in `data/`. |
| React UI blank | Wait for `npm run dev` to compile; refresh http://localhost:5173 once backend is up. |

## Stopping the app
`Ctrl+C` in each terminal running Uvicorn or Vite.

## Next steps
- Replace heuristics with real ML models (pairwise ranking, proficiency scoring).
- Persist data in Postgres + pgvector/Neo4j.
- Add CI/CD, tests, and a Docker workflow that bundles the built React UI.
