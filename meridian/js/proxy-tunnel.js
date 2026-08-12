(() => {
  function generate() {
    const port = document.getElementById("local").value;
    const mode = document.getElementById("mode").value;
    const domain = document.getElementById("domain").value.trim();
    const token = document.getElementById("token").value.trim();
    const only = document.getElementById("only").value.trim();

    let config = "";
    if (mode === "cloudflare") {
      config = `# cloudflared config.yml\ntunnel: ${token}\ningress:\n  - hostname: ${domain}\n    path: ${only}\n    service: http://127.0.0.1:${port}\n  - service: http_status:404\n\n# run\ncloudflared tunnel run --token ${token}`;
    } else if (mode === "frp") {
      config = `# frpc.toml\nserverAddr = "frps.example.com"\nserverPort = 7000\n\n[[proxies]]\nname = "ollama"\ntype = "http"\nlocalIP = "127.0.0.1"\nlocalPort = ${port}\ncustomDomains = ["${domain}"]\n\n# put auth token in server\n# meta token = ${token}`;
    } else {
      config = `# nginx stream/http reverse for local AI\nserver {\n  listen 443 ssl;\n  server_name ${domain};\n  location ${only.replace("*", "")} {\n    proxy_pass http://127.0.0.1:${port};\n    proxy_set_header Authorization "Bearer ${token}";\n  }\n}`;
    }

    const checks = [
      "本地服务仅监听 127.0.0.1",
      "公网必须鉴权（Token / mTLS / IP allowlist）",
      "关闭模型管理接口对外暴露",
      "开启访问日志与速率限制",
      "用 Proxy Gate 再包一层统一对外 API",
    ];

    document.getElementById("config").textContent = config;
    document.getElementById("checklist").innerHTML = checks
      .map((c, i) => `<label class="list-item" style="justify-content:flex-start;gap:.6rem"><input type="checkbox" ${i < 2 ? "checked" : ""}/> ${c}</label>`)
      .join("");
    Meridian.save("proxy-tunnel:last", { port, mode, domain, token, only, config });
    Meridian.toast("隧道方案已生成");
  }

  document.getElementById("genBtn").onclick = generate;
  document.getElementById("exportBtn").onclick = () => {
    if (!document.getElementById("config").textContent.includes("server") && !document.getElementById("config").textContent.includes("tunnel")) generate();
    Meridian.download("proxy-tunnel.txt", document.getElementById("config").textContent);
  };

  const last = Meridian.load("proxy-tunnel:last", null);
  if (last) {
    document.getElementById("local").value = last.port;
    document.getElementById("mode").value = last.mode;
    document.getElementById("domain").value = last.domain;
    document.getElementById("token").value = last.token;
    document.getElementById("only").value = last.only;
    document.getElementById("config").textContent = last.config;
  }
})();
