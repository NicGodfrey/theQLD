/* AGENT FACTORY by MERIDIAN — workflow × gateway pack composer (local-first). */
'use strict';

const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const LS_KEY = 'meridian.agentfactory.v1';
const GATE_KEY = 'meridian.proxygate.v1';
const uid = p => p + Math.random().toString(36).slice(2, 8);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
function download(name, text, mime = 'application/json') {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([text], { type: mime }));
  a.download = name; a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 4000);
}
let toastT = null;
function toast(msg) {
  const t = $('#toast'); t.textContent = msg; t.classList.add('show');
  clearTimeout(toastT); toastT = setTimeout(() => t.classList.remove('show'), 1800);
}

/* ---------- catalogs ---------- */
const TOOLS = ['llm', 'image', 'search', 'webhook', 'review'];
const MODELS = ['gpt-4o', 'claude-3.7-sonnet', 'gemini-2.0-flash', 'deepseek-v3', 'llama-3.1-70b (local)', 'flux-pro', 'sdxl-turbo', '—'];
const TEMPLATES = {
  create: { label: 'Flow Create', zh: '创作', desc: 'Concepts → briefs → hero assets → review.', steps: [
    { title: 'Ideate 10 concepts from campaign goal', tool: 'llm', model: 'gpt-4o' },
    { title: 'Expand winner into a visual brief', tool: 'llm', model: 'claude-3.7-sonnet' },
    { title: 'Generate hero assets', tool: 'image', model: 'flux-pro' },
    { title: 'Human review gate', tool: 'review', model: '—' },
  ]},
  market: { label: 'Flow Market', zh: '营销', desc: 'Audience → angles → variants → schedule.', steps: [
    { title: 'Mine audience pains from community threads', tool: 'search', model: 'gemini-2.0-flash' },
    { title: 'Draft 5 campaign angles', tool: 'llm', model: 'gpt-4o' },
    { title: 'Spin 20 ad copy variants per angle', tool: 'llm', model: 'deepseek-v3' },
    { title: 'Push winners to scheduler', tool: 'webhook', model: '—' },
  ]},
  content: { label: 'Flow Content', zh: '内容', desc: 'Topics → outline → draft → SEO polish.', steps: [
    { title: 'Cluster search intents into topics', tool: 'search', model: 'gemini-2.0-flash' },
    { title: 'Outline pillar article', tool: 'llm', model: 'claude-3.7-sonnet' },
    { title: 'Draft sections in parallel', tool: 'llm', model: 'deepseek-v3' },
    { title: 'SEO polish + internal links', tool: 'llm', model: 'gpt-4o' },
    { title: 'Publish payload to CMS', tool: 'webhook', model: '—' },
  ]},
  ops: { label: 'Flow Ops', zh: '用户运营', desc: 'Segment → lifecycle → triage → digest.', steps: [
    { title: 'Segment users by behaviour', tool: 'llm', model: 'deepseek-v3' },
    { title: 'Compose lifecycle messages per segment', tool: 'llm', model: 'claude-3.7-sonnet' },
    { title: 'Sentiment triage on replies', tool: 'llm', model: 'gemini-2.0-flash' },
    { title: 'Weekly ops digest to Slack', tool: 'webhook', model: '—' },
  ]},
};

/* ---------- state ---------- */
const freshDraft = base => ({
  name: '',
  base,
  steps: TEMPLATES[base].steps.map(s => ({ id: uid('s'), ...s })),
  route: { mode: 'proxygate', path: '', upstream: '' },
});
let state = { draft: freshDraft('create'), packs: [] };
try {
  const raw = JSON.parse(localStorage.getItem(LS_KEY));
  if (raw && raw.draft) state = raw;
} catch (e) { /* fresh */ }
const save = () => localStorage.setItem(LS_KEY, JSON.stringify(state));

/* ---------- proxy gate integration ---------- */
function readGateRoutes() {
  try {
    const gate = JSON.parse(localStorage.getItem(GATE_KEY));
    if (!gate || !Array.isArray(gate.routes)) return [];
    return gate.routes.map(r => {
      const up = (gate.upstreams || []).find(u => u.id === r.upstreamId);
      return { path: r.path, upstream: up ? up.name : 'unknown', kind: up ? up.kind : '?' };
    });
  } catch (e) { return []; }
}

