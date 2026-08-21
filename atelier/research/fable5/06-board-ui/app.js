/* ============================================================
   Atelier Board UI — vanilla JS, no build step.

   Talks to the Helix REST API at relative /api (see UI_SPEC.md
   for the assumed contract). When /api is unreachable — e.g.
   when this folder is served by `python3 -m http.server` — the
   app transparently falls back to a localStorage-backed demo
   backend with simulated token streaming, so every interaction
   remains testable.
   ============================================================ */
(() => {
"use strict";

/* ---------------------------------------------------------- *
 * Utilities
 * ---------------------------------------------------------- */

const $  = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

const uid = () =>
  (crypto.randomUUID ? crypto.randomUUID() : "id-" + Math.random().toString(36).slice(2) + Date.now().toString(36));

const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
const now = () => Date.now();

function debounce(fn, ms) {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
}

function toast(text, kind = "") {
  const el = document.createElement("div");
  el.className = `toast ${kind}`;
  el.textContent = text;
  $("#toasts").appendChild(el);
  setTimeout(() => el.classList.add("hide"), 3200);
  setTimeout(() => el.remove(), 3600);
}

function isTypingTarget(t) {
  return t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.tagName === "SELECT" || t.isContentEditable);
}

/** SVG data-URI placeholder art for seeded image nodes (no network needed). */
function svgPlaceholder(label, c1 = "#2a2f3d", c2 = "#454b61", fg = "#c8cede") {
  const svg =
    `<svg xmlns='http://www.w3.org/2000/svg' width='640' height='420'>` +
    `<defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'>` +
    `<stop offset='0' stop-color='${c1}'/><stop offset='1' stop-color='${c2}'/></linearGradient></defs>` +
    `<rect width='640' height='420' fill='url(#g)'/>` +
    `<circle cx='500' cy='90' r='140' fill='rgba(255,255,255,0.05)'/>` +
    `<circle cx='120' cy='360' r='180' fill='rgba(0,0,0,0.12)'/>` +
    `<text x='32' y='380' font-family='monospace' font-size='22' fill='${fg}' opacity='0.85'>${label}</text>` +
    `</svg>`;
  return "data:image/svg+xml;utf8," + encodeURIComponent(svg);
}

/* ---------------------------------------------------------- *
 * Constants & fallback catalog
 * ---------------------------------------------------------- */

const API = "/api";

const FALLBACK_PROVIDERS = [
  { id: "openai",    name: "OpenAI",    models: ["gpt-5.2", "gpt-5.2-mini", "o4"] },
  { id: "anthropic", name: "Anthropic", models: ["claude-opus-4.5", "claude-sonnet-4.5", "claude-haiku-4"] },
  { id: "google",    name: "Google",    models: ["gemini-3-pro", "gemini-3-flash"] },
  { id: "fal",       name: "fal.ai",    models: ["flux-1.1-pro", "seedream-4.5"] },
];

const KEY_PROVIDERS = [
  { id: "openai",    label: "OpenAI",    placeholder: "sk-…" },
  { id: "anthropic", label: "Anthropic", placeholder: "sk-ant-…" },
  { id: "google",    label: "Google AI", placeholder: "AIza…" },
  { id: "fal",       label: "fal.ai",    placeholder: "key-id:key-secret" },
  { id: "replicate", label: "Replicate", placeholder: "r8_…" },
];

const DEFAULT_BRAND_KIT = () => ({
  colors: [
    { name: "Ink",    value: "#101218" },
    { name: "Brass",  value: "#e0a94e" },
    { name: "Cloud",  value: "#e9ebf1" },
  ],
  fonts: { heading: "", body: "" },
  logo_url: "",
  voice: "",
});

const NODE_DEFAULTS = {
  note:  { w: 260, h: 180 },
  image: { w: 320, h: 230 },
  video: { w: 360, h: 220 },
};

/* ---------------------------------------------------------- *
 * App state
 * ---------------------------------------------------------- */

const state = {
  backend: null,          // RemoteBackend | LocalBackend
  live: false,            // true when talking to real /api
  projects: [],
  projectId: null,
  threads: [],
  threadId: null,
  messages: [],
  nodes: [],              // canvas nodes for current project
  providers: FALLBACK_PROVIDERS,
  provider: "anthropic",
  model: "claude-sonnet-4.5",
  mode: "fast",           // 'fast' | 'thinking'
  brandKit: DEFAULT_BRAND_KIT(),
  camera: { x: 0, y: 0, scale: 1 },
  selectedNodeId: null,
  maxZ: 1,
  streaming: false,
};

const prefs = {
  load() { try { return JSON.parse(localStorage.getItem("atelier.prefs") || "{}"); } catch { return {}; } },
  save(patch) {
    const p = { ...prefs.load(), ...patch };
    localStorage.setItem("atelier.prefs", JSON.stringify(p));
  },
};

/* ---------------------------------------------------------- *
 * Remote backend — Helix REST at /api
 * ---------------------------------------------------------- */

async function apiFetch(path, opts = {}) {
  const res = await fetch(API + path, {
    headers: { "Content-Type": "application/json", ...(opts.headers || {}) },
    ...opts,
  });
  if (!res.ok) throw new Error(`${opts.method || "GET"} ${path} → ${res.status}`);
  if (res.status === 204) return null;
  return res.json();
}

const asList = (d) => (Array.isArray(d) ? d : d && Array.isArray(d.items) ? d.items : []);

const RemoteBackend = {
  kind: "remote",

  listProjects:  () => apiFetch("/projects").then(asList),
  createProject: (name) => apiFetch("/projects", { method: "POST", body: JSON.stringify({ name }) }),

  listThreads:  (pid) => apiFetch(`/projects/${pid}/threads`).then(asList),
  createThread: (pid, title) =>
    apiFetch(`/projects/${pid}/threads`, { method: "POST", body: JSON.stringify({ title }) }),

  listMessages: (tid) => apiFetch(`/threads/${tid}/messages`).then(asList),

  listNodes:  (pid) => apiFetch(`/projects/${pid}/nodes`).then(asList),
  createNode: (pid, node) =>
    apiFetch(`/projects/${pid}/nodes`, { method: "POST", body: JSON.stringify(node) }),
  updateNode: (id, patch) =>
    apiFetch(`/nodes/${id}`, { method: "PATCH", body: JSON.stringify(patch) }),
  deleteNode: (id) => apiFetch(`/nodes/${id}`, { method: "DELETE" }),

  listProviders: () => apiFetch("/providers").then(asList),

  getKeys:  () => apiFetch("/keys"),
  saveKeys: (map) => apiFetch("/keys", { method: "PUT", body: JSON.stringify(map) }),

  getBrandKit:  (pid) => apiFetch(`/projects/${pid}/brand-kit`),
  saveBrandKit: (pid, kit) =>
    apiFetch(`/projects/${pid}/brand-kit`, { method: "PUT", body: JSON.stringify(kit) }),

  async upload(file) {
    const fd = new FormData();
    fd.append("file", file);
    const res = await fetch(API + "/uploads", { method: "POST", body: fd });
    if (!res.ok) throw new Error(`POST /uploads → ${res.status}`);
    return res.json(); // { id, url, kind }
  },

  /**
   * POST /api/chat — Server-Sent Events stream.
   * Events: thinking.delta {delta}, message.delta {delta},
   *         done {message}, error {message}.
   * The server persists both the user turn and the assistant turn.
   */
  async sendChat(payload, handlers) {
    const res = await fetch(API + "/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
      body: JSON.stringify(payload),
    });
    if (!res.ok || !res.body) throw new Error(`POST /chat → ${res.status}`);

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buf = "";

    const dispatch = (event, dataRaw) => {
      let data = {};
      if (dataRaw && dataRaw !== "[DONE]") { try { data = JSON.parse(dataRaw); } catch { data = { delta: dataRaw }; } }
      if (dataRaw === "[DONE]" || event === "done") handlers.onDone?.(data.message || null);
      else if (event === "thinking.delta") handlers.onThinking?.(data.delta ?? "");
      else if (event === "error") handlers.onError?.(new Error(data.message || "stream error"));
      else handlers.onToken?.(data.delta ?? "");
    };

    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
      let idx;
      while ((idx = buf.indexOf("\n\n")) >= 0) {
        const frame = buf.slice(0, idx);
        buf = buf.slice(idx + 2);
        let event = "message.delta";
        const dataLines = [];
        for (const line of frame.split("\n")) {
          if (line.startsWith("event:")) event = line.slice(6).trim();
          else if (line.startsWith("data:")) dataLines.push(line.slice(5).trimStart());
        }
        if (dataLines.length) dispatch(event, dataLines.join("\n"));
      }
    }
    handlers.onDone?.(null); // idempotent close if server ended without a done frame
  },
};

