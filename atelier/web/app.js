const state = {
  projects: [],
  threads: [],
  projectId: null,
  threadId: null,
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
  if (!res.ok) throw new Error(data.error || res.statusText);
  return data;
}

function el(tag, attrs = {}, kids = []) {
  const node = document.createElement(tag);
  Object.entries(attrs).forEach(([k, v]) => {
    if (k === "class") node.className = v;
    else if (k === "text") node.textContent = v;
    else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v);
  });
  kids.forEach((c) => node.append(c));
  return node;
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

async function refreshBoard() {
  if (!state.projectId) return;
  const data = await api(`/api/projects/${state.projectId}/board`);
  const board = document.getElementById("board");
  board.innerHTML = "";
  (data.nodes || []).forEach((node) => {
    const card = el("div", { class: "node" + (node.type === "note" ? " note" : "") });
    card.style.left = node.x + "px";
    card.style.top = node.y + "px";
    card.style.width = node.w + "px";
    card.style.height = node.h + "px";
    if (node.type === "image" && node.artifact_id) {
      const img = el("img", { src: `/api/artifacts/${node.artifact_id}`, alt: node.text || "" });
      card.append(img, el("div", { class: "cap", text: node.text || "artifact" }));
    } else {
      card.textContent = node.text || "note";
    }
    enableDrag(card, node);
    board.append(card);
  });
}

function enableDrag(card, node) {
  let sx, sy, ox, oy, moving = false;
  card.addEventListener("pointerdown", (e) => {
    moving = true;
    sx = e.clientX; sy = e.clientY;
    ox = node.x; oy = node.y;
    card.setPointerCapture(e.pointerId);
  });
  card.addEventListener("pointermove", (e) => {
    if (!moving) return;
    node.x = ox + (e.clientX - sx);
    node.y = oy + (e.clientY - sy);
    card.style.left = node.x + "px";
    card.style.top = node.y + "px";
  });
  card.addEventListener("pointerup", async () => {
    if (!moving) return;
    moving = false;
    await api(`/api/nodes/${node.id}`, { method: "POST", body: { x: node.x, y: node.y } });
  });
}

async function refreshMessages() {
  const box = document.getElementById("messages");
  box.innerHTML = "";
  if (!state.threadId) return;
  const data = await api(`/api/threads/${state.threadId}/messages`);
  (data.messages || []).forEach((m) => {
    box.append(el("div", { class: "msg " + m.role, text: m.content }));
  });
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
};

document.getElementById("saveBrand").onclick = async () => {
  const kit = JSON.parse(document.getElementById("brandKit").value || "{}");
  await api(`/api/projects/${state.projectId}/brand`, { method: "POST", body: { brand_kit: kit } });
};

document.getElementById("run").onclick = async () => {
  const status = document.getElementById("runStatus");
  status.textContent = "Conductor weaving…";
  try {
    if (!state.threadId) throw new Error("create a thread first");
    await api(`/api/threads/${state.threadId}/run`, {
      method: "POST",
      body: {
        prompt: document.getElementById("prompt").value,
        mode: document.getElementById("mode").value,
        provider: document.getElementById("provider").value,
        model: document.getElementById("model").value,
      },
    });
    document.getElementById("prompt").value = "";
    await bootProject();
    status.textContent = "Pinned to board.";
  } catch (err) {
    status.textContent = err.message;
  }
};

document.getElementById("openCatalog").onclick = async () => {
  const data = await api("/api/catalog");
  const names = (data.mvp_wire || []).join(", ");
  alert(`Helix catalog: ${data.count} repos. MVP wire: ${names}`);
};

bootProject().catch((err) => {
  document.getElementById("runStatus").textContent = err.message;
});
