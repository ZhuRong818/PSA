from fastapi import APIRouter, Query
from ..core import config
from ..services import recommender

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/plans")
def get_plans(email: str | None = None):
    data = recommender.recommend(config.EMP_PROFILES_PATH, config.FUNCTIONS_SKILLS_PATH)
    if email:
        return {email: data.get(email)}
    return data

@router.get("/lpi")
def get_lpi(email: str | None = None):
    return recommender.get_lpi(config.EMP_PROFILES_PATH, email=email)

@router.get("/mentors")
def get_mentors(email: str, limit: int = 3):
    return recommender.get_mentors(config.EMP_PROFILES_PATH, email=email, limit=limit)

@router.get("/courses")
def find_courses(
    q: str | None = Query(None, description="Keyword search"),
    skill: str | None = None,
    difficulty: str | None = Query(None, description="Beginner/Intermediate/Advanced"),
    min_hours: float | None = None,
    max_hours: float | None = None,
    language: str | None = None,
    limit: int = 10,
):
    return recommender.find_courses(
        courses_path=config.COURSES_PATH,
        q=q,
        skill=skill,
        difficulty=difficulty,
        min_hours=min_hours,
        max_hours=max_hours,
        language=language,
        limit=limit,
    )

@router.get("/chat")
def chat(q: str = Query(..., description="User query"), email: str | None = None):
    # Very simple stub
    if "stress" in q.lower() or "overwhelm" in q.lower():
        return {"reply": "I'm here for you. Try a 5‑minute break and paced breathing. You can access PSA Well‑being resources or EAP."}
    if "skills" in q.lower() and email:
        plans = recommender.recommend(config.EMP_PROFILES_PATH, config.FUNCTIONS_SKILLS_PATH)
        emp = plans.get(email, {}).get("employee")
        if emp:
            return {"reply": f"You're in {emp['role']} ({emp['department']}). I can suggest next roles and courses. Try /plans."}
    return {"reply": "Ask me about roles, skills, mentors, or well‑being. Try: /plans"}