/* ---------------------------------------------------------- *
 * Local backend — demo mode backed by localStorage
 * ---------------------------------------------------------- */

const LS_KEY = "atelier.local.v1";

function localDB() {
  try { const d = JSON.parse(localStorage.getItem(LS_KEY)); if (d) return d; } catch {}
  return seedDB();
}
function saveDB(db) {
  try { localStorage.setItem(LS_KEY, JSON.stringify(db)); }
  catch { /* quota exceeded (large data URLs) — session-only from here */ }
}

function seedDB() {
  const pid = uid(), tid = uid();
  const db = {
    projects: [{ id: pid, name: "Neon Botanica — Campaign", created_at: now() }],
    threads: { [pid]: [{ id: tid, project_id: pid, title: "Art direction", created_at: now() }] },
    messages: {
      [tid]: [
        { id: uid(), thread_id: tid, role: "user", content: "Give me a direction for the hero visual. Organic but electric.", mode: "fast", provider: "anthropic", model: "claude-sonnet-4.5", created_at: now() - 60000 },
        { id: uid(), thread_id: tid, role: "assistant", content: "Direction: macro botanical forms lit like signage. Deep charcoal field, a single brass-toned specimen, hairline electric-cyan rim light. Keep 60% negative space for the headline. I placed a reference frame and a palette note on the board.", mode: "fast", provider: "anthropic", model: "claude-sonnet-4.5", created_at: now() - 55000 },
      ],
    },
    nodes: {
      [pid]: [
        { id: uid(), project_id: pid, type: "note", x: -520, y: -180, w: 300, h: 210, z: 1,
          data: { text: "BRIEF — Neon Botanica\nSpring campaign, 3 hero images + 1 teaser video.\nAudience: design-literate 25–40.\nMood: organic forms, electric accents, quiet luxury." } },
        { id: uid(), project_id: pid, type: "image", x: -150, y: -230, w: 340, h: 250, z: 2,
          data: { src: svgPlaceholder("hero_ref_01", "#1d2b26", "#37584a", "#bfe3cf"), title: "hero_ref_01 — moss + brass" } },
        { id: uid(), project_id: pid, type: "image", x: 240, y: -140, w: 300, h: 220, z: 3,
          data: { src: svgPlaceholder("hero_ref_02", "#2b1d2a", "#584a37", "#e3d3bf"), title: "hero_ref_02 — petal macro" } },
        { id: uid(), project_id: pid, type: "note", x: -140, y: 90, w: 260, h: 150, z: 4,
          data: { text: "Palette lock\nInk #101218 · Brass #E0A94E · Cloud #E9EBF1\nAccent use ≤ 10% of frame." } },
        { id: uid(), project_id: pid, type: "video", x: 190, y: 140, w: 360, h: 210, z: 5,
          data: { title: "teaser_16x9.mp4", sub: "Video placeholder — render pending" } },
      ],
    },
    brand: { [pid]: {
      colors: [
        { name: "Ink", value: "#101218" },
        { name: "Brass", value: "#e0a94e" },
        { name: "Cloud", value: "#e9ebf1" },
        { name: "Fern", value: "#4e8a68" },
      ],
      fonts: { heading: "Fraunces", body: "Inter" },
      logo_url: "",
      voice: "Confident, warm, editorial. Short sentences. No exclamation marks.",
    } },
    keys: {},
  };
  saveDB(db);
  return db;
}

const DEMO_REPLIES = [
  "Here's a take. Anchor the composition on a single oversized botanical form, offset to the right third. Keep the left half as negative space in Ink (#101218) so the headline breathes. Brass (#E0A94E) appears only as rim light — under 10% of the frame, per the palette lock.\n\nIf you want, I can draft three headline options that match the brand voice next.",
  "Three headline options, matched to the voice notes (confident, warm, no exclamation marks):\n\n1. Grown in the dark. Built to glow.\n2. Nature, rewired.\n3. The quiet kind of electric.\n\nOption 3 fits the negative-space layout best — short enough to set large in the heading font.",
  "For the teaser video, I'd storyboard four beats: (1) black frame, a hum; (2) macro stem, rim light traces upward; (3) full specimen revealed in brass tones; (4) logo lockup on Ink. Total runtime around 12 seconds. I left a placeholder frame on the board — replace it once the render lands.",
  "Noted. I've logged that decision in the project ledger so future generations stay consistent with it. Anything else on this thread, or should we branch a new one for the print adaptation?",
];

const DEMO_THINKING =
  "Reading project ledger: palette lock (Ink/Brass/Cloud), voice = editorial, no exclamation marks. " +
  "Checking board context: 2 reference frames, 1 palette note, 1 pending video slot. " +
  "Constraints satisfied → composing response with concrete, board-aware suggestions.";

let demoReplyIx = 0;

