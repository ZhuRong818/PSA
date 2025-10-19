import os

EMP_PROFILES_PATH = os.getenv("EMP_PROFILES_PATH", "/mnt/data/Employee_Profiles.json")
FUNCTIONS_SKILLS_PATH = os.getenv("FUNCTIONS_SKILLS_PATH", "/mnt/data/Functions & Skills(List).csv")
COURSES_PATH = os.getenv("COURSES_PATH", "/mnt/data/Courses_Catalog.csv")

# OpenAI settings (optional)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")  # optional, e.g., for proxy
OPENAI_TIMEOUT = float(os.getenv("OPENAI_TIMEOUT", "15"))
