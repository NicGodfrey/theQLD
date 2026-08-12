/* CANVAS STUDIO by MERIDIAN — connected creative canvas (local-first). */
'use strict';

const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const LS_KEY = 'meridian.canvas.v1';
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

/* ---------- node type registry ---------- */
const NW = 212, NH = 118;
const TYPES = {
  prompt: { label: 'Image Prompt', color: '#C8F542', fields: [
    ['subject', 'text', 'Subject'], ['scene', 'text', 'Scene / light'], ['negative', 'text', 'Negative'],
  ]},
  style: { label: 'Style Ref', color: '#D9773F', fields: [
    ['style', 'text', 'Style'], ['medium', 'text', 'Medium'], ['strength', 'number', 'Strength %'],
  ]},
  copy: { label: 'Copy Block', color: '#8FD3F0', fields: [
    ['headline', 'text', 'Headline'], ['body', 'textarea', 'Body'], ['tone', 'text', 'Tone'],
  ]},
  brand: { label: 'Brand Kit', color: '#7FE0C3', fields: [
    ['brand', 'text', 'Brand name'], ['colors', 'text', 'Palette (hex, comma)'], ['voice', 'text', 'Voice'],
  ]},
};
const DEFAULT_FIELDS = {
  prompt: { subject: 'a levitating glass teapot in a concrete atrium', scene: 'morning haze, single window light', negative: 'text, watermark, extra limbs' },
  style:  { style: 'risograph print', medium: '2-colour riso, heavy grain', strength: 80 },
  copy:   { headline: 'Steep the static out.', body: 'Small-batch botanicals for loud days.', tone: 'dry, calm' },
  brand:  { brand: 'NOVA TEA', colors: '#0B1F2A, #C8F542, #F3F0E7', voice: 'dry wit, botanical calm' },
};

/* ---------- state ---------- */
function sampleBoard() {
  const n = (type, x, y, fields) => ({ id: uid('n'), type, x, y, fields: { ...DEFAULT_FIELDS[type], ...fields } });
  const brand = n('brand', 60, 60, {});
  const style = n('style', 60, 260, {});
  const copy = n('copy', 60, 460, {});
  const prompt = n('prompt', 460, 240, {});
  return {
    id: uid('bd'), name: 'First board',
    nodes: [brand, style, copy, prompt],
    links: [
      { id: uid('l'), from: brand.id, to: prompt.id },
      { id: uid('l'), from: style.id, to: prompt.id },
      { id: uid('l'), from: copy.id, to: prompt.id },
    ],
    view: { x: 40, y: 20, s: 1 },
  };
}
let state = { boards: [sampleBoard()], currentId: null };
try {
  const raw = JSON.parse(localStorage.getItem(LS_KEY));
  if (raw && Array.isArray(raw.boards) && raw.boards.length) state = raw;
} catch (e) { /* fresh */ }
if (!state.currentId || !state.boards.find(b => b.id === state.currentId)) state.currentId = state.boards[0].id;
const save = () => localStorage.setItem(LS_KEY, JSON.stringify(state));
const board = () => state.boards.find(b => b.id === state.currentId);

/* ---------- selection & interaction state ---------- */
let sel = { kind: null, id: null };            // kind: 'node' | 'link'
let drag = null;                               // {mode:'pan'|'node'|'connect', ...}
let connectPos = null;                         // world coords of temp link end
const stage = $('#stage');

const world = (sx, sy) => {
  const r = stage.getBoundingClientRect();
  const v = board().view;
  return { x: (sx - r.left - v.x) / v.s, y: (sy - r.top - v.y) / v.s };
};

