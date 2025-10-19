from __future__ import annotations

import json, math
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

TODAY = date.today()
LEVEL_WEIGHTS = {"Beginner": 0.25, "Intermediate": 0.5, "Advanced": 0.85, "Expert": 1.0}

def _parse_date(s: Optional[str]):
    if not s: return None
    try: return datetime.strptime(s, "%Y-%m-%d").date()
    except: return None

@dataclass
class EmployeeLite:
    email: str
    job_title: str
    department: str
    unit: str
    in_role_since: Optional[str]
    skills: List[str]
    competencies: List[Dict[str, str]]
    positions_history: List[Dict[str, Any]]
    projects: List[Dict[str, Any]]

def load_employees(path: str) -> List[EmployeeLite]:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    out: List[EmployeeLite] = []
    for e in raw:
        out.append(
            EmployeeLite(
                email=e["personal_info"]["email"],
                job_title=e["employment_info"]["job_title"],
                department=e["employment_info"]["department"],
                unit=e["employment_info"]["unit"],
                in_role_since=e["employment_info"].get("in_role_since"),
                skills=[s["skill_name"] for s in e.get("skills", [])],
                competencies=e.get("competencies", []),
                positions_history=e.get("positions_history", []),
                projects=e.get("projects", []),
            )
        )
    return out

def load_taxonomy(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    cols = {c.lower().strip(): c for c in df.columns}
    fa = next((cols[k] for k in cols if "function" in k and "area" in k), None)
    sp = next((cols[k] for k in cols if "special" in k), None)
    sk = next((cols[k] for k in cols if "skill" in k), None)
    if not (fa and sp and sk):
        raise ValueError(f"CSV must contain function_area, specialization, skill_name columns. Found: {list(df.columns)}")
    df = df.rename(columns={fa: "function_area", sp: "specialization", sk: "skill_name"})
    for c in ["function_area", "specialization", "skill_name"]:
        df[c] = df[c].astype(str).str.strip()
    return df[["function_area", "specialization", "skill_name"]].dropna()

def load_courses(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    cols = {c.lower().strip(): c for c in df.columns}
    req = {
        "title": next((cols[k] for k in cols if "title" in k), None),
        "skill_name": next((cols[k] for k in cols if "skill" in k and "name" in k), None),
        "provider": next((cols[k] for k in cols if "provider" in k), None),
        "difficulty": next((cols[k] for k in cols if "difficulty" in k or "level" in k), None),
        "duration_hours": next((cols[k] for k in cols if "duration" in k and "hour" in k), None),
        "language": next((cols[k] for k in cols if "language" in k), None),
        "url": next((cols[k] for k in cols if k.strip()=="url"), None),
        "description": next((cols[k] for k in cols if "desc" in k), None),
    }
    for k, v in req.items():
        if v is None and k in {"description", "url"}:
            continue
        if v is None:
            raise ValueError("Courses CSV missing required column: " + k)
    df = df.rename(columns={v: k for k, v in req.items() if v})
    for c in ["title", "skill_name", "provider", "difficulty", "language"]:
        df[c] = df[c].astype(str).str.strip()
    if "duration_hours" in df:
        df["duration_hours"] = pd.to_numeric(df["duration_hours"], errors="coerce")
    return df

def build_role_skill_index(employees: List[EmployeeLite]) -> Dict[str, Dict[str, float]]:
    idx: Dict[str, Dict[str, float]] = {}
    for e in employees:
        tenure = 1.0
        d = _parse_date(e.in_role_since)
        if d:
            tenure = max(0.5, (TODAY - d).days / 365.0)
        for s in e.skills:
            idx.setdefault(e.job_title, {}).setdefault(s, 0.0)
            idx[e.job_title][s] += min(2.0, tenure)
    return idx

def cosine(a: List[float], b: List[float]) -> float:
    dot = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a)); nb = math.sqrt(sum(y*y for y in b))
    return 0.0 if na == 0 or nb == 0 else dot/(na*nb)

def role_adjacency(role_skill_index: Dict[str, Dict[str, float]], top_k: int = 5) -> Dict[str, List[Tuple[str, float]]]:
    vocab = sorted({sk for r in role_skill_index for sk in role_skill_index[r]})
    vecs = {r: [role_skill_index[r].get(sk, 0.0) for sk in vocab] for r in role_skill_index}
    roles = list(vecs.keys())
    adj = {}
    for i, r in enumerate(roles):
        sims = []
        for j, r2 in enumerate(roles):
            if i == j: continue
            sims.append((r2, cosine(vecs[r], vecs[r2])))
        sims.sort(key=lambda x: x[1], reverse=True)
        adj[r] = sims[:top_k]
    return adj

def gap_score(current: List[str], target: List[str]) -> float:
    have = set(x.lower() for x in current)
    need = [x.lower() for x in target]
    if not need: return 0.0
    missing = [x for x in need if x not in have]
    return len(missing)/len(need)

def compute_lpi(e: EmployeeLite) -> float:
    # competencies
    if e.competencies:
        comp = sum(LEVEL_WEIGHTS.get(c.get("level","Intermediate"), 0.5) for c in e.competencies)/len(e.competencies)
    else:
        comp = 0.5
    impact = min(1.0, 0.3 + 0.1*sum(len(p.get("outcomes",[])) for p in e.projects))
    prog = 0.2 + 0.1*len(e.positions_history)
    score = (0.4*comp + 0.3*impact + 0.3*min(1.0, prog))*10
    return round(max(0.0, min(10.0, score)), 2)