const LocalBackend = {
  kind: "local",

  async listProjects() { return localDB().projects; },
  async createProject(name) {
    const db = localDB();
    const p = { id: uid(), name, created_at: now() };
    db.projects.push(p);
    db.threads[p.id] = [];
    db.nodes[p.id] = [];
    db.brand[p.id] = DEFAULT_BRAND_KIT();
    saveDB(db);
    return p;
  },

  async listThreads(pid) { return localDB().threads[pid] || []; },
  async createThread(pid, title) {
    const db = localDB();
    const t = { id: uid(), project_id: pid, title, created_at: now() };
    (db.threads[pid] = db.threads[pid] || []).push(t);
    db.messages[t.id] = [];
    saveDB(db);
    return t;
  },

  async listMessages(tid) { return localDB().messages[tid] || []; },

  async listNodes(pid) { return localDB().nodes[pid] || []; },
  async createNode(pid, node) {
    const db = localDB();
    (db.nodes[pid] = db.nodes[pid] || []).push(node);
    saveDB(db);
    return node;
  },
  async updateNode(id, patch) {
    const db = localDB();
    for (const list of Object.values(db.nodes)) {
      const n = list.find((n) => n.id === id);
      if (n) { Object.assign(n, patch, { data: { ...n.data, ...(patch.data || {}) } }); break; }
    }
    saveDB(db);
  },
  async deleteNode(id) {
    const db = localDB();
    for (const pid of Object.keys(db.nodes)) db.nodes[pid] = db.nodes[pid].filter((n) => n.id !== id);
    saveDB(db);
  },

  async listProviders() { return FALLBACK_PROVIDERS; },

  async getKeys() {
    const keys = localDB().keys;
    const out = {};
    for (const [k, v] of Object.entries(keys)) out[k] = { set: true, hint: "…" + String(v).slice(-4) };
    return out;
  },
  async saveKeys(map) {
    const db = localDB();
    for (const [k, v] of Object.entries(map)) if (v) db.keys[k] = btoa(v); // demo only — see UI_SPEC.md
    saveDB(db);
    return this.getKeys();
  },

  async getBrandKit(pid) { return localDB().brand[pid] || DEFAULT_BRAND_KIT(); },
  async saveBrandKit(pid, kit) {
    const db = localDB();
    db.brand[pid] = kit;
    saveDB(db);
    return kit;
  },

  async upload(file) {
    // Small files persist as data URLs; large ones live for the session only.
    if (file.size <= 1.5 * 1024 * 1024) {
      const url = await new Promise((ok, no) => {
        const r = new FileReader();
        r.onload = () => ok(r.result);
        r.onerror = no;
        r.readAsDataURL(file);
      });
      return { id: uid(), url, kind: file.type };
    }
    return { id: uid(), url: URL.createObjectURL(file), kind: file.type, ephemeral: true };
  },

  async sendChat(payload, handlers) {
    // Persist the user turn.
    const db = localDB();
    const userMsg = {
      id: uid(), thread_id: payload.thread_id, role: "user", content: payload.message,
      mode: payload.mode, provider: payload.provider, model: payload.model, created_at: now(),
    };
    (db.messages[payload.thread_id] = db.messages[payload.thread_id] || []).push(userMsg);
    saveDB(db);

    const reply = DEMO_REPLIES[demoReplyIx++ % DEMO_REPLIES.length];
    const think = payload.mode === "thinking" ? DEMO_THINKING : "";

    const streamText = (text, cb, delay) =>
      new Promise((resolve) => {
        const parts = text.split(/(\s+)/).filter(Boolean);
        let i = 0;
        const tick = () => {
          if (i >= parts.length) return resolve();
          cb(parts[i++]);
          setTimeout(tick, delay);
        };
        setTimeout(tick, delay);
      });

    if (think) await streamText(think, (t) => handlers.onThinking?.(t), 14);
    await streamText(reply, (t) => handlers.onToken?.(t), 22);

    const asstMsg = {
      id: uid(), thread_id: payload.thread_id, role: "assistant", content: reply,
      thinking: think, mode: payload.mode, provider: payload.provider, model: payload.model, created_at: now(),
    };
    const db2 = localDB();
    (db2.messages[payload.thread_id] = db2.messages[payload.thread_id] || []).push(asstMsg);
    saveDB(db2);
    handlers.onDone?.(asstMsg);
  },
};

/* ---------------------------------------------------------- *
 * Backend detection
 * ---------------------------------------------------------- */

async function detectBackend() {
  try {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 1500);
    const res = await fetch(API + "/health", { signal: ctrl.signal });
    clearTimeout(timer);
    if (res.ok) return { backend: RemoteBackend, live: true };
  } catch { /* fall through to demo */ }
  return { backend: LocalBackend, live: false };
}

function renderConnState() {
  const pill = $("#connPill");
  pill.classList.toggle("live", state.live);
  pill.classList.toggle("demo", !state.live);
  $("#connLabel").textContent = state.live ? "Live /api" : "Demo mode";
  pill.title = state.live
    ? "Connected to the Helix API at /api"
    : "No /api backend found — using local demo data. Click to retry.";
  const detail = $("#connDetail");
  if (detail) detail.textContent = state.live ? "Helix REST at /api (live)" : "local demo store (no /api reachable)";
}

/* ---------------------------------------------------------- *
 * DOM handles
 * ---------------------------------------------------------- */

const viewport = $("#viewport");
const world = $("#world");
const zoomHud = $("#zoomHud");
const msgList = $("#msgList");
const chatInput = $("#chatInput");

const nodeEls = new Map(); // node.id -> element

/* ---------------------------------------------------------- *
 * Camera (pan / zoom)
 * ---------------------------------------------------------- */

function applyCamera() {
  const { x, y, scale } = state.camera;
  world.style.transform = `translate(${x}px, ${y}px) scale(${scale})`;
  viewport.style.backgroundSize = `${24 * scale}px ${24 * scale}px`;
  viewport.style.backgroundPosition = `${x}px ${y}px`;
  zoomHud.textContent = `${Math.round(scale * 100)}%`;
}

function screenToWorld(clientX, clientY) {
  const r = viewport.getBoundingClientRect();
  const { x, y, scale } = state.camera;
  return { x: (clientX - r.left - x) / scale, y: (clientY - r.top - y) / scale };
}

function zoomAt(clientX, clientY, factor) {
  const cam = state.camera;
  const newScale = clamp(cam.scale * factor, 0.2, 2.5);
  const r = viewport.getBoundingClientRect();
  const px = clientX - r.left, py = clientY - r.top;
  cam.x = px - ((px - cam.x) / cam.scale) * newScale;
  cam.y = py - ((py - cam.y) / cam.scale) * newScale;
  cam.scale = newScale;
  applyCamera();
}

function zoomCenter(factor) {
  const r = viewport.getBoundingClientRect();
  zoomAt(r.left + r.width / 2, r.top + r.height / 2, factor);
}

function resetZoom() {
  state.camera = { x: viewport.clientWidth / 2, y: viewport.clientHeight / 2, scale: 1 };
  applyCamera();
}

