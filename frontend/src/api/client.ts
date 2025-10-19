export type EmployeePlan = {
  employee: {
    email: string;
    role: string;
    department: string;
  };
  leadership_potential_index: number;
  next_roles: Array<{ role: string; fit: number; missing_skills_example: string[] }>;
  upskilling_plan: Array<{
    skill: string;
    function_area: string;
    specialization: string;
    suggested_learning: string;
  }>;
  mentors: Array<any>;
  recognition_nudges: string[];
  internal_mobility_options: string[];
};

const DEFAULT_BASE = "http://localhost:8080";

const API_BASE = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? DEFAULT_BASE;

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  return res.json() as Promise<T>;
}

export async function fetchPlans(email?: string): Promise<Record<string, EmployeePlan>> {
  const params = email ? `?email=${encodeURIComponent(email)}` : "";
  const res = await fetch(`${API_BASE}/plans${params}`);
  return handleResponse(res);
}

export async function fetchMentors(email: string, limit = 3) {
  const res = await fetch(
    `${API_BASE}/mentors?email=${encodeURIComponent(email)}&limit=${limit}`
  );
  return handleResponse<{ email: string; mentors: any[] }>(res);
}

export async function requestMentor(payload: {
  mentee_email: string;
  mentor_email: string;
  message: string;
}) {
  const res = await fetch(`${API_BASE}/mentors/request`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}

export async function searchCourses(params: {
  skill?: string;
  difficulty?: string;
  min_hours?: number;
  max_hours?: number;
  q?: string;
  limit?: number;
}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      query.append(key, String(value));
    }
  });
  const res = await fetch(`${API_BASE}/courses?${query.toString()}`);
  return handleResponse<{ total: number; items: any[] }>(res);
}

export async function submitRecognition(payload: {
  sender_email: string;
  recipient_email: string;
  psa_value: string;
  message: string;
}) {
  const res = await fetch(`${API_BASE}/recognitions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}

export async function submitFeedback(payload: {
  email: string;
  focus_area: string;
  strengths: string[];
}) {
  const res = await fetch(`${API_BASE}/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}

export async function fetchLeadership(limit = 8) {
  const res = await fetch(`${API_BASE}/leadership?limit=${limit}`);
  return handleResponse<{ items: any[] }>(res);
}

export async function sendKaiMessage(payload: { email?: string; q: string }) {
  const params = new URLSearchParams({ q: payload.q });
  if (payload.email) params.append("email", payload.email);
  const res = await fetch(`${API_BASE}/chat?${params.toString()}`);
  return handleResponse<{ reply: string }>(res);
}