def recommend(employees_path: str, taxonomy_path: str) -> Dict[str, Any]:
    emps = load_employees(employees_path)
    taxo = load_taxonomy(taxonomy_path)
    rsi = build_role_skill_index(emps)
    adj = role_adjacency(rsi, top_k=5)

    results: Dict[str, Any] = {}
    for e in emps:
        # candidate roles
        cand = [r for r, s in adj.get(e.job_title, []) if s > 0.2]
        # business-rule nudge
        if "Cloud" in e.job_title: cand += ["Enterprise Architect", "IT Strategy Manager"]
        if e.department == "Finance": cand += ["Senior FP&A Manager", "Finance Business Partner"]
        if e.department.startswith("Human Resource"): cand += ["Head of Talent Management", "OD & Leadership Lead"]
        # unique preserve order
        seen=set(); next_roles=[]
        for r in cand:
            if r not in seen: seen.add(r); next_roles.append(r)
        # enrich
        enriched=[]
        for r in next_roles[:5]:
            target_sk = list(rsi.get(r, {}).keys())
            enriched.append({
                "role": r,
                "fit": round(1.0 - gap_score(e.skills, target_sk), 2),
                "missing_skills_example": [sk for sk in target_sk if sk not in e.skills][:5]
            })
        # upskilling plan: pick skills in same function area not possessed
        # We don't have function areas per employee here, so we fallback to top of taxonomy
        plan=[]
        for _, row in taxo.iterrows():
            sk = row["skill_name"]
            if sk not in e.skills:
                plan.append({
                    "skill": sk,
                    "function_area": row["function_area"],
                    "specialization": row["specialization"],
                    "suggested_learning": f"Course: {sk} Foundations (mock)"
                })
            if len(plan)>=8: break

        # mentors: simple placeholder (none until we add directory) -> could pick managers later
        mentors=[]

        results[e.email] = {
            "employee": {"email": e.email, "role": e.job_title, "department": e.department},
            "leadership_potential_index": compute_lpi(e),
            "next_roles": enriched,
            "upskilling_plan": plan,
            "internal_mobility_options": list({ph.get("role_title") for ph in e.positions_history if ph.get("role_title")})[:6],
            "mentors": mentors,
            "recognition_nudges": [
                "Give a shout‑out to a teammate exemplifying Teamwork.",
                "Share one lesson learned in your team channel this week.",
                "Nominate a peer for monthly recognition program."
            ]
        }
    return results

def get_lpi(employees_path: str, email: Optional[str] = None) -> Dict[str, Any]:
    emps = load_employees(employees_path)
    scores = {e.email: compute_lpi(e) for e in emps}
    if email:
        return {email: scores.get(email)}
    return scores

def get_mentors(employees_path: str, email: str, limit: int = 3) -> Dict[str, Any]:
    emps = load_employees(employees_path)
    me = next((e for e in emps if e.email == email), None)
    if not me:
        return {"email": email, "mentors": []}
    rsi = build_role_skill_index(emps)
    adj = role_adjacency(rsi, top_k=10)
    similar_roles = {r for r, _ in adj.get(me.job_title, [])}
    my_lpi = compute_lpi(me)
    cand = []
    for e in emps:
        if e.email == email:
            continue
        lpi = compute_lpi(e)
        seniority = len(e.positions_history)
        same_dept = 1.0 if e.department == me.department else 0.0
        same_unit = 1.0 if e.unit == me.unit else 0.0
        role_sim = 1.0 if e.job_title in similar_roles else 0.0
        score = 0.35*same_dept + 0.2*same_unit + 0.25*role_sim + 0.2*max(0.0, lpi - my_lpi)/10.0 + 0.05*seniority
        cand.append({
            "email": e.email,
            "role": e.job_title,
            "department": e.department,
            "unit": e.unit,
            "leadership_potential_index": lpi,
            "score": round(score, 3)
        })
    cand.sort(key=lambda x: x["score"], reverse=True)
    return {"email": email, "mentors": cand[:max(1, limit)]}

def find_courses(
    courses_path: str,
    q: Optional[str] = None,
    skill: Optional[str] = None,
    difficulty: Optional[str] = None,
    min_hours: Optional[float] = None,
    max_hours: Optional[float] = None,
    language: Optional[str] = None,
    limit: int = 10,
) -> Dict[str, Any]:
    df = load_courses(courses_path)
    if skill:
        df = df[df["skill_name"].str.lower().str.contains(skill.lower())]
    if difficulty:
        df = df[df["difficulty"].str.lower() == difficulty.lower()]
    if language:
        df = df[df["language"].str.lower() == language.lower()]
    if min_hours is not None:
        df = df[(df["duration_hours"].fillna(0) >= float(min_hours))]
    if max_hours is not None:
        df = df[(df["duration_hours"].fillna(0) <= float(max_hours))]
    if q:
        ql = q.lower()
        text = df[[c for c in ["title", "description", "skill_name", "provider"] if c in df]].fillna("")
        df = df.assign(_score=(
            text.apply(lambda r: sum(1 for v in r.values if ql in str(v).lower()), axis=1)
        ))
        df = df[df["_score"] > 0].sort_values("_score", ascending=False)
    rows = df.head(limit).to_dict(orient="records")
    for r in rows:
        r.pop("_score", None)
    return {"total": int(len(df)), "items": rows}