function fitBoard() {
  if (!state.nodes.length) { resetZoom(); return; }
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const n of state.nodes) {
    minX = Math.min(minX, n.x); minY = Math.min(minY, n.y);
    maxX = Math.max(maxX, n.x + n.w); maxY = Math.max(maxY, n.y + n.h);
  }
  const pad = 80;
  const bw = maxX - minX + pad * 2, bh = maxY - minY + pad * 2;
  const scale = clamp(Math.min(viewport.clientWidth / bw, viewport.clientHeight / bh), 0.2, 1.4);
  state.camera.scale = scale;
  state.camera.x = (viewport.clientWidth - (maxX + minX) * scale) / 2;
  state.camera.y = (viewport.clientHeight - (maxY + minY) * scale) / 2;
  applyCamera();
}

/* ---------------------------------------------------------- *
 * Canvas nodes — render
 * ---------------------------------------------------------- */

const NODE_ICONS = {
  note: `<svg viewBox="0 0 24 24" width="11" height="11"><path d="M5 4h14a1 1 0 0 1 1 1v9l-6 6H5a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1Z" fill="none" stroke="currentColor" stroke-width="2"/></svg>`,
  image: `<svg viewBox="0 0 24 24" width="11" height="11"><rect x="4" y="4" width="16" height="16" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="m5 16 4-3.5 3 2.5 3-2 4 3.5" fill="none" stroke="currentColor" stroke-width="2"/></svg>`,
  video: `<svg viewBox="0 0 24 24" width="11" height="11"><rect x="3" y="5" width="18" height="14" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="m10 9 5 3-5 3V9Z" fill="currentColor"/></svg>`,
};
const NODE_LABELS = { note: "Note", image: "Image", video: "Video" };

function buildNodeEl(node) {
  const el = document.createElement("article");
  el.className = `node type-${node.type}`;
  el.dataset.id = node.id;

  const head = document.createElement("header");
  head.className = "node-head";
  head.innerHTML =
    `<span class="node-kind">${NODE_ICONS[node.type] || ""}<span>${NODE_LABELS[node.type] || node.type}</span></span>`;
  const del = document.createElement("button");
  del.className = "node-del";
  del.dataset.nodrag = "";
  del.title = "Delete node";
  del.innerHTML = `<svg viewBox="0 0 24 24" width="12" height="12"><path d="M6 6l12 12M18 6 6 18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>`;
  del.addEventListener("click", (e) => { e.stopPropagation(); removeNode(node.id); });
  head.appendChild(del);
  el.appendChild(head);

  const body = document.createElement("div");
  body.className = "node-body";

  if (node.type === "note") {
    body.contentEditable = "true";
    body.spellcheck = false;
    body.dataset.nodrag = "";
    body.textContent = node.data?.text || "";
    body.addEventListener("input", debounce(() => {
      node.data = { ...node.data, text: body.textContent };
      persistNode(node, { data: { text: body.textContent } });
    }, 500));
    // Keep note edits from bubbling into canvas shortcuts; Escape exits editing.
    body.addEventListener("keydown", (e) => {
      e.stopPropagation();
      if (e.key === "Escape") { e.preventDefault(); body.blur(); }
    });
  } else if (node.type === "image") {
    const img = document.createElement("img");
    img.src = node.data?.src || "";
    img.alt = node.data?.title || "image";
    img.draggable = false;
    body.appendChild(img);
    if (node.data?.title) {
      const cap = document.createElement("div");
      cap.className = "node-caption";
      cap.textContent = node.data.title;
      body.appendChild(cap);
    }
  } else if (node.type === "video") {
    body.innerHTML =
      `<div class="video-play"><svg viewBox="0 0 24 24" width="18" height="18"><path d="m9 7 8 5-8 5V7Z" fill="currentColor"/></svg></div>` +
      `<div class="video-label"></div><div class="video-sub"></div>`;
    body.querySelector(".video-label").textContent = node.data?.title || "untitled.mp4";
    body.querySelector(".video-sub").textContent = node.data?.sub || "Video placeholder";
  }
  el.appendChild(body);

  const rez = document.createElement("div");
  rez.className = "node-resize";
  el.appendChild(rez);

  positionNodeEl(el, node);
  return el;
}

function positionNodeEl(el, node) {
  el.style.transform = `translate(${node.x}px, ${node.y}px)`;
  el.style.width = `${node.w}px`;
  el.style.height = `${node.h}px`;
  el.style.zIndex = node.z || 1;
}

function renderNodes() {
  world.innerHTML = "";
  nodeEls.clear();
  state.maxZ = 1;
  for (const n of state.nodes) {
    state.maxZ = Math.max(state.maxZ, n.z || 1);
    const el = buildNodeEl(n);
    nodeEls.set(n.id, el);
    world.appendChild(el);
  }
  $("#emptyHint").hidden = state.nodes.length > 0;
}

function selectNode(id) {
  if (state.selectedNodeId && nodeEls.get(state.selectedNodeId))
    nodeEls.get(state.selectedNodeId).classList.remove("selected");
  state.selectedNodeId = id;
  if (!id) return;
  const el = nodeEls.get(id);
  const node = state.nodes.find((n) => n.id === id);
  if (el && node) {
    el.classList.add("selected");
    node.z = ++state.maxZ;
    el.style.zIndex = node.z;
    persistNode(node, { z: node.z });
  }
}

const persistNode = debounce((node, patch) => {
  state.backend.updateNode(node.id, patch).catch(() => toast("Couldn't save node change", "err"));
}, 250);

async function addNode(type, data = {}, at = null) {
  const d = NODE_DEFAULTS[type];
  const center = at || screenToWorld(
    viewport.getBoundingClientRect().left + viewport.clientWidth / 2,
    viewport.getBoundingClientRect().top + viewport.clientHeight / 2
  );
  const node = {
    id: uid(),
    project_id: state.projectId,
    type,
    x: Math.round(center.x - d.w / 2),
    y: Math.round(center.y - d.h / 2),
    w: data.w || d.w,
    h: data.h || d.h,
    z: ++state.maxZ,
    data,
  };
  state.nodes.push(node);
  const el = buildNodeEl(node);
  nodeEls.set(node.id, el);
  world.appendChild(el);
  $("#emptyHint").hidden = true;
  selectNode(node.id);
  try {
    const saved = await state.backend.createNode(state.projectId, node);
    if (saved?.id && saved.id !== node.id) { // server may assign its own id
      nodeEls.delete(node.id); node.id = saved.id;
      nodeEls.set(node.id, el); el.dataset.id = node.id;
    }
  } catch { toast("Couldn't save node to server", "err"); }
  return node;
}

async function removeNode(id) {
  state.nodes = state.nodes.filter((n) => n.id !== id);
  nodeEls.get(id)?.remove();
  nodeEls.delete(id);
  if (state.selectedNodeId === id) state.selectedNodeId = null;
  $("#emptyHint").hidden = state.nodes.length > 0;
  try { await state.backend.deleteNode(id); } catch { toast("Couldn't delete node on server", "err"); }
}

/* ---------------------------------------------------------- *
 * Canvas gestures — pan, drag, resize, zoom
 * ---------------------------------------------------------- */

let gesture = null;   // { type, startX, startY, ... }
let spaceDown = false;

