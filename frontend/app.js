// ============================================================
// TaskFlow Pro — Frontend
// 03-design: Vanilla JS + 모듈 변수 + DOM 직접 갱신 + 3초 폴링
// ============================================================

const API_BASE = '/api';
const POLL_INTERVAL_MS = 3000;

let tasks = [];
let pollTimer = null;

// ---------------- 테마 (라이트/다크) ----------------
function currentTheme() {
  return document.documentElement.classList.contains('dark') ? 'dark' : 'light';
}

function applyTheme(theme) {
  const root = document.documentElement;
  if (theme === 'dark') root.classList.add('dark');
  else root.classList.remove('dark');
  const icon = document.getElementById('themeIcon');
  if (icon) icon.textContent = theme === 'dark' ? '☀️' : '🌙';
}

function initTheme() {
  // index.html 인라인 스크립트가 이미 클래스를 적용함 — 아이콘만 동기화
  applyTheme(currentTheme());
  document.getElementById('themeToggle').addEventListener('click', () => {
    const next = currentTheme() === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    localStorage.setItem('theme', next);
  });
}

// ---------------- 시간 포맷 ----------------
// 02-specs: 목록 카드는 "D-N HH:MM" (지난 마감은 "D+N HH:MM")
function formatDue(dueIso) {
  if (!dueIso) return '';
  const due = new Date(dueIso);
  if (isNaN(due.getTime())) return '';

  const now = new Date();
  const dueDay = new Date(due.getFullYear(), due.getMonth(), due.getDate());
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const dayDiff = Math.round((dueDay - today) / 86400000);

  const hh = String(due.getHours()).padStart(2, '0');
  const mm = String(due.getMinutes()).padStart(2, '0');
  const sign = dayDiff >= 0 ? '-' : '+';
  const abs = Math.abs(dayDiff);
  return `D${sign}${abs} ${hh}:${mm}`;
}

// created_at: 상대 시간 ("n분 전") — dayjs + ko locale
function formatRelative(iso) {
  if (!iso) return '';
  const d = dayjs(iso);
  return d.isValid() ? d.fromNow() : '';
}

// 절대 시간 (툴팁용): "YYYY-MM-DD HH:mm"
function formatAbsolute(iso) {
  if (!iso) return '';
  const d = dayjs(iso);
  return d.isValid() ? d.format('YYYY-MM-DD HH:mm') : '';
}

