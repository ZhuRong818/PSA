from __future__ import annotations

from typing import Optional, Dict, Any

from . import recommender
from ..core import config


def _format_context_for_email(plans: Dict[str, Any], email: Optional[str]) -> str:
    if not email or email not in plans:
        return ""
    p = plans[email]
    parts = []
    parts.append(f"Employee: {p['employee']['email']} | Role: {p['employee']['role']} | Dept: {p['employee']['department']}")
    parts.append(f"LPI: {p.get('leadership_potential_index')}")
    nr = p.get("next_roles", [])[:3]
    if nr:
        parts.append("Next roles: " + ", ".join([f"{x['role']} (fit {x['fit']})" for x in nr]))
    ms = []
    for x in nr:
        ms += x.get("missing_skills_example", [])
    if ms:
        parts.append("Missing skills: " + ", ".join(sorted(set(ms))[:6]))
    return "\n".join(parts)


def chat_reply(q: str, email: Optional[str] = None, locale: Optional[str] = None) -> Dict[str, Any]:
    """
    Returns a reply. If OpenAI key is present, uses the model with grounded context from plans.
    Otherwise falls back to simple heuristics.
    """
    # Well-being quick path
    ql = q.lower()
    if any(x in ql for x in ["stress", "overwhelm", "burnout", "tired", "anxious"]):
        return {
            "reply": (
                "I’m here for you. Try a 5‑minute pause, breathe 4‑4‑6, "
                "and consider a short walk. You can access PSA Well‑being resources "
                "or EAP for confidential support."
            )
        }

    # Generate context
    plans = recommender.recommend(config.EMP_PROFILES_PATH, config.FUNCTIONS_SKILLS_PATH)
    ctx = _format_context_for_email(plans, email)

    # If OpenAI key not present, return a heuristic response
    if not config.OPENAI_API_KEY:
        if "skills" in ql and email and email in plans:
            return {
                "reply": (
                    f"You’re in {plans[email]['employee']['role']} "
                    f"({plans[email]['employee']['department']}). "
                    "I can suggest next roles and courses. Try /plans or /courses."
                )
            }
        return {"reply": "Ask about roles, skills, mentors, or courses. Try: /plans or /courses"}

    # Use OpenAI (or Azure OpenAI) when key is available
    try:
        client = None
        model_name = config.OPENAI_MODEL

        if config.AZURE_OPENAI_DEPLOYMENT:
            from openai import AzureOpenAI  # type: ignore

            endpoint = config.AZURE_OPENAI_ENDPOINT or config.OPENAI_BASE_URL
            if not endpoint:
                raise RuntimeError("AZURE_OPENAI_ENDPOINT (or OPENAI_BASE_URL) must be set for Azure OpenAI")
            client = AzureOpenAI(
                api_key=config.OPENAI_API_KEY,
                api_version=config.AZURE_OPENAI_API_VERSION,
                azure_endpoint=endpoint,
            )
            model_name = config.AZURE_OPENAI_DEPLOYMENT
        else:
            from openai import OpenAI  # type: ignore

            client_kwargs = {}
            if config.OPENAI_BASE_URL:
                client_kwargs["base_url"] = config.OPENAI_BASE_URL
            client = OpenAI(api_key=config.OPENAI_API_KEY, **client_kwargs)

        system = (
            "You are ‘Kai’, a concise, friendly career assistant for PSA. "
            "Use the provided context faithfully. Be accessibility-first, "
            "avoid PII beyond what’s given, and keep answers under ~120 words."
        )
        user = (
            f"User query: {q}\n"
            f"Context (employee):\n{ctx}\n"
            "If user asks for next steps, reference available endpoints: /plans, /mentors, /courses."
        )

        # Chat Completions API
        resp = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.3,
        )
        txt = resp.choices[0].message.content.strip() if resp.choices else ""
        if not txt:
            txt = "I can help with roles, mentors, and courses. Try /plans or /courses."
        return {"reply": txt}
    except Exception as e:
        print(f"Kai OpenAI fallback: {e}", flush=True)
        return {"reply": "I can help with roles, mentors, and courses. Try /plans or /courses."}