viewport.addEventListener("pointerdown", (e) => {
  if (e.button === 2) return;
  const nodeEl = e.target.closest(".node");
  const isBackground = !nodeEl;

  if (e.button === 1 || spaceDown || isBackground) {
    if (isBackground) selectNode(null);
    gesture = { type: "pan", startX: e.clientX, startY: e.clientY, camX: state.camera.x, camY: state.camera.y };
    viewport.classList.add("pan-live");
    viewport.setPointerCapture(e.pointerId);
    e.preventDefault();
    return;
  }

  const id = nodeEl.dataset.id;
  const node = state.nodes.find((n) => n.id === id);
  if (!node) return;
  selectNode(id);

  if (e.target.closest(".node-resize")) {
    gesture = { type: "resize", node, el: nodeEl, startX: e.clientX, startY: e.clientY, w: node.w, h: node.h };
    viewport.setPointerCapture(e.pointerId);
    e.preventDefault();
    return;
  }
  if (e.target.closest("[data-nodrag]")) return; // editable body / buttons

  gesture = { type: "node", node, el: nodeEl, startX: e.clientX, startY: e.clientY, x: node.x, y: node.y, moved: false };
  viewport.setPointerCapture(e.pointerId);
  e.preventDefault();
});

viewport.addEventListener("pointermove", (e) => {
  if (!gesture) return;
  const dx = e.clientX - gesture.startX;
  const dy = e.clientY - gesture.startY;

  if (gesture.type === "pan") {
    state.camera.x = gesture.camX + dx;
    state.camera.y = gesture.camY + dy;
    applyCamera();
  } else if (gesture.type === "node") {
    if (Math.abs(dx) + Math.abs(dy) > 3) gesture.moved = true;
    if (!gesture.moved) return;
    gesture.el.classList.add("dragging");
    gesture.node.x = gesture.x + dx / state.camera.scale;
    gesture.node.y = gesture.y + dy / state.camera.scale;
    positionNodeEl(gesture.el, gesture.node);
  } else if (gesture.type === "resize") {
    gesture.node.w = Math.max(140, gesture.w + dx / state.camera.scale);
    gesture.node.h = Math.max(90, gesture.h + dy / state.camera.scale);
    positionNodeEl(gesture.el, gesture.node);
  }
});

function endGesture(e) {
  if (!gesture) return;
  if (gesture.type === "pan") {
    viewport.classList.remove("pan-live");
  } else if (gesture.type === "node" && gesture.moved) {
    gesture.el.classList.remove("dragging");
    const n = gesture.node;
    persistNode(n, { x: Math.round(n.x), y: Math.round(n.y) });
  } else if (gesture.type === "resize") {
    const n = gesture.node;
    persistNode(n, { w: Math.round(n.w), h: Math.round(n.h) });
  }
  try { viewport.releasePointerCapture(e.pointerId); } catch {}
  gesture = null;
}
viewport.addEventListener("pointerup", endGesture);
viewport.addEventListener("pointercancel", endGesture);

viewport.addEventListener("wheel", (e) => {
  e.preventDefault();
  const factor = Math.exp(-e.deltaY * (e.ctrlKey ? 0.0035 : 0.0015));
  zoomAt(e.clientX, e.clientY, factor);
}, { passive: false });

viewport.addEventListener("dblclick", (e) => {
  if (e.target.closest(".node")) return;
  addNote(screenToWorld(e.clientX, e.clientY));
});

function addNote(at = null) { addNode("note", { text: "" }, at).then((n) => {
  const el = nodeEls.get(n.id);
  el?.querySelector(".node-body")?.focus();
}); }

/* ---------------------------------------------------------- *
 * Upload / drop
 * ---------------------------------------------------------- */

const dropOverlay = $("#dropOverlay");
let dragDepth = 0;

viewport.addEventListener("dragenter", (e) => { e.preventDefault(); dragDepth++; dropOverlay.classList.add("active"); });
viewport.addEventListener("dragover", (e) => { e.preventDefault(); });
viewport.addEventListener("dragleave", (e) => { e.preventDefault(); if (--dragDepth <= 0) { dragDepth = 0; dropOverlay.classList.remove("active"); } });
viewport.addEventListener("drop", async (e) => {
  e.preventDefault();
  dragDepth = 0;
  dropOverlay.classList.remove("active");
  const files = [...(e.dataTransfer?.files || [])];
  if (!files.length) return;
  const at = screenToWorld(e.clientX, e.clientY);
  let offset = 0;
  for (const f of files) {
    await placeFile(f, { x: at.x + offset, y: at.y + offset });
    offset += 36;
  }
});

$("#filePicker").addEventListener("change", async (e) => {
  for (const f of [...e.target.files]) await placeFile(f, null);
  e.target.value = "";
});

async function placeFile(file, at) {
  if (file.type.startsWith("video/")) {
    return addNode("video", { title: file.name, sub: "Video placeholder — upload queued" }, at);
  }
  if (!file.type.startsWith("image/")) {
    return addNode("note", { text: `📎 ${file.name}\n(unsupported type: ${file.type || "unknown"})` }, at);
  }
  try {
    const up = await state.backend.upload(file);
    // Size the node to the image's aspect ratio (bounded).
    const dims = await new Promise((ok) => {
      const im = new Image();
      im.onload = () => ok({ w: im.naturalWidth, h: im.naturalHeight });
      im.onerror = () => ok({ w: 4, h: 3 });
      im.src = up.url;
    });
    const w = 320, h = clamp(Math.round((w * dims.h) / dims.w), 120, 480);
    return addNode("image", { src: up.url, title: file.name, w, h }, at);
  } catch {
    toast("Upload failed", "err");
  }
}

/* ---------------------------------------------------------- *
 * Toolbar & keyboard
 * ---------------------------------------------------------- */

$("#toolbar").addEventListener("click", (e) => {
  const btn = e.target.closest("button[data-act]");
  if (!btn) return;
  const act = btn.dataset.act;
  if (act === "add-note") addNote();
  else if (act === "upload") $("#filePicker").click();
  else if (act === "add-video") addNode("video", { title: "untitled.mp4", sub: "Video placeholder" });
  else if (act === "zoom-in") zoomCenter(1.2);
  else if (act === "zoom-out") zoomCenter(1 / 1.2);
  else if (act === "zoom-fit") fitBoard();
});

zoomHud.addEventListener("click", resetZoom);

window.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    // Escape must work even while focus sits in a panel input.
    closeAllPanels();
    closePopover();
    if (!isTypingTarget(e.target)) selectNode(null);
    else e.target.blur?.();
    return;
  }
  if (e.code === "Space" && !isTypingTarget(e.target)) {
    spaceDown = true;
    viewport.classList.add("panning");
    if (!isTypingTarget(document.activeElement)) e.preventDefault();
    return;
  }
  if (isTypingTarget(e.target)) return;

  switch (e.key) {
    case "Delete":
    case "Backspace":
      if (state.selectedNodeId) { removeNode(state.selectedNodeId); e.preventDefault(); }
      break;
    case "n": case "N": addNote(); break;
    case "u": case "U": $("#filePicker").click(); break;
    case "v": case "V": addNode("video", { title: "untitled.mp4", sub: "Video placeholder" }); break;
    case "f": case "F": fitBoard(); break;
    case "0": resetZoom(); break;
    case "+": case "=": zoomCenter(1.2); break;
    case "-": case "_": zoomCenter(1 / 1.2); break;
    case "c": case "C": toggleChat(); break;
  }
});
window.addEventListener("keyup", (e) => {
  if (e.code === "Space") { spaceDown = false; viewport.classList.remove("panning"); }
});

