#!/usr/bin/env bash
set -euo pipefail

# Load .env if present
if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi

export EMP_PROFILES_PATH="${EMP_PROFILES_PATH:-./data/Employee_Profiles.json}"
export FUNCTIONS_SKILLS_PATH="${FUNCTIONS_SKILLS_PATH:-./data/Functions & Skills(List).csv}"
export COURSES_PATH="${COURSES_PATH:-./data/Courses_Catalog.csv}"

python3 -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8080}" --reload