/* ---------- manifest ---------- */
function buildManifest(draft, meta = {}) {
  const route = resolveRoute(draft);
  return {
    schema: 'meridian.agentpack/1',
    meta: {
      name: draft.name || 'Untitled pack',
      base: draft.base,
      baseLabel: `${TEMPLATES[draft.base].label} · ${TEMPLATES[draft.base].zh}`,
      tool: 'AGENT FACTORY by MERIDIAN',
      createdAt: meta.createdAt || new Date().toISOString(),
      version: 1,
    },
    workflow: {
      steps: draft.steps.map((s, i) => ({ order: i + 1, id: s.id, title: s.title, tool: s.tool, model: s.model })),
    },
    routing: {
      mode: draft.route.mode,
      gateway: 'proxy-gate',
      path: route.path || '(unset)',
      upstream: route.upstream || '(unset)',
    },
    requirements: {
      env: ['GATEWAY_BASE_URL', 'GATEWAY_CLIENT_KEY'],
      services: ['MERIDIAN Proxy Gate (or any OpenAI-compatible reverse proxy)'],
    },
  };
}
function resolveRoute(draft) {
  if (draft.route.mode === 'manual') return { path: draft.route.path, upstream: draft.route.upstream };
  const routes = readGateRoutes();
  const found = routes.find(r => r.path === draft.route.path);
  return found || routes[0] || { path: '', upstream: '' };
}

/* ---------- render: builder ---------- */
function renderTemplates() {
  $('#tplRow').innerHTML = Object.entries(TEMPLATES).map(([k, t]) => `
    <button class="tpl ${state.draft.base === k ? 'sel' : ''}" data-tpl="${k}">
      <span class="zh">${esc(t.zh)}</span><h3>${esc(t.label)}</h3><p>${esc(t.desc)}</p>
    </button>`).join('');
}
function renderSteps() {
  $('#steps').innerHTML = state.draft.steps.map((s, i) => `
    <div class="steprow" data-id="${s.id}">
      <span class="num">${String(i + 1).padStart(2, '0')}</span>
      <input type="text" data-f="title" value="${esc(s.title)}" placeholder="step title">
      <select data-f="tool">${TOOLS.map(t => `<option ${s.tool === t ? 'selected' : ''}>${t}</option>`).join('')}</select>
      <select data-f="model">${MODELS.map(m => `<option ${s.model === m ? 'selected' : ''}>${esc(m)}</option>`).join('')}</select>
      <span style="display:flex;gap:5px;align-items:center">
        <span class="mv"><button data-act="up" title="Move up">▲</button><button data-act="down" title="Move down">▼</button></span>
        <button class="btn btn-danger btn-sm kill" data-act="del" title="Remove">×</button>
      </span>
    </div>`).join('') || '<p style="font-size:12px;color:var(--dim-2)">No steps — add one or reset to template.</p>';
}
function renderRouteBox() {
  const mode = state.draft.route.mode;
  $('#routeSource').value = mode;
  $('#routePickWrap').style.display = mode === 'proxygate' ? '' : 'none';
  $('#routeManualWrap').style.display = mode === 'manual' ? 'flex' : 'none';
  if (mode === 'proxygate') {
    const routes = readGateRoutes();
    $('#routePick').innerHTML = routes.length
      ? routes.map(r => `<option value="${esc(r.path)}" ${state.draft.route.path === r.path ? 'selected' : ''}>${esc(r.path)} → ${esc(r.upstream)}</option>`).join('')
      : '<option value="">(no routes found in Proxy Gate)</option>';
    $('#routeHint').innerHTML = routes.length
      ? `Found <b style="color:var(--acid)">${routes.length}</b> route(s) in this browser's Proxy Gate config.`
      : `No Proxy Gate config in this browser yet — open <a href="proxy-gate.html" style="color:var(--acid)">Proxy Gate</a> once, or switch to manual entry.`;
  } else {
    $('#routePath').value = state.draft.route.path;
    $('#routeUpstream').value = state.draft.route.upstream;
    $('#routeHint').textContent = 'Manual mode: describe the path and upstream your runner should call.';
  }
}
function renderManifest() {
  $('#manifestPreview').textContent = JSON.stringify(buildManifest(state.draft), null, 2);
}
function renderBuilder() {
  $('#draftName').value = state.draft.name;
  renderTemplates(); renderSteps(); renderRouteBox(); renderManifest();
}

