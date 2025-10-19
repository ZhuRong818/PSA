import os
from typing import List, Optional

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass


def _clean(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    v = value.strip()
    if (v.startswith("\"") and v.endswith("\"")) or (v.startswith("'") and v.endswith("'")):
        v = v[1:-1]
    return v.strip() or None


def _pick(env_name: str, fallbacks: List[str]) -> str:
    raw = _clean(os.getenv(env_name))
    if raw:
        return raw
    for p in fallbacks:
        if os.path.exists(p):
            return p
    return fallbacks[0]

EMP_PROFILES_PATH = _pick("EMP_PROFILES_PATH", [
    "./data/Employee_Profiles.json",
    "/mnt/data/Employee_Profiles.json",
])
FUNCTIONS_SKILLS_PATH = _pick("FUNCTIONS_SKILLS_PATH", [
    "./data/Functions & Skills(List).csv",
    "/mnt/data/Functions & Skills(List).csv",
])
COURSES_PATH = _pick("COURSES_PATH", [
    "./data/Courses_Catalog.csv",
    "/mnt/data/Courses_Catalog.csv",
])

# OpenAI settings (optional)
OPENAI_API_KEY = _clean(os.getenv("OPENAI_API_KEY"))
OPENAI_MODEL = _clean(os.getenv("OPENAI_MODEL")) or "gpt-4o-mini"
OPENAI_BASE_URL = _clean(os.getenv("OPENAI_BASE_URL"))  # optional, e.g., for proxy
OPENAI_TIMEOUT = float(_clean(os.getenv("OPENAI_TIMEOUT")) or "15")
