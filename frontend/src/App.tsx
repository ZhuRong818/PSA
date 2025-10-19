import { useEffect, useMemo, useState } from "react";
import {
  fetchPlans,
  fetchMentors,
  requestMentor,
  searchCourses,
  submitRecognition,
  submitFeedback,
  sendKaiMessage,
  fetchLeadership,
  EmployeePlan,
} from "./api/client";
import { Panel } from "./components/Panel";
import { CourseFilters } from "./components/CourseFilters";
import { toast, ToastViewport } from "./components/Toast";

type PlanMap = Record<string, EmployeePlan>;

const defaultRecognitionValues = [
  "Care",
  "Collaboration",
  "Courage",
  "Commitment",
  "Creativity",
];

function App() {
  const [loading, setLoading] = useState(true);
  const [plans, setPlans] = useState<PlanMap>({});
  const [selectedEmail, setSelectedEmail] = useState<string>("");
  const [mentors, setMentors] = useState<any[]>([]);
  const [courses, setCourses] = useState<any[]>([]);
  const [leadership, setLeadership] = useState<any[]>([]);
  const [isMentorModalOpen, setMentorModalOpen] = useState(false);
  const [kaiMessage, setKaiMessage] = useState("");
  const [kaiReply, setKaiReply] = useState("Ask Kai something about your growth, wellbeing, or next roles.");
  const [courseFilters, setCourseFilters] = useState({
    skill: "",
    difficulty: "",
    min_hours: "",
    max_hours: "",
  });
  const [mentorDraft, setMentorDraft] = useState({ mentorEmail: "", message: "" });
  const [recognitionDraft, setRecognitionDraft] = useState({
    recipientEmail: "",
    psaValue: defaultRecognitionValues[0],
    message: "",
  });
  const [feedbackDraft, setFeedbackDraft] = useState({
    focus: "",
    strengths: "" as string,
  });

  useEffect(() => {
    async function init() {
      try {
        const data = await fetchPlans();
        setPlans(data);
        const firstEmail = Object.keys(data)[0];
        if (firstEmail) {
          setSelectedEmail(firstEmail);
          await refreshMentors(firstEmail);
          await loadLeadership();
        }
      } catch (err) {
        console.error(err);
        toast.error("Failed to load plans. Check API status.");
      } finally {
        setLoading(false);
      }
    }
    init();
  }, []);

  const employees = useMemo(() => Object.values(plans).map((p) => p.employee), [plans]);
  const activePlan = selectedEmail ? plans[selectedEmail] : undefined;

  async function refreshMentors(email: string) {
    try {
      const data = await fetchMentors(email, 3);
      setMentors(data.mentors);
    } catch (err) {
      console.error(err);
      toast.error("Unable to load mentors right now.");
    }
  }

  async function loadCourses(params = courseFilters) {
    try {
      const parsed = {
        skill: params.skill || undefined,
        difficulty: params.difficulty || undefined,
        min_hours: params.min_hours ? Number(params.min_hours) : undefined,
        max_hours: params.max_hours ? Number(params.max_hours) : undefined,
      };
      const data = await searchCourses(parsed);
      setCourses(data.items);
      toast.info(`Found ${data.items.length} courses.`);
    } catch (err) {
      console.error(err);
      toast.error("Course search failed. Try adjusting filters.");
    }
  }

  async function loadLeadership() {
    try {
      const { items } = await fetchLeadership(6);
      setLeadership(items);
    } catch (err) {
      console.error(err);
    }
  }

  const handleMentorSubmit = async () => {
    if (!selectedEmail) return;
    try {
      const result = await requestMentor({
        mentee_email: selectedEmail,
        mentor_email: mentorDraft.mentorEmail,
        message: mentorDraft.message,
      });
      toast.success("Mentor request drafted.");
      setMentorModalOpen(false);
      setMentorDraft({ mentorEmail: "", message: "" });
      setKaiReply(result.tips?.join(" \n") ?? "Mentor request submitted.");
    } catch (err) {
      console.error(err);
      toast.error("Could not submit mentor request.");
    }
  };

  const handleRecognitionSubmit = async () => {
    if (!selectedEmail) return;
    try {
      const result = await submitRecognition({
        sender_email: selectedEmail,
        recipient_email: recognitionDraft.recipientEmail,
        psa_value: recognitionDraft.psaValue,
        message: recognitionDraft.message,
      });
      toast.success("Recognition drafted successfully.");
      setRecognitionDraft({ recipientEmail: "", psaValue: defaultRecognitionValues[0], message: "" });
      setKaiReply(result.share_copy ?? "Recognition captured.");
    } catch (err) {
      console.error(err);
      toast.error("Recognition submission failed.");
    }
  };

  const handleFeedbackSubmit = async () => {
    if (!selectedEmail) return;
    try {
      const result = await submitFeedback({
        email: selectedEmail,
        focus_area: feedbackDraft.focus,
        strengths: feedbackDraft.strengths
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
      });
      toast.success("Feedback reflection saved.");
      setFeedbackDraft({ focus: "", strengths: "" });
      setKaiReply(result.reflection_prompt ?? "Reflection captured.");
    } catch (err) {
      console.error(err);
      toast.error("Feedback simulation failed.");
    }
  };

  const handleKaiSend = async () => {
    if (!kaiMessage.trim()) return;
    try {
      const { reply } = await sendKaiMessage({ email: selectedEmail, q: kaiMessage });
      setKaiReply(reply);
      setKaiMessage("");
    } catch (err) {
      console.error(err);
      toast.error("Kai is unavailable. Check OpenAI key.");
    }
  };

  return (
    <div className="app-shell">
      <ToastViewport />
      <header>
        <div className="brand">PSA PathFinder</div>
        <p>Personalised growth companion for PSA employees</p>
      </header>

      <main>
        <Panel title="Select Employee" description="Pick an employee to personalise plans and mentoring.">
          {loading ? (
            <div className="status">Loading employee data…</div>
          ) : (
            <select
              value={selectedEmail}
              onChange={async (evt) => {
                const email = evt.target.value;
                setSelectedEmail(email);
                if (email) {
                  await refreshMentors(email);
                }
              }}
            >
              {employees.map((emp) => (
                <option key={emp.email} value={emp.email}>
                  {emp.email} — {emp.role}
                </option>
              ))}
            </select>
          )}
        </Panel>

        {activePlan && (
          <section className="grid">
            <Panel title="Career Snapshot" description="Leadership potential, next moves, and skill focus.">
              <div className="stat" aria-live="polite">
                <div className="label">Leadership Potential Index</div>
                <div className="value">{activePlan.leadership_potential_index.toFixed(2)}</div>
              </div>
              <div className="stack">
                <h4>Next roles</h4>
                <ul>
                  {activePlan.next_roles.map((role) => (
                    <li key={role.role}>
                      <strong>{role.role}</strong>
                      <span>Fit: {Math.round(role.fit * 100)}%</span>
                      {role.missing_skills_example.length > 0 && (
                        <small>Gaps: {role.missing_skills_example.join(", ")}</small>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
              <div className="stack">
                <h4>Upskilling focus</h4>
                <ul>
                  {activePlan.upskilling_plan.slice(0, 5).map((item) => (
                    <li key={item.skill}>
                      <strong>{item.skill}</strong>
                      <small>
                        {item.function_area} • {item.specialization}
                      </small>
                      <span>{item.suggested_learning}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </Panel>

            <Panel
              title="Mentorship"
              description="Leverage PSA mentors and send an intro note."
              actionLabel="Draft mentor request"
              onAction={() => setMentorModalOpen(true)}
            >
              <ul className="list-cards">
                {mentors.map((mentor) => (
                  <li key={mentor.email}>
                    <div className="card-title">{mentor.email}</div>
                    <div className="card-sub">{mentor.role}</div>
                    <div className="card-meta">{mentor.department}</div>
                    <div className="card-score">Match score {Math.round(mentor.score * 100)}%</div>
                  </li>
                ))}
              </ul>
            </Panel>

            <Panel
              title="Courses"
              description="Filter curated content aligned with PSA paths."
              actionLabel="Search"
              onAction={() => loadCourses()}
            >
              <CourseFilters filters={courseFilters} onChange={setCourseFilters} />
              <ul className="list-courses">
                {courses.map((course) => (
                  <li key={course.title}>
                    <header>
                      <strong>{course.title}</strong>
                      <span>{course.provider}</span>
                    </header>
                    <p>{course.description}</p>
                    <footer>
                      <span>{course.difficulty}</span>
                      {course.duration_hours && <span>{course.duration_hours} hours</span>}
                      <a href={course.url} target="_blank" rel="noreferrer">
                        View
                      </a>
                    </footer>
                  </li>
                ))}
              </ul>
            </Panel>

            <Panel title="Recognition & Feedback" description="Celebrate peers and capture reflections.">
              <div className="form-grid">
                <div>
                  <label>Recipient</label>
                  <input
                    type="email"
                    placeholder="colleague@psa.com"
                    value={recognitionDraft.recipientEmail}
                    onChange={(evt) =>
                      setRecognitionDraft((state) => ({ ...state, recipientEmail: evt.target.value }))
                    }
                  />
                </div>
                <div>
                  <label>PSA value</label>
                  <select
                    value={recognitionDraft.psaValue}
                    onChange={(evt) =>
                      setRecognitionDraft((state) => ({ ...state, psaValue: evt.target.value }))
                    }
                  >
                    {defaultRecognitionValues.map((value) => (
                      <option key={value}>{value}</option>
                    ))}
                  </select>
                </div>
                <div className="full">
                  <label>Message</label>
                  <textarea
                    rows={3}
                    placeholder="Highlight impact, behaviour, and outcome."
                    value={recognitionDraft.message}
                    onChange={(evt) =>
                      setRecognitionDraft((state) => ({ ...state, message: evt.target.value }))
                    }
                  />
                </div>
                <button type="button" onClick={handleRecognitionSubmit}>
                  Send appreciation
                </button>
              </div>

              <div className="divider" />

              <div className="form-grid">
                <div className="full">
                  <label>Growth focus</label>
                  <input
                    type="text"
                    placeholder="e.g. improving stakeholder communication"
                    value={feedbackDraft.focus}
                    onChange={(evt) => setFeedbackDraft((state) => ({ ...state, focus: evt.target.value }))}
                  />
                </div>
                <div className="full">
                  <label>Strengths (comma separated)</label>
                  <input
                    type="text"
                    placeholder="cloud architecture, mentoring"
                    value={feedbackDraft.strengths}
                    onChange={(evt) =>
                      setFeedbackDraft((state) => ({ ...state, strengths: evt.target.value }))
                    }
                  />
                </div>
                <button type="button" onClick={handleFeedbackSubmit}>
                  Log reflection
                </button>
              </div>
            </Panel>

            <Panel title="Leadership league" description="Top emerging leaders based on sample index.">
              <ul className="list-leadership">
                {leadership.map((item: any) => (
                  <li key={item.email}>
                    <div>{item.email}</div>
                    <span>{item.role}</span>
                    <strong>{item.leadership_potential_index.toFixed(2)}</strong>
                    <small>Next: {item.next_roles.join(", ") || "n/a"}</small>
                  </li>
                ))}
              </ul>
            </Panel>

            <Panel title="Kai — Conversational AI" description="Well-being, skills, and career nudges." primary>
              <div className="kai-panel">
                <div className="kai-reply" aria-live="polite">
                  {kaiReply}
                </div>
                <div className="kai-input">
                  <input
                    type="text"
                    placeholder="Ask Kai about mentors, wellbeing, or next moves"
                    value={kaiMessage}
                    onChange={(evt) => setKaiMessage(evt.target.value)}
                    onKeyDown={(evt) => {
                      if (evt.key === "Enter") {
                        evt.preventDefault();
                        handleKaiSend();
                      }
                    }}
                  />
                  <button type="button" onClick={handleKaiSend}>
                    Send
                  </button>
                </div>
              </div>
            </Panel>
          </section>
        )}

        {isMentorModalOpen && (
          <div className="modal" role="dialog" aria-modal="true">
            <div className="modal-card">
              <header>
                <h3>Draft mentor request</h3>
                <button className="close" onClick={() => setMentorModalOpen(false)}>
                  ×
                </button>
              </header>
              <div className="modal-body">
                <label>Mentor email</label>
                <input
                  type="email"
                  value={mentorDraft.mentorEmail}
                  onChange={(evt) =>
                    setMentorDraft((state) => ({ ...state, mentorEmail: evt.target.value }))
                  }
                  placeholder="mentor@psa.com"
                />
                <label>Intro message</label>
                <textarea
                  rows={4}
                  value={mentorDraft.message}
                  onChange={(evt) =>
                    setMentorDraft((state) => ({ ...state, message: evt.target.value }))
                  }
                  placeholder="Share why you would value their support, goals, cadence, etc."
                />
              </div>
              <footer>
                <button type="button" onClick={handleMentorSubmit}>
                  Submit request
                </button>
              </footer>
            </div>
          </div>
        )}
      </main>

      <footer>
        <small>Prototype • PSA PathFinder • Replace heuristics with production services when ready.</small>
      </footer>
    </div>
  );
}

export default App;