/* ---------- render: dashboard ---------- */
function renderPacks() {
  $('#packCount').textContent = `${state.packs.length} pack${state.packs.length === 1 ? '' : 's'}`;
  $('#packs').innerHTML = state.packs.length ? state.packs.map(p => `
    <div class="pack" data-id="${p.id}">
      <div class="ph">
        <h3 title="${esc(p.manifest.meta.name)}">${esc(p.manifest.meta.name)}</h3>
        <span class="base base-${esc(p.manifest.meta.base)}">${esc(p.manifest.meta.base)}</span>
      </div>
      <div class="meta">
        <b>${p.manifest.workflow.steps.length}</b> steps · route <b>${esc(p.manifest.routing.path)}</b> → ${esc(p.manifest.routing.upstream)}<br>
        installed ${new Date(p.installedAt).toLocaleDateString()} · <b>${p.runs}</b> sim run${p.runs === 1 ? '' : 's'}
      </div>
      <div class="acts">
        <button class="btn btn-acid btn-sm" data-act="run">▶ Run</button>
        <button class="btn btn-sm" data-act="export">⇩ Export</button>
        <button class="btn btn-copper btn-sm" data-act="load">✎ Builder</button>
        <button class="btn btn-danger btn-sm" data-act="del">×</button>
      </div>
    </div>`).join('')
    : '<p style="font-size:12.5px;color:var(--dim-2);grid-column:1/-1">Nothing installed. Build a pack above, or import one.</p>';
}

/* ---------- run simulator ---------- */
let running = false;
function runPack(pack) {
  if (running) return toast('A run is already in progress');
  running = true;
  const log = $('#runlog');
  log.hidden = false;
  log.innerHTML = `<div class="info">▶ ${esc(pack.manifest.meta.name)} — simulated run · ${new Date().toLocaleTimeString()}</div>` +
    `<div class="dimline">routing via ${esc(pack.manifest.routing.path)} → ${esc(pack.manifest.routing.upstream)} (gateway: ${esc(pack.manifest.routing.gateway)})</div>`;
  const steps = pack.manifest.workflow.steps;
  let i = 0;
  const tick = () => {
    if (i >= steps.length) {
      const dur = (steps.length * 0.9 + Math.random() * 2).toFixed(1);
      log.innerHTML += `<div class="ok">✓ pack completed — ${steps.length} steps, ~${dur}s simulated wall-clock</div>`;
      log.scrollTop = log.scrollHeight;
      pack.runs++; running = false;
      save(); renderPacks();
      return;
    }
    const s = steps[i];
    const ms = Math.round(300 + Math.random() * 1400);
    const tok = s.tool === 'llm' ? Math.round(200 + Math.random() * 1600) : 0;
    const warn = Math.random() < 0.08;
    log.innerHTML += `<div>${warn ? '<span class="warn">▸ retry</span>' : '▸'} step ${i + 1}/${steps.length} — ${esc(s.title)} <span class="dimline">[${esc(s.tool)}${s.model && s.model !== '—' ? '/' + esc(s.model) : ''}] ${ms}ms${tok ? ' · ' + tok + ' tok' : ''}</span></div>`;
    log.scrollTop = log.scrollHeight;
    i++;
    setTimeout(tick, 260 + Math.random() * 420);
  };
  setTimeout(tick, 350);
}

