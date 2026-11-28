/* Contract Assistant v3: the browser side. Plain JavaScript, no framework, no build step.

   What it does, in order:
   1. Ask the server who is logged in (GET /api/me). If nobody, show the mock login.
   2. On a question, POST it to /api/ask/stream and read the answer as server-sent events.
      The server sends one event each time an agent finishes, so the steps tick off live.
   3. Show the answer, plus a "how this answer was built" panel (facts and passages).

   Security note: everything the model writes is added with textContent / text nodes,
   never innerHTML, so a model reply can not inject HTML or scripts into the page.
   The browser never sends client_id. The server takes it from the login cookie. */

const SVG_NS = 'http://www.w3.org/2000/svg';
const $ = (selector) => document.querySelector(selector);

/* ---------- small helpers ---------- */

/** Build an element: h('div', {class: 'x', text: 'hi'}, child, child) */
function h(tag, props = {}, ...children) {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(props)) {
    if (value === null || value === undefined || value === false) continue;
    if (key === 'class') el.className = value;
    else if (key === 'text') el.textContent = value;
    else if (key.startsWith('on')) el.addEventListener(key.slice(2), value);
    else el.setAttribute(key, value === true ? '' : value);
  }
  for (const child of children.flat()) if (child !== null && child !== undefined) el.append(child);
  return el;
}

function icon(name) {
  const svg = document.createElementNS(SVG_NS, 'svg');
  svg.setAttribute('class', 'icon');
  svg.setAttribute('aria-hidden', 'true');
  const use = document.createElementNS(SVG_NS, 'use');
  use.setAttribute('href', `#i-${name}`);
  svg.append(use);
  return svg;
}

const plural = (n, word) => `${n} ${word}${n === 1 ? '' : 's'}`;
const fmtMs = (ms) => (ms < 1000 ? `${ms} ms` : `${(ms / 1000).toFixed(1)} s`);
const dateFmt = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric', timeZone: 'UTC' });
const fmtDate = (iso) => (iso ? dateFmt.format(new Date(`${iso}T00:00:00Z`)) : '—');
const numFmt = new Intl.NumberFormat('en-US');
const initials = (name) => name.split(/\s+/).slice(0, 2).map((w) => w[0]).join('').toUpperCase();
const titleCase = (id) => id.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());

function announce(text) { $('#sr-status').textContent = text; }

/** Keep the newest content in view, but only if the reader was already at the bottom. */
function keepPinned(change) {
  const thread = $('#thread');
  const pinned = thread.scrollHeight - thread.scrollTop - thread.clientHeight < 140;
  change();
  if (pinned) thread.scrollTop = thread.scrollHeight;
}

async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: options.body ? { 'Content-Type': 'application/json' } : {},
    credentials: 'same-origin',
    ...options,
  });
  return res;
}

/* ---------- state ---------- */

let user = null;        // {username, name, client_id}
let asOf = '';          // the demo date, an ISO string
let busy = false;
let controller = null;  // lets the Stop button cancel a request
let lastQuestion = '';

/* ---------- login ---------- */

async function showLogin(message) {
  user = null;
  $('#app').hidden = true;
  $('#login').hidden = false;
  const error = $('#login-error');
  error.hidden = !message;
  if (message) error.replaceChildren(icon('alert'), h('div', { class: 'alert-body', text: message }));

  const list = $('#user-list');
  try {
    const res = await api('/api/users');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const users = await res.json();
    list.replaceChildren(...users.map((u) => h('li', {},
      h('button', { class: 'user-row', type: 'button', onclick: (e) => login(u.username, e.currentTarget) },
        h('span', { class: 'avatar', 'aria-hidden': 'true', text: initials(u.name) }),
        h('span', {}, h('strong', { text: u.name.split(' (')[0] }),
          h('small', { text: (u.name.match(/\((.*)\)/) || [, ''])[1] }),
          h('code', { text: `client_id: ${u.client_id}` })))))
    );
    list.querySelector('button')?.focus();
  } catch (err) {
    list.replaceChildren();
    error.hidden = false;
    error.replaceChildren(icon('alert'), h('div', { class: 'alert-body' },
      h('strong', { text: 'Could not load the attorney list.' }),
      `Is the server running? (${err.message})`));
  }
}