/* ---------- canvas rendering ---------- */
function nodeSummary(n) {
  const vals = Object.values(n.fields).map(v => String(v)).filter(Boolean);
  return [vals[0] || '', vals.slice(1).join(' · ')];
}
function linkPath(a, b) {
  const x1 = a.x + NW, y1 = a.y + NH / 2, x2 = b.x, y2 = b.y + NH / 2;
  const dx = Math.max(46, Math.abs(x2 - x1) / 2);
  return `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`;
}
function renderCanvas() {
  const bd = board();
  const v = bd.view;
  let s = `<defs>
    <pattern id="dots" width="26" height="26" patternUnits="userSpaceOnUse">
      <circle cx="1.5" cy="1.5" r="1.2" fill="rgba(243,240,231,.10)"/>
    </pattern>
    <filter id="nshadow" x="-40%" y="-40%" width="180%" height="180%">
      <feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="#000" flood-opacity="0.45"/>
    </filter>
  </defs>`;
  s += `<g transform="translate(${v.x} ${v.y}) scale(${v.s})">`;
  s += `<rect x="-6000" y="-6000" width="12000" height="12000" fill="url(#dots)" data-bg="1"/>`;

  // links
  bd.links.forEach(l => {
    const a = bd.nodes.find(n => n.id === l.from), b = bd.nodes.find(n => n.id === l.to);
    if (!a || !b) return;
    const on = sel.kind === 'link' && sel.id === l.id;
    const col = on ? '#C8F542' : 'rgba(243,240,231,.4)';
    s += `<path d="${linkPath(a, b)}" fill="none" stroke="transparent" stroke-width="14" data-link="${l.id}" style="cursor:pointer"/>`;
    s += `<path d="${linkPath(a, b)}" fill="none" stroke="${col}" stroke-width="${on ? 2.6 : 1.8}" pointer-events="none" ${on ? '' : 'stroke-dasharray="0"'} />`;
    const mx = (a.x + NW + b.x) / 2, my = (a.y + b.y + NH) / 2;
    s += `<circle cx="${mx}" cy="${my}" r="3" fill="${col}" pointer-events="none"/>`;
  });

  // temp connect line
  if (drag && drag.mode === 'connect' && connectPos) {
    const a = bd.nodes.find(n => n.id === drag.fromId);
    if (a) {
      const x1 = a.x + NW, y1 = a.y + NH / 2;
      s += `<path d="M ${x1} ${y1} C ${x1 + 50} ${y1}, ${connectPos.x - 50} ${connectPos.y}, ${connectPos.x} ${connectPos.y}" fill="none" stroke="#C8F542" stroke-width="2" stroke-dasharray="6 5" pointer-events="none"/>`;
    }
  }

  // nodes
  bd.nodes.forEach(n => {
    const T = TYPES[n.type];
    const on = sel.kind === 'node' && sel.id === n.id;
    const [l1, l2] = nodeSummary(n);
    s += `<g data-node="${n.id}" transform="translate(${n.x} ${n.y})" style="cursor:move">
      <rect width="${NW}" height="${NH}" rx="14" fill="#102B39" stroke="${on ? '#C8F542' : 'rgba(243,240,231,.2)'}" stroke-width="${on ? 2 : 1}" filter="url(#nshadow)"/>
      <rect width="${NW}" height="30" rx="14" fill="${T.color}" opacity=".16"/>
      <rect x="0" y="26" width="${NW}" height="4" fill="${T.color}" opacity=".55"/>
      <circle cx="14" cy="15" r="4.5" fill="${T.color}"/>
      <text x="27" y="19" font-family="IBM Plex Mono,monospace" font-size="10" letter-spacing="1.4" fill="rgba(243,240,231,.85)">${esc(T.label.toUpperCase())}</text>
      <text x="14" y="56" font-family="IBM Plex Sans,sans-serif" font-weight="600" font-size="13" fill="#F3F0E7">${esc(l1.slice(0, 26))}${l1.length > 26 ? '…' : ''}</text>
      <text x="14" y="76" font-family="IBM Plex Sans,sans-serif" font-size="11" fill="rgba(243,240,231,.5)">${esc(l2.slice(0, 32))}${l2.length > 32 ? '…' : ''}</text>
      <text x="14" y="${NH - 12}" font-family="IBM Plex Mono,monospace" font-size="9" fill="rgba(243,240,231,.3)">${esc(n.id)}</text>
      <circle cx="0" cy="${NH / 2}" r="6" fill="#0B1F2A" stroke="${T.color}" stroke-width="2"/>
      <g data-port-out="${n.id}" style="cursor:crosshair">
        <circle cx="${NW}" cy="${NH / 2}" r="13" fill="transparent"/>
        <circle cx="${NW}" cy="${NH / 2}" r="6.5" fill="${T.color}" stroke="#0B1F2A" stroke-width="2"/>
      </g>
    </g>`;
  });
  s += '</g>';
  stage.innerHTML = s;
  $('#zoomBadge').textContent = Math.round(v.s * 100) + '%';
  $('#statNodes').textContent = bd.nodes.length + ' nodes';
  $('#statLinks').textContent = bd.links.length + ' links';
}
let rafPending = false;
function renderCanvasSoon() {
  if (rafPending) return;
  rafPending = true;
  requestAnimationFrame(() => { rafPending = false; renderCanvas(); });
}

