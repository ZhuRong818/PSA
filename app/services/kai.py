from __future__ import annotations

import re
from typing import Optional, Dict, Any, List

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


def _extract_target_role(query: str) -> Optional[str]:
    match = re.search(r"(?:become|be|to\s+be)\s+(?:an?\s+)?([^?!.]+)", query, flags=re.IGNORECASE)
    if match:
        role = re.sub(r"\b(role|position)\b", "", match.group(1), flags=re.IGNORECASE).strip()
        return role or None
    match2 = re.search(r"\b(?:move|transition|advance)\s+(?:into|to)\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*)", query)
    if match2:
        return match2.group(1).strip()
    return None


def _career_coach_reply(q: str, ql: str, email: Optional[str], plans: Dict[str, Any]) -> Optional[str]:
    if not email or email not in plans:
        return None

    target_role = _extract_target_role(q)
    career_query = any(
        phrase in ql
        for phrase in [
            "career path",
            "next role",
            "advance",
            "growth goal",
            "development plan",
            "improve my skills",
            "grow in my career",
            "how to progress",
            "move up",
        ]
    )

    if not target_role and not career_query:
        return None

    try:
        emps = recommender.load_employees(config.EMP_PROFILES_PATH)
    except Exception:
        emps = []
    me = next((emp for emp in emps if emp.email == email), None)
    current_skills = {s.lower() for s in (me.skills if me else [])}
    rsi = recommender.build_role_skill_index(emps) if emps else {}

    reply_parts: List[str] = []

    if target_role:
        target_lower = target_role.lower()
        candidate_role = None
        for role in rsi.keys():
            if role.lower() == target_lower:
                candidate_role = role
                break
        if not candidate_role:
            for role in rsi.keys():
                if target_lower in role.lower():
                    candidate_role = role
                    break
        if candidate_role:
            target_skills = list(rsi.get(candidate_role, {}).keys())
            missing = [sk for sk in target_skills if sk.lower() not in current_skills][:3]
            focus_skills = missing or target_skills[:3]
            if focus_skills:
                focus_text = ", ".join(focus_skills)
                reply_parts.append(
                    f"To become a {candidate_role}, focus on building skills like {focus_text}."
                )
                course_skill = focus_skills[0]
                course_resp = recommender.find_courses(
                    courses_path=config.COURSES_PATH,
                    skill=course_skill,
                    limit=1,
                )
                if course_resp.get("items"):
                    course_title = course_resp["items"][0].get("title")
                    if course_title:
                        reply_parts.append(
                            f"Consider taking \"{course_title}\" to develop your {course_skill} capability."
                        )
            else:
                reply_parts.append(
                    f"A {candidate_role} role needs specialised experience. Partner with mentors to identify targeted learning paths."
                )
        else:
            # If we cannot locate the role, fall back to generic guidance
            career_query = True

    if not reply_parts and career_query:
        plan = plans.get(email)
        if not plan:
            return None
        next_roles = plan.get("next_roles", [])
        if next_roles:
            best_role = next_roles[0]
            role_name = best_role.get("role")
            fit = best_role.get("fit", 0)
            missing_skills = best_role.get("missing_skills_example", [])[:2]
            if not missing_skills:
                missing_skills = [item["skill"] for item in plan.get("upskilling_plan", [])[:2]]
            if role_name:
                reply = (
                    f"One possible next role is {role_name} (fit {int(round(fit * 100))}%)."
                )
                reply_parts.append(reply)
            if missing_skills:
                skills_text = " and ".join(missing_skills)
                reply_parts.append(
                    f"Consider developing skills like {skills_text} to prepare."
                )
                course_resp = recommender.find_courses(
                    courses_path=config.COURSES_PATH,
                    skill=missing_skills[0],
                    limit=1,
                )
                if course_resp.get("items"):
                    course_title = course_resp["items"][0].get("title")
                    if course_title:
                        reply_parts.append(
                            f"For example, \"{course_title}\" is a good starting point for {missing_skills[0]}."
                        )
        else:
            reply_parts.append(
                "Continuously developing your skills opens new opportunities. Pair stretch assignments with targeted courses to progress."
            )

    return " ".join(reply_parts) if reply_parts else None


def chat_reply(q: str, email: Optional[str] = None, locale: Optional[str] = None) -> Dict[str, Any]:
    try:
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
        try:
            plans = recommender.recommend(
                config.EMP_PROFILES_PATH,
                config.FUNCTIONS_SKILLS_PATH,
                courses_path=config.COURSES_PATH,
            )
        except TypeError:
            plans = recommender.recommend(
                config.EMP_PROFILES_PATH,
                config.FUNCTIONS_SKILLS_PATH,
            )
        ctx = _format_context_for_email(plans, email)

        # Career guidance if explicitly requested
        career_reply = _career_coach_reply(q, ql, email, plans)
        if career_reply:
            return {"reply": career_reply}

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
                "Give practical, actionable advice that can help users grow career path. "

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
    except Exception as outer:
        # Ensure the API never returns non-JSON on unexpected errors
        print(f"Kai handler error: {outer}", flush=True)
        return {"reply": "Sorry, I hit a snag. Try asking about roles, mentors, or courses."}
