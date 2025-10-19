"""Utility functions for mentorship, recognition, and feedback simulations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

from . import recommender


@dataclass
class InteractionContext:
    """Small data container hydrated from recommender outputs."""

    plans: Dict[str, Dict]

    @classmethod
    def load(cls, employees_path: str, taxonomy_path: str) -> "InteractionContext":
        plans = recommender.recommend(employees_path, taxonomy_path)
        return cls(plans=plans)

    def employee_exists(self, email: str) -> bool:
        return email in self.plans

    def get_employee_summary(self, email: str) -> str:
        p = self.plans.get(email)
        if not p:
            return "Unknown employee"
        emp = p.get("employee", {})
        lpi = p.get("leadership_potential_index")
        next_roles = ", ".join(r["role"] for r in p.get("next_roles", [])[:3])
        return (
            f"{emp.get('email')} | {emp.get('role')} | {emp.get('department')} | "
            f"LPI {lpi} | Next roles: {next_roles or 'n/a'}"
        )


def mentor_request_message(ctx: InteractionContext, email: str, mentor_email: str, message: str) -> Dict:
    timestamp = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    if not ctx.employee_exists(email) or not ctx.employee_exists(mentor_email):
        return {
            "status": "error",
            "timestamp": timestamp,
            "summary": "Either employee or mentor email was not recognised.",
        }
    mentee_summary = ctx.get_employee_summary(email)
    mentor_summary = ctx.get_employee_summary(mentor_email)
    return {
        "status": "submitted",
        "timestamp": timestamp,
        "mentee": mentee_summary,
        "mentor": mentor_summary,
        "tips": [
            "Set clear objectives for your first meeting (e.g. certification, stretch project).",
            "Agree on cadence and preferred channels in the first conversation.",
            "Share a short bio with focus areas and how you like to receive feedback.",
        ],
        "echo": message.strip(),
    }


def recognition_message(ctx: InteractionContext, sender_email: str, recipient_email: str, value: str, note: str) -> Dict:
    timestamp = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    if not ctx.employee_exists(sender_email) or not ctx.employee_exists(recipient_email):
        return {
            "status": "error",
            "timestamp": timestamp,
            "summary": "Sender or recipient email not recognised.",
        }
    sender = ctx.get_employee_summary(sender_email)
    recipient = ctx.get_employee_summary(recipient_email)
    return {
        "status": "recorded",
        "timestamp": timestamp,
        "sender": sender,
        "recipient": recipient,
        "value": value,
        "recognition_story": note.strip(),
        "share_copy": f"Celebrating {recipient_email} for demonstrating {value}: {note.strip()}",
        "next_steps": [
            "Publish on #recognition channel with optional photo (ensure consent).",
            "Log it in PSA recognition tracker if part of quarterly awards.",
            "Encourage recipient to pass it forward within their squad.",
        ],
    }


def feedback_simulation(_: InteractionContext, email: str, strengths: List[str], focus: str) -> Dict:
    timestamp = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    return {
        "status": "captured",
        "timestamp": timestamp,
        "reflection_prompt": (
            "Thank you for sharing. Consider booking a 15‑min retro with your partner "
            "to align on the focus area: "
            f"{focus.strip()}"
        ),
        "strength_highlights": strengths,
        "template": (
            "START: continue leveraging {strengths[0] if strengths else 'your strengths'}\n"
            "STOP: reduce blockers around the focus area\n"
            "CONTINUE: recognise progress weekly"
        ),
        "suggested_actions": [
            "Schedule feedback follow-up in two weeks.",
            "Document key actions in the mentorship tracker.",
            "Share a nudge via Kai to celebrate small wins.",
        ],
    }


def leadership_league(ctx: InteractionContext, limit: int) -> List[Dict]:
    ranked = sorted(
        ctx.plans.values(), key=lambda p: p.get("leadership_potential_index", 0), reverse=True
    )
    output: List[Dict] = []
    for p in ranked[:limit]:
        emp = p.get("employee", {})
        output.append(
            {
                "email": emp.get("email"),
                "role": emp.get("role"),
                "department": emp.get("department"),
                "leadership_potential_index": p.get("leadership_potential_index"),
                "next_roles": [r.get("role") for r in p.get("next_roles", [])[:3]],
            }
        )
    return output