async function login(username, button) {
  button.disabled = true;
  const res = await api('/api/login', { method: 'POST', body: JSON.stringify({ username }) });
  if (!res.ok) {
    button.disabled = false;
    return showLogin('Login failed. Please try again.');
  }
  await boot();
}

async function logout() {
  controller?.abort();
  await api('/api/logout', { method: 'POST' });
  $('#thread-inner').replaceChildren();
  await showLogin();
}

/* ---------- the chat shell ---------- */

async function boot() {
  const res = await api('/api/me');
  if (!res.ok) return showLogin('The server returned an error. Check its log.');
  const me = await res.json();
  if (!me.user) return showLogin();
  user = me.user;
  asOf = me.as_of_date;

  $('#login').hidden = true;
  $('#app').hidden = false;
  const [shortName, team] = [user.name.split(' (')[0], (user.name.match(/\((.*)\)/) || [, ''])[1]];
  $('#who-avatar').textContent = initials(shortName);
  $('#who-name').textContent = shortName;
  $('#who-team').textContent = team;
  $('#who-client').textContent = `client_id: ${user.client_id}`;
  $('#as-of').textContent = fmtDate(asOf);

  $('#thread-inner').replaceChildren(emptyState());
  $('#question').focus();
}

const SUGGESTIONS = [
  ['Which contracts expire in the next 90 days?', 'Postgres'],
  ['What does the liability clause say in the CloudServe contract?', 'Knowledge Base'],
  ['Which contracts auto-renew within 90 days and have unlimited liability?', 'Both'],
];

function emptyState() {
  return h('section', { class: 'empty', id: 'empty' },
    h('h2', { text: `Ask about the ${titleCase(user.client_id)} contracts` }),
    h('p', { text: 'Try these in order. The tag shows which agent usually does the work. Open "How this answer was built" under each answer to check it.' }),
    h('ul', { class: 'suggest' }, SUGGESTIONS.map(([q, tag]) => h('li', {},
      h('button', { type: 'button', onclick: () => ask(q) },
        h('span', { text: q }), h('span', { class: 'tag', text: tag }))))));
}

/* ---------- the composer ---------- */

const box = () => $('#question');

function resizeBox() {
  box().style.height = 'auto';
  box().style.height = `${Math.min(box().scrollHeight, 144)}px`;
}

function refreshSend() {
  const send = $('#send');
  send.classList.toggle('stop', busy);
  send.replaceChildren(icon(busy ? 'stop' : 'send'));
  send.setAttribute('aria-label', busy ? 'Stop' : 'Send question');
  send.disabled = !busy && box().value.trim() === '';
}

$('#composer').addEventListener('submit', (e) => {
  e.preventDefault();
  if (busy) return controller?.abort();
  const q = box().value.trim();
  if (q) ask(q);
});
box().addEventListener('input', () => { resizeBox(); refreshSend(); });
box().addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) {
    e.preventDefault();
    $('#composer').requestSubmit();
  }
});
$('#logout').addEventListener('click', logout);

/* ---------- asking ---------- */

