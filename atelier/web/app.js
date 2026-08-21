const state = {
  projects: [],
  threads: [],
  projectId: null,
  threadId: null,
  camera: { x: 0, y: 0, zoom: 1 },
  lastArtifactId: null,
  lastUploadId: null,
};

async function api(path, opts = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  const text = await res.text();
  let data = {};
  try { data = text ? JSON.parse(text) : {}; } catch { data = { raw: text }; }
  if (!res.ok) {
    const err = new Error(data.error || res.statusText);
    err.status = res.status;
    err.code = data.code;
    throw err;
  }
  return data;
}

function el(tag, attrs = {}, kids = []) {
  const node = document.createElement(tag);
  Object.entries(attrs).forEach(([k, v]) => {
    if (k === "class") node.className = v;
    else if (k === "text") node.textContent = v;
    else if (k === "html") node.innerHTML = v;
    else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v);
  });
  kids.forEach((c) => node.append(c));
  return node;
}

function applyCamera() {
  const board = document.getElementById("board");
  const { x, y, zoom } = state.camera;
  board.style.transform = `translate(${x}px, ${y}px) scale(${zoom})`;
  const readout = document.getElementById("camReadout");
  if (readout) readout.textContent = Math.round(zoom * 100) + "%";
}

let persistCameraTimer = null;
let pendingCamera = null;

function clampCamera(camera) {
  const zoom = Number(camera && camera.zoom);
  return {
    x: Number(camera && camera.x) || 0,
    y: Number(camera && camera.y) || 0,
    zoom: Math.min(3, Math.max(0.25, zoom > 0 ? zoom : 1)),
  };
}

async function flushCamera() {
  clearTimeout(persistCameraTimer);
  persistCameraTimer = null;
  const pending = pendingCamera;
  pendingCamera = null;
  if (!pending) return;
  try {
    await api(`/api/projects/${pending.projectId}/camera`, {
      method: "POST",
      body: { camera: pending.camera },
    });
  } catch { /* camera persist is best-effort */ }
}

// Project and camera are captured when the write is scheduled, not when it
// fires: switching projects inside the debounce window must still land the
// move on the board that actually moved.
function persistCamera() {
  if (!state.projectId) return;
  pendingCamera = { projectId: state.projectId, camera: clampCamera(state.camera) };
  clearTimeout(persistCameraTimer);
  persistCameraTimer = setTimeout(flushCamera, 180);
}

function resetCamera() {
  state.camera = { x: 0, y: 0, zoom: 1 };
  applyCamera();
  persistCamera();
}

function fitCamera() {
  const cards = [...document.querySelectorAll("#board .node")];
  if (!cards.length) {
    resetCamera();
    return;
  }
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  cards.forEach((card) => {
    const x = parseFloat(card.style.left) || 0;
    const y = parseFloat(card.style.top) || 0;
    const w = parseFloat(card.style.width) || 280;
    const h = parseFloat(card.style.height) || 200;
    minX = Math.min(minX, x);
    minY = Math.min(minY, y);
    maxX = Math.max(maxX, x + w);
    maxY = Math.max(maxY, y + h);
  });
  const wrap = document.getElementById("boardWrap");
  const vw = wrap.clientWidth || 800;
  const vh = wrap.clientHeight || 600;
  const pad = 64;
  const spanX = Math.max(1, maxX - minX);
  const spanY = Math.max(1, maxY - minY);
  const zoom = Math.min(3, Math.max(0.25, Math.min((vw - pad * 2) / spanX, (vh - pad * 2) / spanY)));
  state.camera = {
    x: (vw - (maxX + minX) * zoom) / 2,
    y: (vh - (maxY + minY) * zoom) / 2,
    zoom,
  };
  applyCamera();
  persistCamera();
}

async function refreshProjects() {
  const data = await api("/api/projects");
  state.projects = data.projects || [];
  if (!state.projectId && state.projects[0]) state.projectId = state.projects[0].id;
  const box = document.getElementById("projectList");
  box.innerHTML = "";
  state.projects.forEach((p) => {
    box.append(el("button", {
      class: "item" + (p.id === state.projectId ? " active" : ""),
      text: p.name,
      onclick: async () => {
        await flushCamera();
        state.projectId = p.id;
        state.threadId = null;
        state.lastUploadId = null;
        await bootProject();
      },
    }));
  });
}