/* ---------- events: builder ---------- */
$('#draftName').addEventListener('input', e => { state.draft.name = e.target.value; save(); renderManifest(); });
$('#tplRow').addEventListener('click', e => {
  const b = e.target.closest('[data-tpl]');
  if (!b) return;
  const base = b.dataset.tpl;
  if (state.draft.base !== base) {
    const keepName = state.draft.name;
    state.draft = freshDraft(base);
    state.draft.name = keepName;
    save(); renderBuilder();
    toast(TEMPLATES[base].label + ' template loaded');
  }
});
$('#btnReloadTpl').addEventListener('click', () => {
  const keep = { name: state.draft.name, route: state.draft.route };
  state.draft = freshDraft(state.draft.base);
  Object.assign(state.draft, keep);
  save(); renderBuilder(); toast('Steps reset to template');
});
$('#btnAddStep').addEventListener('click', () => {
  state.draft.steps.push({ id: uid('s'), title: 'New step', tool: 'llm', model: 'gpt-4o' });
  save(); renderSteps(); renderManifest();
});
$('#steps').addEventListener('click', e => {
  const btn = e.target.closest('[data-act]');
  if (!btn) return;
  const id = btn.closest('.steprow').dataset.id;
  const idx = state.draft.steps.findIndex(s => s.id === id);
  const act = btn.dataset.act;
  if (act === 'del') state.draft.steps.splice(idx, 1);
  else if (act === 'up' && idx > 0) [state.draft.steps[idx - 1], state.draft.steps[idx]] = [state.draft.steps[idx], state.draft.steps[idx - 1]];
  else if (act === 'down' && idx < state.draft.steps.length - 1) [state.draft.steps[idx + 1], state.draft.steps[idx]] = [state.draft.steps[idx], state.draft.steps[idx + 1]];
  else return;
  save(); renderSteps(); renderManifest();
});
$('#steps').addEventListener('input', e => {
  const inp = e.target.closest('[data-f]');
  if (!inp) return;
  const st = state.draft.steps.find(s => s.id === inp.closest('.steprow').dataset.id);
  if (!st) return;
  st[inp.dataset.f] = inp.value;
  save(); renderManifest();
});
$('#routeSource').addEventListener('change', e => {
  state.draft.route.mode = e.target.value;
  save(); renderRouteBox(); renderManifest();
});
$('#routePick').addEventListener('change', e => {
  state.draft.route.path = e.target.value;
  save(); renderManifest();
});
$('#btnRefreshRoutes').addEventListener('click', () => { renderRouteBox(); renderManifest(); toast('Re-read Proxy Gate config'); });
['routePath', 'routeUpstream'].forEach(id => $('#' + id).addEventListener('input', () => {
  state.draft.route.path = $('#routePath').value.trim();
  state.draft.route.upstream = $('#routeUpstream').value.trim();
  save(); renderManifest();
}));
$('#btnBuild').addEventListener('click', () => {
  if (!state.draft.steps.length) return toast('Add at least one step');
  const manifest = buildManifest(state.draft);
  if (!state.draft.name.trim()) manifest.meta.name = TEMPLATES[state.draft.base].label + ' pack #' + (state.packs.length + 1);
  state.packs.unshift({ id: uid('p'), installedAt: Date.now(), runs: 0, manifest });
  save(); renderPacks();
  toast(`“${manifest.meta.name}” installed`);
  $('#packs').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
});
$('#btnExportDraft').addEventListener('click', () => {
  const manifest = buildManifest(state.draft);
  download(`agent-pack-${(manifest.meta.name || 'draft').replace(/[^a-z0-9]+/gi, '-').toLowerCase()}.json`, JSON.stringify(manifest, null, 2));
  toast('Draft pack exported');
});

/* ---------- events: dashboard ---------- */
$('#packs').addEventListener('click', e => {
  const btn = e.target.closest('[data-act]');
  if (!btn) return;
  const pack = state.packs.find(p => p.id === btn.closest('.pack').dataset.id);
  if (!pack) return;
  const act = btn.dataset.act;
  if (act === 'run') runPack(pack);
  else if (act === 'export') {
    download(`agent-pack-${pack.manifest.meta.name.replace(/[^a-z0-9]+/gi, '-').toLowerCase()}.json`, JSON.stringify(pack.manifest, null, 2));
    toast('Pack exported');
  } else if (act === 'load') {
    const m = pack.manifest;
    state.draft = {
      name: m.meta.name,
      base: TEMPLATES[m.meta.base] ? m.meta.base : 'create',
      steps: m.workflow.steps.map(s => ({ id: s.id || uid('s'), title: s.title, tool: s.tool, model: s.model })),
      route: { mode: m.routing.mode === 'manual' ? 'manual' : 'proxygate', path: m.routing.path === '(unset)' ? '' : m.routing.path, upstream: m.routing.upstream === '(unset)' ? '' : m.routing.upstream },
    };
    save(); renderBuilder();
    window.scrollTo({ top: 0, behavior: 'smooth' });
    toast('Pack loaded into builder');
  } else if (act === 'del') {
    if (!confirm(`Uninstall “${pack.manifest.meta.name}”?`)) return;
    state.packs = state.packs.filter(p => p.id !== pack.id);
    save(); renderPacks(); toast('Pack removed');
  }
});
$('#importFile').addEventListener('change', e => {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => {
    try {
      const m = JSON.parse(reader.result);
      if (m.schema !== 'meridian.agentpack/1' || !m.workflow || !Array.isArray(m.workflow.steps)) throw new Error('bad schema');
      state.packs.unshift({ id: uid('p'), installedAt: Date.now(), runs: 0, manifest: m });
      save(); renderPacks(); toast(`“${m.meta?.name || 'Pack'}” imported`);
    } catch (err) {
      toast('Not a valid agent pack (need schema meridian.agentpack/1)');
    }
  };
  reader.readAsText(file);
  e.target.value = '';
});

/* ---------- boot ---------- */
(function boot() {
  renderBuilder(); renderPacks();
})();