async function ask(question) {
  if (busy) return;
  busy = true;
  lastQuestion = question;
  box().value = '';
  resizeBox();
  refreshSend();
  $('#empty')?.remove();

  const bot = createBotMessage();
  $('#thread-inner').append(h('div', { class: 'msg user' }, h('div', { class: 'bubble', text: question })), bot.root);
  $('#thread').scrollTop = $('#thread').scrollHeight;  // sending always jumps to the new question
  announce('Working on your question.');

  controller = new AbortController();
  try {
    const res = await api('/api/ask/stream', { method: 'POST', body: JSON.stringify({ question }), signal: controller.signal });
    if (res.status === 401) { busy = false; return showLogin('Your session ended. Please log in again.'); }
    if (!res.ok) throw new Error(res.status === 422 ? 'The question must be between 1 and 1000 characters.' : `The server answered HTTP ${res.status}.`);

    let finished = false;
    for await (const { event, data } of readEvents(res)) {
      keepPinned(() => {
        if (event === 'step') handleStep(bot, data.node, data.ms, data.data);
        else if (event === 'done') { finished = true; finish(bot, data.ms); }
        else if (event === 'error') { finished = true; fail(bot, data.message); }
      });
    }
    if (!finished) keepPinned(() => fail(bot, 'The connection closed before the answer was complete.'));
  } catch (err) {
    keepPinned(() => (err.name === 'AbortError' ? stopped(bot) : fail(bot, err.message)));
  } finally {
    busy = false;
    controller = null;
    refreshSend();
    box().focus();
  }
}

/** Read a server-sent-events response. (EventSource can not POST, so we parse it by hand.) */
async function* readEvents(res) {
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    let end;
    while ((end = buffer.indexOf('\n\n')) >= 0) {
      const raw = buffer.slice(0, end);
      buffer = buffer.slice(end + 2);
      let event = 'message';
      const data = [];
      for (const line of raw.split('\n')) {
        if (line.startsWith('event:')) event = line.slice(6).trim();
        else if (line.startsWith('data:')) data.push(line.slice(5).trimStart());
      }
      if (data.length) yield { event, data: JSON.parse(data.join('\n')) };
    }
  }
}

/* ---------- one assistant message ---------- */

const STEP_LABEL = { router: 'Router', metadata_agent: 'Postgres facts', rag_agent: 'Knowledge Base', merge: 'Answer' };
// After the router decides, these are the steps still to come.
const PLAN = { rag: ['rag_agent', 'merge'], metadata: ['metadata_agent', 'merge'], both: ['metadata_agent', 'rag_agent', 'merge'] };
const ROUTE_TEXT = {
  rag: 'It is about what a clause says, so only the Knowledge Base was searched.',
  metadata: 'It needs exact facts, so only Postgres was queried.',
  both: 'It needs both: Postgres first found which contracts qualify, then the Knowledge Base read their clauses.',
};

function createBotMessage() {
  const statusIcon = h('span', { class: 'sum-icon' }, h('span', { class: 'spin' }));
  const sumText = h('span', { class: 'sum-text', text: 'Working on it' });
  const summary = h('summary', {}, statusIcon, sumText, icon('chevron'));
  const steps = h('ol', { class: 'steps' });
  const body = h('div', { class: 'trace-body' });
  const details = h('details', { class: 'trace', open: true }, summary, steps, body);
  const answer = h('div', { class: 'answer' });
  const extra = h('div');
  const root = h('article', { class: 'msg bot' },
    h('div', { class: 'avatar-bot', 'aria-hidden': 'true' }, icon('scale')),
    h('div', { class: 'bot-col' }, details, answer, extra));
  const bot = { root, details, steps, body, answer, extra, statusIcon, sumText, rows: new Map(), result: {} };
  addStep(bot, 'router', 'active');
  return bot;
}

function stateIcon(state) {
  if (state === 'active') return h('span', { class: 'spin' });
  if (state === 'done') return icon('check');
  if (state === 'error') return icon('x');
  if (state === 'skipped') return icon('minus');
  return h('span', { class: 'dot' });
}

function addStep(bot, node, state) {
  const iconCell = h('span', { class: 'step-icon' }, stateIcon(state));
  const detail = h('span', { class: 'step-detail' });
  const time = h('span', { class: 'step-time' });
  const li = h('li', { class: 'step', 'data-state': state }, iconCell,
    h('span', {}, h('span', { class: 'step-name', text: STEP_LABEL[node] }), detail), time);
  bot.steps.append(li);
  bot.rows.set(node, { li, iconCell, detail, time, state });
}