async function refreshThreads() {
  if (!state.projectId) return;
  const data = await api(`/api/projects/${state.projectId}/threads`);
  state.threads = data.threads || [];
  if (!state.threadId && state.threads[0]) state.threadId = state.threads[0].id;
  const box = document.getElementById("threadList");
  box.innerHTML = "";
  state.threads.forEach((t) => {
    box.append(el("button", {
      class: "item" + (t.id === state.threadId ? " active" : ""),
      text: (t.topic || "untitled") + " · " + t.mode,
      onclick: async () => {
        state.threadId = t.id;
        await refreshMessages();
        refreshThreads();
      },
    }));
  });
}

function renderPlan(plan) {
  const card = document.getElementById("planCard");
  if (!plan) {
    card.classList.add("hidden");
    card.innerHTML = "";
    return;
  }
  card.classList.remove("hidden");
  const route = plan.route || {};
  const weave = plan.weave || [];
  card.innerHTML = "";
  const steps = el("ol", { class: "plan-steps" }, weave.slice(0, 4).map((w) => {
    const label = `${w.kind || "image"}: ${(w.prompt || "").slice(0, 80)}`;
    return el("li", {
      class: "plan-step",
      text: label,
      title: "Click to load this step into the composer",
      onclick: (ev) => {
        ev.currentTarget.classList.toggle("done");
        const box = document.getElementById("prompt");
        if (box) box.value = w.prompt || "";
      },
    });
  }));
  card.append(
    el("div", { class: "plan-title", text: "Plan · " + (plan.intent || "brief") }),
    el("div", { class: "plan-meta", text: `${plan.mode || "fast"} · ${route.provider || "demo"} / ${route.model || ""}` }),
    steps,
  );
  const critique = (plan.critique || "").trim();
  if (critique) {
    card.append(el("div", { class: "plan-critic", text: "Critique · " + critique }));
  }
}

async function refreshBoard() {
  if (!state.projectId) return;
  const data = await api(`/api/projects/${state.projectId}/board`);
  if (data.camera) state.camera = clampCamera(data.camera);
  applyCamera();
  const board = document.getElementById("board");
  board.innerHTML = "";
  (data.nodes || []).forEach((node) => {
    const card = el("div", { class: "node" + (node.type === "note" || node.type === "text" ? " note" : "") + (node.type === "text" ? " text-layer" : "") });
    card.style.left = node.x + "px";
    card.style.top = node.y + "px";
    card.style.width = node.w + "px";
    card.style.height = node.h + "px";
    if (node.type === "image" && node.artifact_id) {
      state.lastArtifactId = node.artifact_id;
      const img = el("img", { src: `/api/artifacts/${node.artifact_id}`, alt: node.text || "" });
      const tools = el("div", { class: "node-tools" }, [
        el("a", { href: `/api/artifacts/${node.artifact_id}?download=1`, text: "Download", class: "dl" }),
      ]);
      card.append(img, el("div", { class: "cap", text: node.text || "artifact" }), tools);
    } else {
      card.append(el("div", { class: "text-body", text: node.text || "note" }));
    }
    enableDrag(card, node);
    board.append(card);
  });
}

function enableDrag(card, node) {
  let sx, sy, ox, oy, moving = false;
  card.addEventListener("pointerdown", (e) => {
    e.stopPropagation();
    moving = true;
    sx = e.clientX; sy = e.clientY;
    ox = node.x; oy = node.y;
    card.setPointerCapture(e.pointerId);
  });
  card.addEventListener("pointermove", (e) => {
    if (!moving) return;
    const z = state.camera.zoom || 1;
    node.x = ox + (e.clientX - sx) / z;
    node.y = oy + (e.clientY - sy) / z;
    card.style.left = node.x + "px";
    card.style.top = node.y + "px";
  });
  card.addEventListener("pointerup", async () => {
    if (!moving) return;
    moving = false;
    await api(`/api/nodes/${node.id}`, { method: "POST", body: { x: node.x, y: node.y } });
  });
}

function zoomAt(px, py, factor) {
  const z = state.camera.zoom || 1;
  const next = clampCamera({ ...state.camera, zoom: z * factor });
  const z2 = next.zoom;
  const ratio = z ? z2 / z : 1;
  next.x = px - (px - (state.camera.x || 0)) * ratio;
  next.y = py - (py - (state.camera.y || 0)) * ratio;
  state.camera = next;
}

