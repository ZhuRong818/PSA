from typing import Optional, List

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from ..core import config
from ..services import recommender, kai, interactions

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/plans")
def get_plans(email: Optional[str] = None):
    data = recommender.recommend(config.EMP_PROFILES_PATH, config.FUNCTIONS_SKILLS_PATH)
    if email:
        return {email: data.get(email)}
    return data

@router.get("/lpi")
def get_lpi(email: Optional[str] = None):
    return recommender.get_lpi(config.EMP_PROFILES_PATH, email=email)

@router.get("/mentors")
def get_mentors(email: str, limit: int = 3):
    return recommender.get_mentors(config.EMP_PROFILES_PATH, email=email, limit=limit)


class MentorRequest(BaseModel):
    mentee_email: str = Field(..., description="Employee requesting mentorship")
    mentor_email: str = Field(..., description="Desired mentor")
    message: str = Field(..., min_length=3, description="Introductory message")


@router.post("/mentors/request")
def request_mentor(payload: MentorRequest):
    ctx = interactions.InteractionContext.load(
        config.EMP_PROFILES_PATH, config.FUNCTIONS_SKILLS_PATH
    )
    return interactions.mentor_request_message(
        ctx,
        email=payload.mentee_email,
        mentor_email=payload.mentor_email,
        message=payload.message,
    )

@router.get("/courses")
def find_courses(
    q: Optional[str] = Query(None, description="Keyword search"),
    skill: Optional[str] = None,
    difficulty: Optional[str] = Query(None, description="Beginner/Intermediate/Advanced"),
    min_hours: Optional[float] = None,
    max_hours: Optional[float] = None,
    language: Optional[str] = None,
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
def chat(
    q: str = Query(..., description="User query"),
    email: Optional[str] = None,
    locale: Optional[str] = None,
):
    return kai.chat_reply(q=q, email=email, locale=locale)


class RecognitionPayload(BaseModel):
    sender_email: str
    recipient_email: str
    psa_value: str = Field(..., description="PSA value or behaviour spotlight")
    message: str = Field(..., min_length=3)


@router.post("/recognitions")
def submit_recognition(payload: RecognitionPayload):
    ctx = interactions.InteractionContext.load(
        config.EMP_PROFILES_PATH, config.FUNCTIONS_SKILLS_PATH
    )
    return interactions.recognition_message(
        ctx,
        sender_email=payload.sender_email,
        recipient_email=payload.recipient_email,
        value=payload.psa_value,
        note=payload.message,
    )


class FeedbackPayload(BaseModel):
    email: str
    focus_area: str = Field(..., description="Area the person wants to improve")
    strengths: List[str] = Field(default_factory=list)


@router.post("/feedback")
def capture_feedback(payload: FeedbackPayload):
    ctx = interactions.InteractionContext.load(
        config.EMP_PROFILES_PATH, config.FUNCTIONS_SKILLS_PATH
    )
    return interactions.feedback_simulation(
        ctx,
        email=payload.email,
        strengths=payload.strengths,
        focus=payload.focus_area,
    )


@router.get("/leadership")
def leadership_league(limit: int = 10):
    ctx = interactions.InteractionContext.load(
        config.EMP_PROFILES_PATH, config.FUNCTIONS_SKILLS_PATH
    )
    return {"items": interactions.leadership_league(ctx, limit=min(max(limit, 1), 50))}
