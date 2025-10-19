const $ = (sel) => document.querySelector(sel);

async function api(path) {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

function setOutput(obj) {
  const el = $('#output');
  el.textContent = typeof obj === 'string' ? obj : JSON.stringify(obj, null, 2);
}

async function loadEmails() {
  try {
    const data = await api('/plans');
    const emails = Object.keys(data);
    const sel = $('#email-select');
    sel.innerHTML = '';
    for (const e of emails) {
      const opt = document.createElement('option');
      opt.value = e; opt.textContent = e;
      sel.appendChild(opt);
    }
  } catch (e) {
    setOutput({ error: String(e) });
  }
}

async function loadPlan() {
  const email = $('#email-select').value;
  if (!email) return;
  try {
    const data = await api(`/plans?email=${encodeURIComponent(email)}`);
    setOutput(data[email] ?? data);
  } catch (e) {
    setOutput({ error: String(e) });
  }
}

async function loadMentors() {
  const email = $('#email-select').value;
  if (!email) return;
  try {
    const data = await api(`/mentors?email=${encodeURIComponent(email)}&limit=3`);
    setOutput(data);
  } catch (e) {
    setOutput({ error: String(e) });
  }
}

async function searchCourses() {
  const s = $('#course-skill').value.trim();
  const d = $('#course-difficulty').value;
  const min = $('#course-min').value;
  const max = $('#course-max').value;
  const qs = new URLSearchParams();
  if (s) qs.set('skill', s);
  if (d) qs.set('difficulty', d);
  if (min) qs.set('min_hours', min);
  if (max) qs.set('max_hours', max);
  try {
    const data = await api(`/courses?${qs.toString()}`);
    setOutput(data);
  } catch (e) {
    setOutput({ error: String(e) });
  }
}

async function sendChat() {
  const email = $('#email-select').value;
  const q = $('#chat-input').value.trim();
  if (!q) return;
  try {
    const qp = new URLSearchParams({ q });
    if (email) qp.set('email', email);
    const data = await api(`/chat?${qp.toString()}`);
    $('#chat-reply').textContent = data.reply ?? '';
  } catch (e) {
    $('#chat-reply').textContent = `Error: ${String(e)}`;
  }
}

window.addEventListener('DOMContentLoaded', () => {
  loadEmails();
  $('#btn-load-plan').addEventListener('click', loadPlan);
  $('#btn-mentors').addEventListener('click', loadMentors);
  $('#btn-courses').addEventListener('click', searchCourses);
  $('#btn-chat').addEventListener('click', sendChat);
});

