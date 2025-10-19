Got it. Here’s a **user-friendly README** focused only on setup and usage (no developer jargon).

---

# PSA PathFinder — User Guide

AI-powered career guidance for PSA employees. See your skill gaps, get upskilling ideas, find courses, and chat with **Kai** for tailored advice.

## What you need

* A computer with internet access (for AI answers).
* One of these:

  * **Azure OpenAI** key + endpoint, or
  * **OpenAI** API key.

## Download

1. Go to your PSA PathFinder page.
2. Click **Download** or **Clone** the project.
3. Unzip (if downloaded as a zip).

## Setup (one-time)

### ) Using **Azure OpenAI** 

1. Open a terminal in the project folder.
2. Set these values (replace with yours), then press Enter after each line:

   ```bash
   export OPENAI_API_KEY="YOUR_AZURE_KEY" //# We provide 02dd5535cd304762b0325aceb8ab83f1 as Azure API key
   export AZURE_OPENAI_ENDPOINT="https://<your-endpoint>/openai"# We provide https://psacodesprint2025.azure-api.net as endpoint
   export AZURE_OPENAI_DEPLOYMENT="gpt-4.1-nano"     # or your deployment name
   export AZURE_OPENAI_API_VERSION="2025-01-01-preview"
   ```
3. Skip to **Run**.



## Run

### Option 1 — Simple run

1. Install requirements (first time only):

   ```bash
   pip install -r requirements.txt
   ```
2. Start the app:

   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8080
   ```
3. Open your browser:
   `http://localhost:8080/ui/`

### Option 2 — Docker (no Python setup)

1. Build:

   ```bash
   docker build -t psa-pathfinder:local .
   ```
2. Run (uses your keys from the current shell):

   ```bash
   docker run --rm -p 8080:8080 \
     -e OPENAI_API_KEY="$OPENAI_API_KEY" \
     -e OPENAI_MODEL="$OPENAI_MODEL" \
     -e AZURE_OPENAI_ENDPOINT="$AZURE_OPENAI_ENDPOINT" \
     -e AZURE_OPENAI_DEPLOYMENT="$AZURE_OPENAI_DEPLOYMENT" \
     -e AZURE_OPENAI_API_VERSION="$AZURE_OPENAI_API_VERSION" \
     psa-pathfinder:local
   ```
3. Open your browser:
   `http://localhost:8080/ui/`

## Use the app

1. **Open** `http://localhost:8080/ui/`.
2. **Select an employee** from the dropdown.
3. Review your **Career Plan**:

   * Current role and LPI.
   * Suggested next roles with fit % and missing skills.
   * Upskilling plan and recognition nudges.
4. **Find Courses**:

   * Search by skill, difficulty, or hours.
   * Click a course to open its page.
5. **Ask Kai**:

   * Type your question (e.g., “What do I need for Terminal Supervisor?”).
   * If an employee is selected, answers are personalized.

## Common issues (quick fixes)

* Chat says: “I can help with roles, mentors, and courses…”
  Your AI key isn’t being used. Re-set your keys in the same terminal and restart the app.
* Azure users: ensure all **four** values are set (key, endpoint, deployment, api-version).
* Nothing loads on `/ui`: wait 2–3 seconds after starting; then refresh.
* Data not found: keep sample files in the `data/` folder (already included).

## Stop the app

* Press `Ctrl + C` in the terminal window.
.

---