/* ---------- inspector ---------- */
function renderInspector() {
  const el = $('#inspector');
  if (sel.kind === 'link') {
    const l = board().links.find(x => x.id === sel.id);
    if (!l) { el.className = 'insp-empty'; el.textContent = 'Select a node to edit its fields.'; return; }
    const a = board().nodes.find(n => n.id === l.from), b = board().nodes.find(n => n.id === l.to);
    el.className = '';
    el.innerHTML = `<div class="insp-type" style="border-color:rgba(200,245,66,.5);color:var(--acid)">connection</div>
      <p style="font-size:13px;color:var(--dim)">${esc(a ? TYPES[a.type].label : '?')} <b style="color:var(--acid)">→</b> ${esc(b ? TYPES[b.type].label : '?')}</p>
      <button class="btn btn-danger btn-sm" id="inspDelLink" style="margin-top:8px">Remove connection</button>`;
    $('#inspDelLink').addEventListener('click', deleteSelected);
    return;
  }
  if (sel.kind !== 'node') { el.className = 'insp-empty'; el.innerHTML = 'Select a node to edit its fields.<br><br><b style="color:var(--foam)">Flow idea:</b> Brand Kit + Style Ref feed an Image Prompt; Copy Blocks ride along.'; return; }
  const n = board().nodes.find(x => x.id === sel.id);
  if (!n) { el.className = 'insp-empty'; el.textContent = 'Select a node to edit its fields.'; return; }
  const T = TYPES[n.type];
  el.className = '';
  el.innerHTML = `<div class="insp-type" style="border-color:${T.color};color:${T.color}">● ${esc(T.label)}</div>` +
    T.fields.map(([key, kind, label]) => {
      const val = esc(n.fields[key] ?? '');
      if (kind === 'textarea') return `<div class="field"><label>${esc(label)}</label><textarea data-fk="${key}" rows="3">${val}</textarea></div>`;
      return `<div class="field"><label>${esc(label)}</label><input type="${kind}" data-fk="${key}" value="${val}"></div>`;
    }).join('') +
    `<button class="btn btn-danger btn-sm" id="inspDelNode">Delete node</button>`;
  $$('#inspector [data-fk]').forEach(inp => inp.addEventListener('input', () => {
    n.fields[inp.dataset.fk] = inp.type === 'number' ? (parseFloat(inp.value) || 0) : inp.value;
    save(); renderCanvasSoon(); renderPackPreview();
  }));
  $('#inspDelNode').addEventListener('click', deleteSelected);
}

/* ---------- prompt pack ---------- */
function compilePack() {
  const bd = board();
  const incoming = id => bd.links.filter(l => l.to === id).map(l => bd.nodes.find(n => n.id === l.from)).filter(Boolean);
  const prompts = bd.nodes.filter(n => n.type === 'prompt').map(p => {
    const feeds = incoming(p.id);
    const parts = [];
    if (p.fields.subject) parts.push(p.fields.subject);
    if (p.fields.scene) parts.push(p.fields.scene);
    feeds.filter(f => f.type === 'style').forEach(f => {
      parts.push(`in the style of ${f.fields.style}${f.fields.medium ? ', ' + f.fields.medium : ''}${f.fields.strength ? ` (style strength ${f.fields.strength}%)` : ''}`);
    });
    feeds.filter(f => f.type === 'brand').forEach(f => {
      if (f.fields.colors) parts.push(`brand palette: ${f.fields.colors}`);
      if (f.fields.voice) parts.push(`mood: ${f.fields.voice}`);
    });
    const copyFeeds = feeds.filter(f => f.type === 'copy');
    copyFeeds.forEach(f => { if (f.fields.headline) parts.push(`space for overlay copy: “${f.fields.headline}”`); });
    return {
      id: p.id,
      title: (p.fields.subject || 'untitled prompt').slice(0, 60),
      prompt: parts.join(', '),
      negative: p.fields.negative || '',
      copy: copyFeeds.map(f => ({ headline: f.fields.headline, body: f.fields.body, tone: f.fields.tone })),
      inputs: feeds.map(f => ({ id: f.id, type: f.type })),
    };
  });
  return {
    schema: 'meridian.promptpack/1',
    tool: 'CANVAS STUDIO by MERIDIAN',
    board: { id: bd.id, name: bd.name },
    generatedAt: new Date().toISOString(),
    nodes: bd.nodes, links: bd.links, prompts,
  };
}
function renderPackPreview() {
  const pack = compilePack();
  if (!pack.prompts.length) {
    $('#packPreview').textContent = 'No Image Prompt nodes yet — add one and wire Style / Brand / Copy nodes into it. The compiled pack shows up here.';
    return;
  }
  $('#packPreview').textContent = pack.prompts.map((p, i) =>
    `── prompt ${i + 1} ─ ${p.title}\n${p.prompt}\n${p.negative ? 'negative: ' + p.negative + '\n' : ''}${p.copy.length ? p.copy.map(c => `copy: “${c.headline}” — ${c.body || ''} [${c.tone || 'neutral'}]`).join('\n') + '\n' : ''}`
  ).join('\n');
}

