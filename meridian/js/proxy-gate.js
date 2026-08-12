(() => {
  let providers = Meridian.load("proxy-gate:providers", [
    { id: "p1", name: "OpenAI", base: "https://api.openai.com", key: "" },
    { id: "p2", name: "DeepSeek", base: "https://api.deepseek.com", key: "" },
    { id: "p3", name: "Custom", base: "https://llm.example.com", key: "" },
  ]);

  const provEl = document.getElementById("providers");
  const preview = document.getElementById("preview");

  function mask(k) {
    if (!k) return "(未设置)";
    return k.slice(0, 3) + "••••" + k.slice(-4);
  }

  function renderProviders() {
    provEl.innerHTML = providers
      .map(
        (p) => `<div class="list-item" style="flex-direction:column;align-items:stretch;gap:.4rem">
        <strong>${p.name}</strong>
        <input data-base="${p.id}" value="${p.base}" />
        <input data-key="${p.id}" type="password" placeholder="上游 API Key" value="${p.key || ""}" />
        <span class="muted">显示：${mask(p.key)}</span>
      </div>`
      )
      .join("");
    document.getElementById("routes").innerHTML = providers
      .map((p) => `<div class="list-item"><span>${document.getElementById("path").value}</span><span class="pill">→ ${p.name}</span></div>`)
      .join("");
  }

  provEl.addEventListener("input", (e) => {
    const t = e.target;
    const p = providers.find((x) => x.id === (t.dataset.base || t.dataset.key));
    if (!p) return;
    if (t.dataset.base) p.base = t.value;
    if (t.dataset.key) p.key = t.value;
    Meridian.save("proxy-gate:providers", providers);
    renderProviders();
  });

  document.getElementById("addProvider").onclick = () => {
    providers.push({ id: Meridian.uid("p"), name: "Custom", base: "https://example.com", key: "" });
    Meridian.save("proxy-gate:providers", providers);
    renderProviders();
  };

  function configs() {
    const path = document.getElementById("path").value.trim();
    const rpm = document.getElementById("rpm").value;
    const allow = document.getElementById("allow").value;
    const primary = providers[0];
    const nginx = `limit_req_zone $binary_remote_addr zone=ai:10m rate=${rpm}r/m;\n\nserver {\n  listen 8080;\n  server_name ai-gateway.local;\n\n  location ${path} {\n    allow ${allow.split(",")[0].trim()};\n    deny all;\n    limit_req zone=ai burst=20 nodelay;\n    proxy_set_header Authorization "Bearer \${UPSTREAM_KEY}";\n    proxy_pass ${primary.base}${path};\n  }\n}`;
    const compose = `services:\n  meridian-proxy-gate:\n    image: nginx:1.27-alpine\n    ports:\n      - "8080:8080"\n    environment:\n      UPSTREAM_KEY: "replace-me"\n    volumes:\n      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro\n`;
    return { nginx, compose, path, rpm, allow };
  }

  function refreshPreview() {
    const c = configs();
    preview.textContent = `# nginx.conf\n${c.nginx}\n\n# docker-compose.yml\n${c.compose}`;
  }

  document.getElementById("path").oninput = () => {
    renderProviders();
    refreshPreview();
  };
  document.getElementById("rpm").oninput = refreshPreview;
  document.getElementById("allow").oninput = refreshPreview;

  document.getElementById("simBtn").onclick = () => {
    const rnd = Meridian.seed(Date.now());
    const lines = Array.from({ length: 5 }, (_, i) => {
      const p = providers[Math.floor(rnd() * providers.length)];
      const code = rnd() > 0.15 ? 200 : 429;
      return `${new Date().toISOString()}  POST ${document.getElementById("path").value}  → ${p.name}  ${code}  ${Math.floor(80 + rnd() * 700)}ms`;
    });
    document.getElementById("logs").textContent = lines.join("\n");
  };

  document.getElementById("exportBtn").onclick = () => {
    const c = configs();
    const gateKey = document.getElementById("gateKey").value;
    Meridian.save("proxy-gate:meta", { gateKey: gateKey ? "set" : "", rpm: c.rpm, allow: c.allow });
    Meridian.download("nginx.conf", c.nginx);
    setTimeout(() => Meridian.download("docker-compose.yml", c.compose), 200);
    Meridian.toast("已导出 Nginx + Compose");
    refreshPreview();
  };

  renderProviders();
  refreshPreview();
})();