function setStep(bot, node, state, detail = null, ms = null) {
  const row = bot.rows.get(node);
  if (!row) return;
  row.state = state;
  row.li.dataset.state = state;
  row.iconCell.replaceChildren(stateIcon(state));
  if (detail !== null) row.detail.replaceChildren(...detail);
  if (ms !== null) row.time.textContent = fmtMs(ms);
}

const code = (text) => h('code', { text });

function queryText(call) {
  const extras = [];
  if (['expiring_within', 'auto_renewing_within'].includes(call.tool)) extras.push(`${call.days} days`);
  if (call.tool === 'find_by_counterparty') extras.push(`"${call.counterparty}"`);
  return extras.length ? `${call.tool}(${extras.join(', ')})` : `${call.tool}()`;
}

function describe(node, data) {
  if (node === 'router') return [`chose `, code(data.route)];
  if (node === 'metadata_agent') return [code(queryText(data.tool_call || {})), ` found ${plural((data.contracts || []).length, 'contract')}`];
  if (node === 'rag_agent') return [`${plural((data.passages || []).length, 'passage')} from the contracts`];
  return ['written from the facts and passages'];
}

function handleStep(bot, node, ms, data) {
  Object.assign(bot.result, data);
  setStep(bot, node, 'done', describe(node, data), ms);
  if (node === 'router') {
    for (const next of PLAN[data.route] || PLAN.both) addStep(bot, next, 'pending');
  }
  if (node === 'merge') {
    renderMarkdown(bot.answer, data.answer || '');
    announce('Answer ready.');
  } else {
    const next = [...bot.rows.entries()].find(([, row]) => row.state === 'pending');
    if (next) setStep(bot, next[0], 'active');
  }
}

function finish(bot, totalMs) {
  for (const [node, row] of bot.rows) {
    if (row.state === 'pending' || row.state === 'active') {
      const why = node === 'rag_agent' ? 'skipped, no contracts matched' : 'skipped';
      setStep(bot, node, 'skipped', [why]);
    }
  }
  bot.statusIcon.className = 'sum-icon ok';
  bot.statusIcon.replaceChildren(icon('check'));
  bot.sumText.textContent = `How this answer was built · ${bot.result.route || 'unknown'} · ${fmtMs(totalMs)}`;
  bot.body.replaceChildren(...traceBody(bot.result));
  bot.details.open = false;
}

function fail(bot, message) {
  for (const [node, row] of bot.rows) {
    if (row.state === 'active') setStep(bot, node, 'error', ['failed']);
    else if (row.state === 'pending') setStep(bot, node, 'skipped');
  }
  bot.statusIcon.className = 'sum-icon bad';
  bot.statusIcon.replaceChildren(icon('alert'));
  bot.sumText.textContent = 'This question could not be answered';
  bot.details.open = true;
  bot.extra.replaceChildren(h('div', { class: 'alert', role: 'alert' }, icon('alert'),
    h('div', { class: 'alert-body' },
      h('strong', { text: 'Something went wrong.' }),
      message,
      h('div', {}, h('button', { class: 'btn', type: 'button', onclick: () => { bot.root.previousSibling?.remove(); bot.root.remove(); ask(lastQuestion); } }, 'Try again')))));
  announce('The question failed.');
}

function stopped(bot) {
  for (const [node, row] of bot.rows) if (row.state === 'active' || row.state === 'pending') setStep(bot, node, 'skipped', ['stopped']);
  bot.statusIcon.replaceChildren(icon('minus'));
  bot.sumText.textContent = 'Stopped';
  announce('Stopped.');
}

/* ---------- the "how this answer was built" body ---------- */