/* ---------- boards ---------- */
function renderBoards() {
  $('#boardSel').innerHTML = state.boards.map(b => `<option value="${b.id}" ${b.id === state.currentId ? 'selected' : ''}>${esc(b.name)}</option>`).join('');
}
function switchBoard(id) {
  state.currentId = id;
  sel = { kind: null, id: null };
  save(); renderBoards(); renderCanvas(); renderInspector(); renderPackPreview();
}

/* ---------- delete ---------- */
function deleteSelected() {
  const bd = board();
  if (sel.kind === 'node') {
    bd.nodes = bd.nodes.filter(n => n.id !== sel.id);
    bd.links = bd.links.filter(l => l.from !== sel.id && l.to !== sel.id);
  } else if (sel.kind === 'link') {
    bd.links = bd.links.filter(l => l.id !== sel.id);
  } else return;
  sel = { kind: null, id: null };
  save(); renderCanvas(); renderInspector(); renderPackPreview();
}

/* ---------- pointer interactions ---------- */
stage.addEventListener('pointerdown', e => {
  e.preventDefault();
  const port = e.target.closest('[data-port-out]');
  const nodeEl = e.target.closest('[data-node]');
  const linkEl = e.target.closest('[data-link]');
  const w = world(e.clientX, e.clientY);
  if (port) {
    drag = { mode: 'connect', fromId: port.dataset.portOut, moved: false };
    connectPos = w;
  } else if (nodeEl) {
    const n = board().nodes.find(x => x.id === nodeEl.dataset.node);
    drag = { mode: 'node', id: n.id, ox: w.x - n.x, oy: w.y - n.y, moved: false, sx: e.clientX, sy: e.clientY };
  } else if (linkEl) {
    sel = { kind: 'link', id: linkEl.dataset.link };
    drag = { mode: 'none', moved: false };
    renderCanvas(); renderInspector();
  } else {
    const v = board().view;
    drag = { mode: 'pan', sx: e.clientX, sy: e.clientY, vx: v.x, vy: v.y, moved: false };
    stage.classList.add('dragging');
  }
});
window.addEventListener('pointermove', e => {
  if (!drag) return;
  const dx = e.clientX - (drag.sx ?? e.clientX), dy = e.clientY - (drag.sy ?? e.clientY);
  if (Math.abs(dx) + Math.abs(dy) > 4) drag.moved = true;
  if (drag.mode === 'pan') {
    const v = board().view;
    v.x = drag.vx + dx; v.y = drag.vy + dy;
    renderCanvasSoon();
  } else if (drag.mode === 'node') {
    const n = board().nodes.find(x => x.id === drag.id);
    if (!n) return;
    const w = world(e.clientX, e.clientY);
    n.x = Math.round(w.x - drag.ox); n.y = Math.round(w.y - drag.oy);
    drag.moved = true;
    renderCanvasSoon();
  } else if (drag.mode === 'connect') {
    connectPos = world(e.clientX, e.clientY);
    drag.moved = true;
    renderCanvasSoon();
  }
});
window.addEventListener('pointerup', e => {
  if (!drag) return;
  const d = drag; drag = null;
  stage.classList.remove('dragging');
  if (d.mode === 'connect') {
    connectPos = null;
    const el = document.elementFromPoint(e.clientX, e.clientY);
    const targetEl = el && el.closest ? el.closest('[data-node]') : null;
    if (targetEl && targetEl.dataset.node !== d.fromId) {
      const bd = board();
      const exists = bd.links.some(l => l.from === d.fromId && l.to === targetEl.dataset.node);
      if (exists) toast('Already connected');
      else {
        bd.links.push({ id: uid('l'), from: d.fromId, to: targetEl.dataset.node });
        save(); toast('Connected');
      }
    }
    renderCanvas(); renderPackPreview();
    return;
  }
  if (d.mode === 'node') {
    if (!d.moved) {
      sel = { kind: 'node', id: d.id };
      renderInspector();
    }
    save(); renderCanvas();
    return;
  }
  if (d.mode === 'pan') {
    if (!d.moved) {
      sel = { kind: null, id: null };
      renderInspector(); renderCanvas();
    } else save();
  }
});
stage.addEventListener('wheel', e => {
  e.preventDefault();
  const v = board().view;
  const r = stage.getBoundingClientRect();
  const sx = e.clientX - r.left, sy = e.clientY - r.top;
  const wx = (sx - v.x) / v.s, wy = (sy - v.y) / v.s;
  const factor = e.deltaY < 0 ? 1.1 : 1 / 1.1;
  v.s = Math.min(2.5, Math.max(0.3, v.s * factor));
  v.x = sx - wx * v.s; v.y = sy - wy * v.s;
  save(); renderCanvasSoon();
}, { passive: false });