// datetime-local <-> ISO 8601(UTC) 변환
function toLocalDateTimeInput(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  if (isNaN(d.getTime())) return '';
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function fromLocalDateTimeInput(value) {
  if (!value) return null;
  const d = new Date(value);
  if (isNaN(d.getTime())) return null;
  return d.toISOString();
}

// ---------------- 상태 배지 ----------------
const STATUS_LABEL = { todo: '할 일', in_progress: '진행 중', done: '완료' };
const STATUS_CLASS = {
  todo: 'bg-slate-200 text-slate-700 dark:bg-slate-700 dark:text-slate-200',
  in_progress: 'bg-amber-200 text-amber-900 dark:bg-amber-500/30 dark:text-amber-200',
  done: 'bg-emerald-200 text-emerald-900 dark:bg-emerald-500/30 dark:text-emerald-200',
};

// ---------------- API 래퍼 ----------------
async function api(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

async function fetchTasks() {
  tasks = await api('/tasks');
  renderList();
}

async function fetchTaskDetail(id) {
  return api(`/tasks/${id}`);
}

async function createTask(payload) {
  await api('/tasks', { method: 'POST', body: JSON.stringify(payload) });
  await fetchTasks();
}

async function updateTask(id, payload) {
  await api(`/tasks/${id}`, { method: 'PUT', body: JSON.stringify(payload) });
  await fetchTasks();
}

async function deleteTask(id) {
  await api(`/tasks/${id}`, { method: 'DELETE' });
  await fetchTasks();
}

// ---------------- 렌더 ----------------
function renderList() {
  const listEl = document.getElementById('taskList');
  const emptyEl = document.getElementById('emptyState');
  listEl.innerHTML = '';

  if (!tasks.length) {
    emptyEl.classList.remove('hidden');
    return;
  }
  emptyEl.classList.add('hidden');

  for (const t of tasks) {
    const card = document.createElement('article');
    card.className =
      'group rounded-2xl backdrop-blur bg-white/70 dark:bg-white/10 shadow-md hover:shadow-lg transition p-4 flex items-center gap-3 cursor-pointer';
    card.dataset.id = t.id;

    const badge = document.createElement('span');
    badge.className = `text-xs px-2 py-1 rounded-lg ${STATUS_CLASS[t.status] || ''}`;
    badge.textContent = STATUS_LABEL[t.status] || t.status;

    const titleWrap = document.createElement('div');
    titleWrap.className = 'flex-1 min-w-0';

    const titleSpan = document.createElement('div');
    titleSpan.className = 'font-medium truncate';
    titleSpan.textContent = t.title;
    titleWrap.appendChild(titleSpan);

    const metaRow = document.createElement('div');
    metaRow.className = 'flex flex-wrap gap-x-2 gap-y-0.5 mt-0.5 text-xs';

    if (t.due_at) {
      const dueEl = document.createElement('span');
      dueEl.className = 'text-slate-500 dark:text-slate-400';
      dueEl.textContent = formatDue(t.due_at);
      dueEl.title = formatAbsolute(t.due_at);
      metaRow.appendChild(dueEl);
    }

    if (t.created_at) {
      const createdEl = document.createElement('span');
      createdEl.className = 'text-slate-400 dark:text-slate-500';
      createdEl.textContent = `· 생성 ${formatRelative(t.created_at)}`;
      createdEl.title = formatAbsolute(t.created_at);
      metaRow.appendChild(createdEl);
    }

    if (metaRow.children.length) titleWrap.appendChild(metaRow);

    const delBtn = document.createElement('button');
    delBtn.type = 'button';
    delBtn.className =
      'min-w-[44px] min-h-[44px] rounded-xl px-2 text-slate-500 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 transition';
    delBtn.setAttribute('aria-label', '삭제');
    delBtn.textContent = '🗑';
    delBtn.addEventListener('click', async (e) => {
      e.stopPropagation();
      if (!confirm(`"${t.title}"을(를) 삭제하시겠습니까?`)) return;
      await deleteTask(t.id);
    });

    card.appendChild(badge);
    card.appendChild(titleWrap);
    card.appendChild(delBtn);
    card.addEventListener('click', () => openEditModal(t.id));

    listEl.appendChild(card);
  }
}

// ---------------- 수정 모달 ----------------
async function openEditModal(id) {
  const detail = await fetchTaskDetail(id);
  document.getElementById('editId').value = detail.id;
  document.getElementById('editTitle').value = detail.title;
  document.getElementById('editDescription').value = detail.description || '';
  document.getElementById('editStatus').value = detail.status;
  document.getElementById('editDueAt').value = toLocalDateTimeInput(detail.due_at);
  document.getElementById('editModal').classList.remove('hidden');
}

function closeEditModal() {
  document.getElementById('editModal').classList.add('hidden');
}

// ---------------- 폼 바인딩 ----------------
function initForms() {
  document.getElementById('createForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('titleInput').value.trim();
    if (!title) return;
    const payload = {
      title,
      status: document.getElementById('statusInput').value,
    };
    const dueIso = fromLocalDateTimeInput(document.getElementById('dueAtInput').value);
    if (dueIso) payload.due_at = dueIso;
    try {
      await createTask(payload);
      e.target.reset();
    } catch (err) {
      console.error(err);
      alert('작업 생성에 실패했습니다.');
    }
  });

  document.getElementById('editForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = Number(document.getElementById('editId').value);
    const payload = {
      title: document.getElementById('editTitle').value.trim(),
      description: document.getElementById('editDescription').value,
      status: document.getElementById('editStatus').value,
      due_at: fromLocalDateTimeInput(document.getElementById('editDueAt').value),
    };
    try {
      await updateTask(id, payload);
      closeEditModal();
    } catch (err) {
      console.error(err);
      alert('작업 수정에 실패했습니다.');
    }
  });

  document.getElementById('editCancel').addEventListener('click', closeEditModal);
  document.getElementById('editModal').addEventListener('click', (e) => {
    if (e.target.id === 'editModal') closeEditModal();
  });
}

// ---------------- 폴링 ----------------
function startPolling() {
  if (pollTimer) clearInterval(pollTimer);
  pollTimer = setInterval(() => {
    // 모달 열려 있는 동안은 폴링 결과로 화면을 흔들지 않음
    if (document.getElementById('editModal').classList.contains('hidden')) {
      fetchTasks().catch((err) => console.error(err));
    }
  }, POLL_INTERVAL_MS);
}

// ---------------- 부팅 ----------------
window.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initForms();
  fetchTasks()
    .then(startPolling)
    .catch((err) => {
      console.error(err);
      document.getElementById('emptyState').textContent =
        '서버에 연결할 수 없습니다.';
      document.getElementById('emptyState').classList.remove('hidden');
    });
});