function traceBody(result) {
  const parts = [];
  if (result.route) parts.push(h('p', { text: ROUTE_TEXT[result.route] || '' }));
  if (result.tool_call) {
    parts.push(h('p', {}, 'Query run for this client only: ', code(queryText(result.tool_call))));
  }
  if ((result.contracts || []).length) {
    parts.push(h('div', {}, h('h3', { text: `Facts from Postgres (${result.contracts.length})` }), factsTable(result.contracts)));
  }
  if ((result.passages || []).length) {
    parts.push(h('div', {}, h('h3', { text: `Passages from the Knowledge Base (${result.passages.length})` }),
      h('div', { class: 'passages' }, result.passages.map((p) => h('figure', { class: 'passage' },
        h('figcaption', {}, h('span', { class: 'cite', text: passageLabel(p) })),
        h('p', { text: p.text, tabindex: '0' }))))));
  }
  return parts;
}

const passageLabel = (p) => `${p.contract_id} ${p.counterparty}`.trim() || 'contract';

function factsTable(rows) {
  const head = ['Contract', 'Expires', 'Notice deadline', 'Auto-renews', 'Annual value'];
  return h('div', { class: 'table-wrap', role: 'region', 'aria-label': 'Contract facts from Postgres', tabindex: '0' },
    h('table', { class: 'facts' },
      h('thead', {}, h('tr', {}, head.map((t, i) => h('th', { scope: 'col', class: i === 4 ? 'num' : '', text: t })))),
      h('tbody', {}, rows.map((r) => {
        const passed = r.notice_deadline && asOf && r.notice_deadline < asOf;
        return h('tr', {},
          h('td', { class: 'who-cell' }, h('strong', { text: r.contract_id }), h('span', { text: r.counterparty })),
          h('td', { text: fmtDate(r.expiry_date) }),
          h('td', {}, fmtDate(r.notice_deadline), passed ? [' ', h('span', { class: 'pill warn', text: 'passed' })] : null),
          h('td', {}, h('span', { class: `pill ${r.auto_renew ? 'yes' : ''}`, text: r.auto_renew ? 'Yes' : 'No' })),
          h('td', { class: 'num', text: r.annual_value == null ? '—' : numFmt.format(Number(r.annual_value)) }));
      }))));
}

/* ---------- the answer text ---------- */

/** Render the small part of Markdown that models actually use: paragraphs, lists, **bold**, `code`
    and [citations]. Everything goes in as text nodes, so nothing can inject HTML. */
function renderMarkdown(container, text) {
  container.replaceChildren();
  let list = null;
  let paragraph = [];
  const flushParagraph = () => {
    if (paragraph.length) container.append(h('p', {}, inline(paragraph.join(' '))));
    paragraph = [];
  };
  for (const raw of text.split('\n')) {
    const line = raw.trim();
    const bullet = line.match(/^[-*•]\s+(.*)/);
    const numbered = line.match(/^\d+[.)]\s+(.*)/);
    if (bullet || numbered) {
      flushParagraph();
      const kind = bullet ? 'ul' : 'ol';
      if (!list || list.tagName.toLowerCase() !== kind) {
        list = h(kind);
        container.append(list);
      }
      list.append(h('li', {}, inline((bullet || numbered)[1])));
    } else if (line === '') {
      flushParagraph();
      list = null;
    } else {
      list = null;
      paragraph.push(line.replace(/^#{1,6}\s+/, ''));
    }
  }
  flushParagraph();
}

function inline(text) {
  const nodes = [];
  const pattern = /\*\*(.+?)\*\*|`([^`]+)`|\[([^\]]+)\](?!\()/g;
  let last = 0;
  for (const m of text.matchAll(pattern)) {
    if (m.index > last) nodes.push(text.slice(last, m.index));
    if (m[1] !== undefined) nodes.push(h('strong', { text: m[1] }));
    else if (m[2] !== undefined) nodes.push(h('code', { text: m[2] }));
    else nodes.push(h('span', { class: 'cite', text: m[3] }));
    last = m.index + m[0].length;
  }
  if (last < text.length) nodes.push(text.slice(last));
  return nodes;
}

/* ---------- go ---------- */

refreshSend();
boot();
