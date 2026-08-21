const state = {
  projects: [],
  threads: [],
  projectId: null,
  threadId: null,
  camera: { x: 0, y: 0, zoom: 1 },
  lastArtifactId: null,
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

async function persistCamera() {
  if (!state.projectId) return;
  try {
    await api(`/api/projects/${state.projectId}/camera`, {
      method: "POST",
      body: { camera: state.camera },
    });
  } catch { /* camera persist is best-effort */ }
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
        state.projectId = p.id;
        state.threadId = null;
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
  card.append(
    el("div", { class: "plan-title", text: "Plan · " + (plan.intent || "brief") }),
    el("div", { class: "plan-meta", text: `${plan.mode || "fast"} · ${route.provider || "demo"} / ${route.model || ""}` }),
    el("ol", { class: "plan-steps" }, weave.slice(0, 4).map((w, i) =>
      el("li", { text: `${w.kind || "image"}: ${(w.prompt || "").slice(0, 80)}` })
    )),
  );
}

async function refreshBoard() {
  if (!state.projectId) return;
  const data = await api(`/api/projects/${state.projectId}/board`);
  if (data.camera) state.camera = data.camera;
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

function enableBoardCamera() {
  const wrap = document.getElementById("boardWrap");
  let panning = false, sx = 0, sy = 0, ox = 0, oy = 0;
  wrap.addEventListener("wheel", (e) => {
    e.preventDefault();
    const factor = e.deltaY > 0 ? 0.92 : 1.08;
    state.camera.zoom = Math.min(3, Math.max(0.25, (state.camera.zoom || 1) * factor));
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

async function uploadFile(file) {
  const buf = await file.arrayBuffer();
  const bytes = new Uint8Array(buf);
  let bin = "";
  bytes.forEach((b) => { bin += String.fromCharCode(b); });
  const data = btoa(bin);
  await api(`/api/projects/${state.projectId}/upload`, {
    method: "POST",
    body: { filename: file.name, mime: file.type || "application/octet-stream", data },
  });
  await refreshBoard();
  document.getElementById("runStatus").textContent = "Uploaded " + file.name;
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
  return {
    prompt: document.getElementById("prompt").value,
    mode: document.getElementById("mode").value,
    provider: document.getElementById("provider").value,
    model: document.getElementById("model").value,
    variants: document.getElementById("variants").checked ? 4 : 0,
    parent_artifact_id: state.lastArtifactId && /spot|局部|edit this/i.test(document.getElementById("prompt").value)
      ? state.lastArtifactId
      : undefined,
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

enableBoardCamera();
bootProject().catch((err) => {
  document.getElementById("runStatus").textContent = err.message;
});