function enableBoardCamera() {
  const wrap = document.getElementById("boardWrap");
  let panning = false, sx = 0, sy = 0, ox = 0, oy = 0;
  wrap.addEventListener("wheel", (e) => {
    e.preventDefault();
    const rect = wrap.getBoundingClientRect ? wrap.getBoundingClientRect() : { left: 0, top: 0 };
    const px = (e.clientX || 0) - (rect.left || 0);
    const py = (e.clientY || 0) - (rect.top || 0);
    if (e.shiftKey && !e.ctrlKey && !e.metaKey) {
      state.camera.x -= e.deltaX || e.deltaY || 0;
      state.camera.y -= e.deltaY || 0;
    } else {
      const factor = e.deltaY > 0 ? 0.92 : 1.08;
      zoomAt(px, py, factor);
    }
    applyCamera();
    persistCamera();
  }, { passive: false });
  wrap.addEventListener("pointerdown", (e) => {
    if (e.target.closest(".node") || e.target.closest(".board-tools")) return;
    panning = true;
    sx = e.clientX; sy = e.clientY;
    ox = state.camera.x; oy = state.camera.y;
    wrap.setPointerCapture(e.pointerId);
  });
  wrap.addEventListener("pointermove", (e) => {
    if (!panning) return;
    state.camera.x = ox + (e.clientX - sx);
    state.camera.y = oy + (e.clientY - sy);
    applyCamera();
  });
  wrap.addEventListener("pointerup", () => {
    if (!panning) return;
    panning = false;
    persistCamera();
  });
  wrap.addEventListener("dragover", (e) => e.preventDefault());
  wrap.addEventListener("drop", async (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) await uploadFile(file);
  });
}

function bytesToBase64(bytes) {
  let bin = "";
  const chunk = 0x8000;
  for (let i = 0; i < bytes.length; i += chunk) {
    bin += String.fromCharCode.apply(null, bytes.subarray(i, i + chunk));
  }
  return btoa(bin);
}

async function uploadFile(file) {
  if (!state.projectId) throw new Error("create a project first");
  const buf = await file.arrayBuffer();
  const data = bytesToBase64(new Uint8Array(buf));
  const result = await api(`/api/projects/${state.projectId}/upload`, {
    method: "POST",
    body: { filename: file.name, mime: file.type || "application/octet-stream", data },
  });
  const id = result.artifact && result.artifact.id;
  if (id) {
    state.lastUploadId = id;
    state.lastArtifactId = id;
  }
  await refreshBoard();
  document.getElementById("runStatus").textContent =
    "Uploaded " + file.name + " · next weave uses it as reference";
}

async function refreshMessages() {
  const box = document.getElementById("messages");
  box.innerHTML = "";
  if (!state.threadId) return;
  const data = await api(`/api/threads/${state.threadId}/messages`);
  let lastPlan = null;
  (data.messages || []).forEach((m) => {
    box.append(el("div", { class: "msg " + m.role, text: m.content }));
    if (m.plan) lastPlan = m.plan;
  });
  renderPlan(lastPlan);
  box.scrollTop = box.scrollHeight;
}

async function refreshKeys() {
  const keys = await api("/api/keys");
  const bits = Object.entries(keys).map(([k, v]) => {
    const mark = v.configured ? "ok" : "warn";
    return `<span class="pill ${mark}">${k}:${v.source}</span>`;
  });
  document.getElementById("keyStatus").innerHTML = bits.join(" ");
}

async function refreshBrand() {
  if (!state.projectId) return;
  const project = await api(`/api/projects/${state.projectId}`);
  document.getElementById("brandKit").value = JSON.stringify(project.brand_kit || {}, null, 2);
}

async function bootProject() {
  await refreshProjects();
  await refreshThreads();
  await refreshBoard();
  await refreshMessages();
  await refreshBrand();
  await refreshKeys();
  const usage = await api("/api/usage");
  const usd = (usage.totals || []).reduce((s, t) => s + (t.estimated_usd || 0), 0);
  document.getElementById("topMeta").textContent =
    `Helix · estimated spend $${usd.toFixed(4)} · keys stay on this machine`;
}

document.getElementById("newProject").onclick = async () => {
  const name = prompt("Project name", "Untitled cloth") || "Untitled cloth";
  const project = await api("/api/projects", { method: "POST", body: { name } });
  state.projectId = project.id;
  state.threadId = null;
  state.lastUploadId = null;
  await bootProject();
};

document.getElementById("newThread").onclick = async () => {
  if (!state.projectId) return;
  const thread = await api(`/api/projects/${state.projectId}/threads`, {
    method: "POST",
    body: { topic: "New thread", mode: document.getElementById("mode").value },
  });
  state.threadId = thread.id;
  await bootProject();
};