/* ---------------------------------------------------------- *
 * Project switcher
 * ---------------------------------------------------------- */

let popoverEl = null;

function closePopover() {
  popoverEl?.remove();
  popoverEl = null;
  $("#projectBtn").setAttribute("aria-expanded", "false");
  document.removeEventListener("pointerdown", onPopoverOutside, true);
}
function onPopoverOutside(e) {
  if (popoverEl && !popoverEl.contains(e.target) && !$("#projectBtn").contains(e.target)) closePopover();
}

$("#projectBtn").addEventListener("click", () => {
  if (popoverEl) { closePopover(); return; }
  const btn = $("#projectBtn");
  btn.setAttribute("aria-expanded", "true");
  const pop = document.createElement("div");
  pop.className = "popover";
  pop.innerHTML = `<div class="pop-title">Projects</div>`;

  for (const p of state.projects) {
    const item = document.createElement("button");
    item.className = "pop-item" + (p.id === state.projectId ? " current" : "");
    item.innerHTML = `<span></span><span class="check">✓</span>`;
    item.firstChild.textContent = p.name;
    item.addEventListener("click", () => { closePopover(); if (p.id !== state.projectId) openProject(p.id); });
    pop.appendChild(item);
  }

  const div = document.createElement("div");
  div.className = "pop-divider";
  pop.appendChild(div);

  const row = document.createElement("div");
  row.className = "pop-new";
  const inp = document.createElement("input");
  inp.type = "text";
  inp.placeholder = "New project name…";
  const go = document.createElement("button");
  go.className = "btn primary";
  go.textContent = "Create";
  const create = async () => {
    const name = inp.value.trim();
    if (!name) return;
    closePopover();
    try {
      const p = await state.backend.createProject(name);
      state.projects.push(p);
      toast(`Project “${p.name}” created`, "ok");
      openProject(p.id);
    } catch { toast("Couldn't create project", "err"); }
  };
  go.addEventListener("click", create);
  inp.addEventListener("keydown", (e) => { if (e.key === "Enter") create(); });
  row.append(inp, go);
  pop.appendChild(row);

  document.body.appendChild(pop);
  const r = btn.getBoundingClientRect();
  pop.style.left = `${r.left}px`;
  pop.style.top = `${r.bottom + 6}px`;
  popoverEl = pop;
  setTimeout(() => inp.focus(), 40);
  document.addEventListener("pointerdown", onPopoverOutside, true);
});

async function openProject(pid) {
  state.projectId = pid;
  prefs.save({ projectId: pid });
  const proj = state.projects.find((p) => p.id === pid);
  $("#projName").textContent = proj?.name || "Untitled";

  // Load board + threads + brand kit in parallel.
  const [nodes, threads, kit] = await Promise.all([
    state.backend.listNodes(pid).catch(() => []),
    state.backend.listThreads(pid).catch(() => []),
    state.backend.getBrandKit(pid).catch(() => DEFAULT_BRAND_KIT()),
  ]);
  state.nodes = nodes;
  state.threads = threads;
  state.brandKit = { ...DEFAULT_BRAND_KIT(), ...kit };

  renderNodes();
  fitBoard();
  renderBrandKit();

  if (!state.threads.length) {
    try {
      const t = await state.backend.createThread(pid, "General");
      state.threads = [t];
    } catch { state.threads = []; }
  }
  renderThreadSel();
  if (state.threads.length) await openThread(state.threads[0].id);
  else { state.threadId = null; state.messages = []; renderMessages(); }
}

/* ---------------------------------------------------------- *
 * Threads & chat
 * ---------------------------------------------------------- */

function renderThreadSel() {
  const sel = $("#threadSel");
  sel.innerHTML = "";
  for (const t of state.threads) {
    const o = document.createElement("option");
    o.value = t.id;
    o.textContent = t.title;
    sel.appendChild(o);
  }
  if (state.threadId) sel.value = state.threadId;
}

$("#threadSel").addEventListener("change", (e) => openThread(e.target.value));

$("#newThreadBtn").addEventListener("click", async () => {
  const title = prompt("New thread title:", `Thread ${state.threads.length + 1}`);
  if (!title) return;
  try {
    const t = await state.backend.createThread(state.projectId, title.trim());
    state.threads.push(t);
    renderThreadSel();
    $("#threadSel").value = t.id;
    await openThread(t.id);
  } catch { toast("Couldn't create thread", "err"); }
});

async function openThread(tid) {
  state.threadId = tid;
  $("#threadSel").value = tid;
  state.messages = await state.backend.listMessages(tid).catch(() => []);
  renderMessages();
}

function msgMeta(m) {
  const who = m.role === "user" ? "You" : "Helix";
  const bits = [who];
  if (m.role === "assistant" && m.provider) bits.push(`${m.provider}/${m.model || "?"}`);
  if (m.role === "assistant" && m.mode) bits.push(m.mode);
  return bits.join(" · ");
}

function buildMsgEl(m) {
  const el = document.createElement("div");
  el.className = `msg role-${m.role}${m.error ? " error" : ""}`;
  el.dataset.id = m.id;

  const meta = document.createElement("div");
  meta.className = "msg-meta";
  meta.textContent = msgMeta(m);
  el.appendChild(meta);

  if (m.role === "assistant" && (m.thinking || m.mode === "thinking")) {
    const det = document.createElement("details");
    det.className = "msg-thinking";
    det.innerHTML = `<summary>Reasoning</summary><div class="think-body"></div>`;
    det.querySelector(".think-body").textContent = m.thinking || "";
    if (!m.thinking) det.hidden = true; // shown once thinking tokens arrive
    el.appendChild(det);
  }

  const body = document.createElement("div");
  body.className = "msg-body";
  body.textContent = m.content || "";
  el.appendChild(body);
  return el;
}

function renderMessages() {
  msgList.innerHTML = "";
  msgList.appendChild($("#chatEmpty") || Object.assign(document.createElement("div"), { id: "chatEmpty" }));
  const empty = $("#chatEmpty");
  empty.hidden = state.messages.length > 0;
  for (const m of state.messages) msgList.appendChild(buildMsgEl(m));
  msgList.scrollTop = msgList.scrollHeight;
}

function isPinnedToBottom() {
  return msgList.scrollHeight - msgList.scrollTop - msgList.clientHeight < 48;
}
function autoScroll(force = false) {
  if (force || isPinnedToBottom()) msgList.scrollTop = msgList.scrollHeight;
}