window.addEventListener('keydown', e => {
  if ((e.key === 'Delete' || e.key === 'Backspace') && !/input|textarea|select/i.test(document.activeElement.tagName)) {
    if (sel.kind) { e.preventDefault(); deleteSelected(); }
  }
  if (e.key === 'Escape' && drag && drag.mode === 'connect') { drag = null; connectPos = null; renderCanvas(); }
});

/* ---------- toolbar ---------- */
$$('.add-btn').forEach(btn => btn.addEventListener('click', () => {
  const type = btn.dataset.add;
  const v = board().view;
  const r = stage.getBoundingClientRect();
  const cx = ((r.width / 2 - v.x) / v.s) - NW / 2 + (Math.random() * 60 - 30);
  const cy = ((r.height / 2 - v.y) / v.s) - NH / 2 + (Math.random() * 60 - 30);
  const n = { id: uid('n'), type, x: Math.round(cx), y: Math.round(cy), fields: { ...DEFAULT_FIELDS[type] } };
  board().nodes.push(n);
  sel = { kind: 'node', id: n.id };
  save(); renderCanvas(); renderInspector(); renderPackPreview();
}));
function zoomBy(f) {
  const v = board().view;
  const r = stage.getBoundingClientRect();
  const sx = r.width / 2, sy = r.height / 2;
  const wx = (sx - v.x) / v.s, wy = (sy - v.y) / v.s;
  v.s = Math.min(2.5, Math.max(0.3, v.s * f));
  v.x = sx - wx * v.s; v.y = sy - wy * v.s;
  save(); renderCanvas();
}
$('#btnZoomIn').addEventListener('click', () => zoomBy(1.2));
$('#btnZoomOut').addEventListener('click', () => zoomBy(1 / 1.2));
$('#btnZoomFit').addEventListener('click', () => {
  const bd = board();
  if (!bd.nodes.length) return;
  const xs = bd.nodes.map(n => n.x), ys = bd.nodes.map(n => n.y);
  const minX = Math.min(...xs) - 40, minY = Math.min(...ys) - 40;
  const maxX = Math.max(...xs) + NW + 40, maxY = Math.max(...ys) + NH + 40;
  const r = stage.getBoundingClientRect();
  const s = Math.min(2, Math.min(r.width / (maxX - minX), r.height / (maxY - minY)));
  bd.view = { s, x: (r.width - (maxX - minX) * s) / 2 - minX * s, y: (r.height - (maxY - minY) * s) / 2 - minY * s };
  save(); renderCanvas();
});
$('#btnDelSel').addEventListener('click', () => sel.kind ? deleteSelected() : toast('Nothing selected'));
$('#btnExportPack').addEventListener('click', () => {
  const pack = compilePack();
  download(`prompt-pack-${board().name.replace(/[^a-z0-9]+/gi, '-').toLowerCase()}.json`, JSON.stringify(pack, null, 2));
  toast(`Prompt pack exported — ${pack.prompts.length} prompt(s)`);
});

/* boards */
$('#boardSel').addEventListener('change', e => switchBoard(e.target.value));
$('#btnNewBoard').addEventListener('click', () => {
  const name = prompt('Board name?', 'Board ' + (state.boards.length + 1));
  if (name === null) return;
  const bd = { id: uid('bd'), name: name || 'Untitled', nodes: [], links: [], view: { x: 60, y: 40, s: 1 } };
  state.boards.push(bd);
  switchBoard(bd.id);
  toast('Board created');
});
$('#btnRenameBoard').addEventListener('click', () => {
  const name = prompt('Rename board:', board().name);
  if (name === null || !name.trim()) return;
  board().name = name.trim();
  save(); renderBoards();
});
$('#btnDelBoard').addEventListener('click', () => {
  if (state.boards.length === 1) return toast('Keep at least one board');
  if (!confirm(`Delete board “${board().name}”?`)) return;
  state.boards = state.boards.filter(b => b.id !== state.currentId);
  switchBoard(state.boards[0].id);
  toast('Board deleted');
});

/* ---------- boot ---------- */
(function boot() {
  renderBoards(); renderCanvas(); renderInspector(); renderPackPreview();
})();