document.getElementById("saveKey").onclick = async () => {
  try {
    await api("/api/keys", {
      method: "POST",
      body: {
        provider: document.getElementById("keyProvider").value,
        key: document.getElementById("keyValue").value,
        base_url: document.getElementById("keyBase").value,
      },
    });
    document.getElementById("keyValue").value = "";
    await refreshKeys();
  } catch (err) {
    document.getElementById("runStatus").textContent = err.message;
  }
};

document.getElementById("saveBrand").onclick = async () => {
  const kit = JSON.parse(document.getElementById("brandKit").value || "{}");
  await api(`/api/projects/${state.projectId}/brand`, { method: "POST", body: { brand_kit: kit } });
};

function runBody() {
  const prompt = document.getElementById("prompt").value;
  const spot = state.lastArtifactId && /spot|局部|edit this/i.test(prompt);
  return {
    prompt,
    mode: document.getElementById("mode").value,
    provider: document.getElementById("provider").value,
    model: document.getElementById("model").value,
    variants: document.getElementById("variants").checked ? 4 : 0,
    parent_artifact_id: spot ? state.lastArtifactId : (state.lastUploadId || undefined),
  };
}

document.getElementById("quoteBtn").onclick = async () => {
  const status = document.getElementById("runStatus");
  try {
    const q = await api("/api/quote", { method: "POST", body: { ...runBody(), thread_id: state.threadId } });
    const label = q.priced ? "priced" : "unpriced conservative";
    status.textContent = `Quote $${Number(q.estimated_usd).toFixed(4)} (${label})` +
      (q.would_exceed ? " — would exceed budget" : "");
  } catch (err) {
    status.textContent = err.message;
  }
};

document.getElementById("run").onclick = async () => {
  const status = document.getElementById("runStatus");
  status.textContent = "Conductor weaving…";
  try {
    if (!state.threadId) throw new Error("create a thread first");
    const result = await api(`/api/threads/${state.threadId}/run?stream=0`, {
      method: "POST",
      body: runBody(),
    });
    if (result.ok === false) throw new Error(result.error || "weave failed");
    document.getElementById("prompt").value = "";
    state.lastUploadId = null;
    renderPlan(result.plan);
    const phases = (result.events || []).filter((e) => e.kind === "phase").map((e) => e.phase);
    status.textContent = result.errors && result.errors.length
      ? result.errors[0]
      : "Pinned to board. " + (phases.length ? phases.join(" → ") : "");
    await bootProject();
  } catch (err) {
    status.textContent = err.message;
    status.classList.add("danger");
  }
};

document.getElementById("undoBtn").onclick = async () => {
  if (!state.projectId) return;
  await api(`/api/projects/${state.projectId}/undo`, { method: "POST", body: {} });
  await refreshBoard();
};

document.getElementById("textLayer").onclick = async () => {
  if (!state.projectId) return;
  const text = prompt("Text layer", "Headline") || "Headline";
  await api(`/api/projects/${state.projectId}/nodes`, {
    method: "POST",
    body: { type: "text", text, x: 120, y: 120 },
  });
  await refreshBoard();
};

document.getElementById("exportZip").onclick = () => {
  if (!state.projectId) return;
  window.location = `/api/projects/${state.projectId}/export`;
};

document.getElementById("openCatalog").onclick = async () => {
  const data = await api("/api/catalog");
  const names = (data.mvp_wire || []).join(", ");
  alert(`Helix catalog: ${data.count} repos. MVP wire: ${names}`);
};

document.getElementById("camHome").onclick = resetCamera;
document.getElementById("camFit").onclick = fitCamera;
document.getElementById("camReadout").onclick = resetCamera;
window.addEventListener("pagehide", flushCamera);

document.getElementById("uploadBtn").onclick = () => {
  document.getElementById("filePick").click();
};
document.getElementById("filePick").addEventListener("change", async (e) => {
  const file = e.target.files && e.target.files[0];
  e.target.value = "";
  if (!file) return;
  try {
    await uploadFile(file);
  } catch (err) {
    document.getElementById("runStatus").textContent = err.message;
  }
});
document.addEventListener("keydown", (e) => {
  if (e.target.closest("input, textarea, select, [contenteditable]")) return;
  if (e.key === "u" || e.key === "U") {
    e.preventDefault();
    document.getElementById("filePick").click();
  }
  if (e.key === "0" || e.key === "h" || e.key === "H") {
    e.preventDefault();
    resetCamera();
  }
  if (e.key === "f" || e.key === "F") {
    e.preventDefault();
    fitCamera();
  }
});

enableBoardCamera();
bootProject().catch((err) => {
  document.getElementById("runStatus").textContent = err.message;
});