/* --- composer --- */

$("#modeSeg").addEventListener("click", (e) => {
  const btn = e.target.closest("button[data-mode]");
  if (!btn) return;
  state.mode = btn.dataset.mode;
  prefs.save({ mode: state.mode });
  for (const b of $$("#modeSeg button")) {
    const active = b === btn;
    b.classList.toggle("active", active);
    b.setAttribute("aria-checked", String(active));
  }
});

function renderProviderPick() {
  const pSel = $("#providerSel"), mSel = $("#modelSel");
  pSel.innerHTML = "";
  for (const p of state.providers) {
    const o = document.createElement("option");
    o.value = p.id;
    o.textContent = p.name;
    pSel.appendChild(o);
  }
  if (!state.providers.find((p) => p.id === state.provider)) state.provider = state.providers[0]?.id;
  pSel.value = state.provider;

  const models = (state.providers.find((p) => p.id === state.provider)?.models) || [];
  mSel.innerHTML = "";
  for (const m of models) {
    const id = typeof m === "string" ? m : m.id;
    const o = document.createElement("option");
    o.value = id;
    o.textContent = typeof m === "string" ? m : (m.label || m.id);
    mSel.appendChild(o);
  }
  if (!models.some((m) => (typeof m === "string" ? m : m.id) === state.model))
    state.model = typeof models[0] === "string" ? models[0] : models[0]?.id;
  if (state.model) mSel.value = state.model;
}

$("#providerSel").addEventListener("change", (e) => {
  state.provider = e.target.value;
  state.model = null;
  renderProviderPick();
  prefs.save({ provider: state.provider, model: state.model });
});
$("#modelSel").addEventListener("change", (e) => {
  state.model = e.target.value;
  prefs.save({ model: state.model });
});

chatInput.addEventListener("input", () => {
  chatInput.style.height = "auto";
  chatInput.style.height = Math.min(chatInput.scrollHeight, 160) + "px";
});
chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});
$("#sendBtn").addEventListener("click", sendMessage);

async function sendMessage() {
  const content = chatInput.value.trim();
  if (!content || state.streaming || !state.threadId) return;

  state.streaming = true;
  $("#sendBtn").disabled = true;
  chatInput.value = "";
  chatInput.style.height = "auto";

  const userMsg = {
    id: uid(), thread_id: state.threadId, role: "user", content,
    mode: state.mode, provider: state.provider, model: state.model, created_at: now(),
  };
  state.messages.push(userMsg);
  $("#chatEmpty").hidden = true;
  msgList.appendChild(buildMsgEl(userMsg));
  autoScroll(true);

  // Assistant placeholder that will fill in as tokens stream.
  const asstMsg = {
    id: uid(), thread_id: state.threadId, role: "assistant", content: "", thinking: "",
    mode: state.mode, provider: state.provider, model: state.model, created_at: now(),
  };
  state.messages.push(asstMsg);
  const asstEl = buildMsgEl(asstMsg);
  asstEl.classList.add("pending");
  msgList.appendChild(asstEl);
  autoScroll(true);

  const bodyEl = asstEl.querySelector(".msg-body");
  const thinkDetails = asstEl.querySelector(".msg-thinking");
  const thinkBody = asstEl.querySelector(".think-body");

  const finish = () => {
    state.streaming = false;
    $("#sendBtn").disabled = false;
    asstEl.classList.remove("pending");
    chatInput.focus();
  };

  try {
    await state.backend.sendChat(
      {
        thread_id: state.threadId,
        project_id: state.projectId,
        message: content,
        mode: state.mode,
        provider: state.provider,
        model: state.model,
      },
      {
        onThinking(tok) {
          if (thinkDetails) {
            thinkDetails.hidden = false;
            thinkDetails.open = true;
            asstMsg.thinking += tok;
            thinkBody.textContent = asstMsg.thinking;
            autoScroll();
          }
        },
        onToken(tok) {
          if (thinkDetails && thinkDetails.open) thinkDetails.open = false; // collapse once answer starts
          asstMsg.content += tok;
          bodyEl.textContent = asstMsg.content;
          autoScroll();
        },
        onDone(finalMsg) {
          if (finalMsg?.content && !asstMsg.content) {
            asstMsg.content = finalMsg.content;   // non-streaming server fallback
            bodyEl.textContent = asstMsg.content;
          }
          if (finalMsg?.id) asstMsg.id = finalMsg.id;
          finish();
          autoScroll();
        },
        onError(err) {
          asstMsg.error = true;
          asstEl.classList.add("error");
          bodyEl.textContent = asstMsg.content || `⚠ ${err.message}`;
          finish();
        },
      }
    );
  } catch (err) {
    asstMsg.error = true;
    asstEl.classList.add("error");
    bodyEl.textContent = `⚠ Request failed — ${err.message}`;
    finish();
  }
  // Safety: some code paths above call finish() already; make it idempotent.
  if (state.streaming) finish();
}

/* --- dock collapse --- */

function toggleChat(force) {
  const dock = $("#chatDock");
  const collapsed = typeof force === "boolean" ? !force : !dock.classList.contains("collapsed");
  dock.classList.toggle("collapsed", collapsed);
  $("#dockExpand").hidden = !collapsed;
  $("#chatToggleBtn").classList.toggle("active", !collapsed);
  prefs.save({ chatOpen: !collapsed });
}
$("#dockCollapse").addEventListener("click", () => toggleChat(false));
$("#dockExpand").addEventListener("click", () => toggleChat(true));
$("#chatToggleBtn").addEventListener("click", () => toggleChat());

/* ---------------------------------------------------------- *
 * Slide-over panels (settings / brand kit)
 * ---------------------------------------------------------- */

function openPanel(id) {
  closeAllPanels();
  const p = $(id);
  p.classList.add("open");
  p.setAttribute("aria-hidden", "false");
  $("#scrim").hidden = false;
}
function closeAllPanels() {
  for (const p of $$(".panel")) { p.classList.remove("open"); p.setAttribute("aria-hidden", "true"); }
  $("#scrim").hidden = true;
}
$("#scrim").addEventListener("click", closeAllPanels);
for (const btn of $$(".panel-close")) btn.addEventListener("click", closeAllPanels);
$("#settingsBtn").addEventListener("click", () => { renderKeys(); openPanel("#settingsPanel"); });
$("#brandKitBtn").addEventListener("click", () => { renderBrandKit(); openPanel("#brandPanel"); });

/* --- BYOK keys --- */

let keyHints = {};

async function loadKeyHints() {
  try { keyHints = (await state.backend.getKeys()) || {}; } catch { keyHints = {}; }
}

