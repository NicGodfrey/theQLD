(() => {
  let models = Meridian.load("proxy-router:models", [
    { id: "m1", name: "gpt-4.1-mini", weight: 50, cost: 0.4, latency: 420 },
    { id: "m2", name: "deepseek-chat", weight: 35, cost: 0.14, latency: 380 },
    { id: "m3", name: "gemini-flash", weight: 15, cost: 0.1, latency: 360 },
  ]);

  const modelsEl = document.getElementById("models");

  function renderModels() {
    modelsEl.innerHTML = models
      .map(
        (m) => `<div class="list-item" style="flex-direction:column;align-items:stretch;gap:.35rem">
        <strong>${m.name}</strong>
        <label class="muted">权重 <input data-w="${m.id}" type="number" value="${m.weight}" style="width:100%" /></label>
        <label class="muted">成本 $/1M <input data-c="${m.id}" type="number" step="0.01" value="${m.cost}" style="width:100%" /></label>
        <label class="muted">延迟 ms <input data-l="${m.id}" type="number" value="${m.latency}" style="width:100%" /></label>
      </div>`
      )
      .join("");
    drawGraph();
    renderCfg();
  }

  modelsEl.addEventListener("input", (e) => {
    const t = e.target;
    const m = models.find((x) => x.id === (t.dataset.w || t.dataset.c || t.dataset.l));
    if (!m) return;
    if (t.dataset.w) m.weight = Number(t.value);
    if (t.dataset.c) m.cost = Number(t.value);
    if (t.dataset.l) m.latency = Number(t.value);
    Meridian.save("proxy-router:models", models);
    drawGraph();
    renderCfg();
  });

  function drawGraph() {
    const total = models.reduce((s, m) => s + m.weight, 0) || 1;
    const nodes = models
      .map((m, i) => {
        const x = 160 + i * 180;
        const y = 140;
        const r = 28 + (m.weight / total) * 36;
        return `<circle cx="${x}" cy="${y}" r="${r}" fill="#1F6F78" fill-opacity="0.85"/><text x="${x}" y="${y + 5}" text-anchor="middle" fill="#F3F0E7" font-size="12" font-family="IBM Plex Sans">${m.name.split("-")[0]}</text><text x="${x}" y="210" text-anchor="middle" fill="#0B1F2A" font-size="12">${m.weight}%</text>`;
      })
      .join("");
    const lines = models
      .map((m, i) => {
        const x = 160 + i * 180;
        return `<path d="M80 80 C 120 80, ${x - 40} 100, ${x} ${140 - (28 + (m.weight / total) * 36)}" stroke="#0B1F2A" stroke-opacity="0.35" fill="none" stroke-width="3"/>`;
      })
      .join("");
    document.getElementById("graph").innerHTML =
      `<rect width="720" height="260" fill="transparent"/><circle cx="80" cy="80" r="34" fill="#C8F542"/><text x="80" y="85" text-anchor="middle" font-size="12" font-weight="700">Gate</text>${lines}${nodes}`;
  }

  function pick(rnd) {
    const total = models.reduce((s, m) => s + m.weight, 0) || 1;
    let r = rnd() * total;
    for (const m of models) {
      r -= m.weight;
      if (r <= 0) return m;
    }
    return models[models.length - 1];
  }

  document.getElementById("simBtn").onclick = () => {
    const rnd = Meridian.seed(Date.now());
    const counts = Object.fromEntries(models.map((m) => [m.name, 0]));
    let cost = 0;
    let lat = 0;
    let fails = 0;
    for (let i = 0; i < 100; i++) {
      let m = pick(rnd);
      if (rnd() < 0.08) {
        fails++;
        const mode = document.getElementById("failover").value;
        const sorted = [...models].sort((a, b) =>
          mode === "cheapest" ? a.cost - b.cost : mode === "fastest" ? a.latency - b.latency : b.weight - a.weight
        );
        m = sorted.find((x) => x.name !== m.name) || m;
      }
      counts[m.name]++;
      cost += m.cost;
      lat += m.latency;
    }
    document.getElementById("stats").textContent = [
      "100 次请求分布：",
      ...Object.entries(counts).map(([k, v]) => `- ${k}: ${v}`),
      `失败转移次数: ${fails}`,
      `估算均成本指数: ${(cost / 100).toFixed(3)}`,
      `估算均延迟: ${Math.round(lat / 100)}ms`,
    ].join("\n");
  };

  function renderCfg() {
    const caddy = models
      .map((m) => `  to ${m.name}.upstream:443 {\n    weight ${m.weight}\n  }`)
      .join("\n");
    const nginx = models.map((m) => `server ${m.name}.upstream:443 weight=${m.weight};`).join("\n");
    const traefik = models
      .map(
        (m, i) => `      - name: ${m.name}\n        url: https://${m.name}.upstream\n        weight: ${m.weight}`
      )
      .join("\n");
    document.getElementById("cfg").textContent = `# Caddyfile\nreverse_proxy {\n${caddy}\n}\n\n# Nginx upstream\nupstream ai_pool {\n${nginx}\n}\n\n# Traefik YAML fragment\nservices:\n  ai-router:\n    loadBalancer:\n      servers:\n${traefik}\n`;
  }

  document.getElementById("addModel").onclick = () => {
    models.push({ id: Meridian.uid("m"), name: "custom-model", weight: 10, cost: 0.2, latency: 400 });
    Meridian.save("proxy-router:models", models);
    renderModels();
  };
  document.getElementById("exportBtn").onclick = () => {
    renderCfg();
    Meridian.download("proxy-router-configs.txt", document.getElementById("cfg").textContent);
    Meridian.toast("已导出配置");
  };
  document.getElementById("failover").onchange = () => Meridian.toast("故障转移策略已更新");

  renderModels();
})();