function renderKeys() {
  const list = $("#keysList");
  list.innerHTML = "";
  for (const kp of KEY_PROVIDERS) {
    const hint = keyHints[kp.id];
    const row = document.createElement("div");
    row.className = "key-row";

    const label = document.createElement("div");
    label.className = "key-label";
    const name = document.createElement("span");
    name.textContent = kp.label;
    const status = document.createElement("span");
    status.className = "key-status" + (hint?.set ? " set" : "");
    status.textContent = hint?.set ? `saved ${hint.hint || ""}` : "not set";
    label.append(name, status);

    const wrap = document.createElement("div");
    wrap.className = "key-input-wrap";
    const input = document.createElement("input");
    input.type = "password";
    input.autocomplete = "off";
    input.spellcheck = false;
    input.placeholder = hint?.set ? "Enter new key to replace" : kp.placeholder;
    input.dataset.provider = kp.id;

    const eye = document.createElement("button");
    eye.className = "icon-btn key-eye";
    eye.title = "Show / hide";
    eye.innerHTML = `<svg viewBox="0 0 24 24" width="15" height="15"><path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="12" cy="12" r="2.6" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>`;
    eye.addEventListener("click", () => {
      input.type = input.type === "password" ? "text" : "password";
      eye.style.color = input.type === "text" ? "var(--accent)" : "";
    });

    wrap.append(input, eye);
    row.append(label, wrap);
    list.appendChild(row);
  }
}

$("#saveKeysBtn").addEventListener("click", async () => {
  const map = {};
  for (const input of $$("#keysList input[data-provider]")) {
    if (input.value.trim()) map[input.dataset.provider] = input.value.trim();
  }
  if (!Object.keys(map).length) { toast("Nothing to save — enter at least one key"); return; }
  try {
    keyHints = (await state.backend.saveKeys(map)) || keyHints;
    await loadKeyHints();
    renderKeys();
    toast("Keys saved", "ok");
  } catch { toast("Couldn't save keys", "err"); }
});

$("#retryConnBtn").addEventListener("click", retryConnection);
$("#connPill").addEventListener("click", retryConnection);

async function retryConnection() {
  const det = await detectBackend();
  const wasLive = state.live;
  state.backend = det.backend;
  state.live = det.live;
  renderConnState();
  if (det.live && !wasLive) {
    toast("Connected to /api — reloading data", "ok");
    await bootData();
  } else if (!det.live) {
    toast("Still no /api backend — staying in demo mode");
  }
}

/* --- brand kit --- */

function renderBrandKit() {
  const kit = state.brandKit;
  const colorsEl = $("#bkColors");
  colorsEl.innerHTML = "";
  kit.colors.forEach((c, i) => {
    const row = document.createElement("div");
    row.className = "bk-color-row";

    const swatch = document.createElement("input");
    swatch.type = "color";
    swatch.value = /^#([0-9a-f]{6})$/i.test(c.value) ? c.value : "#888888";
    swatch.addEventListener("input", () => { c.value = swatch.value; hex.textContent = swatch.value.toUpperCase(); });

    const name = document.createElement("input");
    name.type = "text";
    name.value = c.name || "";
    name.placeholder = "Role (e.g. Primary)";
    name.addEventListener("input", () => { c.name = name.value; });

    const hex = document.createElement("span");
    hex.className = "bk-hex";
    hex.textContent = (c.value || "").toUpperCase();

    const del = document.createElement("button");
    del.className = "icon-btn";
    del.title = "Remove color";
    del.innerHTML = `<svg viewBox="0 0 24 24" width="13" height="13"><path d="M6 6l12 12M18 6 6 18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>`;
    del.addEventListener("click", () => { kit.colors.splice(i, 1); renderBrandKit(); });

    row.append(swatch, name, hex, del);
    colorsEl.appendChild(row);
  });

  $("#bkHeadingFont").value = kit.fonts?.heading || "";
  $("#bkBodyFont").value = kit.fonts?.body || "";
  $("#bkVoice").value = kit.voice || "";

  const img = $("#bkLogoImg"), hint = $("#bkLogoHint");
  if (kit.logo_url) { img.src = kit.logo_url; img.hidden = false; hint.hidden = true; }
  else { img.hidden = true; hint.hidden = false; }
}

$("#bkAddColor").addEventListener("click", () => {
  state.brandKit.colors.push({ name: "", value: "#e0a94e" });
  renderBrandKit();
});

const logoDrop = $("#bkLogoDrop");
logoDrop.addEventListener("click", () => $("#logoPicker").click());
logoDrop.addEventListener("dragover", (e) => { e.preventDefault(); logoDrop.classList.add("over"); });
logoDrop.addEventListener("dragleave", () => logoDrop.classList.remove("over"));
logoDrop.addEventListener("drop", async (e) => {
  e.preventDefault();
  logoDrop.classList.remove("over");
  const f = e.dataTransfer?.files?.[0];
  if (f) await setLogo(f);
});
$("#logoPicker").addEventListener("change", async (e) => {
  const f = e.target.files?.[0];
  if (f) await setLogo(f);
  e.target.value = "";
});
async function setLogo(file) {
  if (!file.type.startsWith("image/")) { toast("Logo must be an image", "err"); return; }
  try {
    const up = await state.backend.upload(file);
    state.brandKit.logo_url = up.url;
    renderBrandKit();
  } catch { toast("Logo upload failed", "err"); }
}

$("#saveBrandBtn").addEventListener("click", async () => {
  state.brandKit.fonts = {
    heading: $("#bkHeadingFont").value.trim(),
    body: $("#bkBodyFont").value.trim(),
  };
  state.brandKit.voice = $("#bkVoice").value.trim();
  try {
    await state.backend.saveBrandKit(state.projectId, state.brandKit);
    toast("Brand kit saved", "ok");
  } catch { toast("Couldn't save brand kit", "err"); }
});

/* ---------------------------------------------------------- *
 * Boot
 * ---------------------------------------------------------- */

async function bootData() {
  const p = prefs.load();
  if (p.mode === "thinking" || p.mode === "fast") {
    state.mode = p.mode;
    for (const b of $$("#modeSeg button")) {
      const active = b.dataset.mode === state.mode;
      b.classList.toggle("active", active);
      b.setAttribute("aria-checked", String(active));
    }
  }

  try { const provs = await state.backend.listProviders(); if (provs.length) state.providers = provs; } catch {}
  if (p.provider) state.provider = p.provider;
  if (p.model) state.model = p.model;
  renderProviderPick();

  await loadKeyHints();

  try {
    state.projects = await state.backend.listProjects();
  } catch {
    state.projects = [];
  }
  if (!state.projects.length) {
    try { state.projects = [await state.backend.createProject("Untitled project")]; }
    catch { toast("Couldn't load projects", "err"); return; }
  }
  const wanted = p.projectId && state.projects.find((x) => x.id === p.projectId) ? p.projectId : state.projects[0].id;
  await openProject(wanted);
}

async function boot() {
  resetZoom();

  const det = await detectBackend();
  state.backend = det.backend;
  state.live = det.live;
  renderConnState();
  if (!det.live) toast("No /api backend found — running in demo mode");

  const p = prefs.load();
  if (p.chatOpen === false) toggleChat(false);

  await bootData();
}

window.addEventListener("resize", applyCamera);
boot();

})();
