(() => {
  let library = Meridian.load("agent-factory:library", []);

  function selectedWorkflows() {
    return [...document.querySelectorAll('input[type="checkbox"]:checked')].map((i) => i.value);
  }

  function buildPack() {
    const name = document.getElementById("name").value.trim() || "untitled-pack";
    const workflows = selectedWorkflows();
    const proxy = document.getElementById("proxy").value;
    const pack = {
      id: Meridian.uid("pack"),
      name,
      workflows,
      proxy,
      endpoints: {
        chat: "/v1/chat/completions",
        routePolicy: proxy.includes("router") ? "weighted-failover" : "single-upstream",
      },
      runtime: {
        localFirst: true,
        exports: ["json", "markdown", "nginx", "compose"],
        notes: "将此 Pack 导入团队后，工作流产物默认经反代网关发出。",
      },
      createdAt: new Date().toISOString(),
      links: workflows.map((w) => {
        const map = {
          create: "../products/flow-create.html",
          market: "../products/flow-market.html",
          content: "../products/flow-content.html",
          ops: "../products/flow-ops.html",
          lovara: "../products/lovara.html",
          canvas: "../products/canvas-studio.html",
        };
        return map[w];
      }),
    };
    document.getElementById("preview").textContent = JSON.stringify(pack, null, 2);
    return pack;
  }

  function renderLib() {
    document.getElementById("library").innerHTML = library.length
      ? library
          .map(
            (p) => `<div class="list-item" style="flex-direction:column;align-items:flex-start">
            <strong>${p.name}</strong>
            <span class="muted">${p.workflows.join(" · ")} → ${p.proxy}</span>
            <span class="pill">${new Date(p.createdAt).toLocaleString()}</span>
          </div>`
          )
          .join("")
      : `<p class="muted">尚未安装 Pack</p>`;
  }

  document.getElementById("buildBtn").onclick = () => {
    buildPack();
    Meridian.toast("Pack 已生成预览");
  };
  document.getElementById("installBtn").onclick = () => {
    const pack = buildPack();
    library.unshift(pack);
    library = library.slice(0, 30);
    Meridian.save("agent-factory:library", library);
    renderLib();
    Meridian.toast("已安装到本地库");
  };
  document.getElementById("exportBtn").onclick = () => {
    const pack = buildPack();
    Meridian.download(`${pack.name.replace(/\s+/g, "-").toLowerCase()}.agentpack.json`, JSON.stringify(pack, null, 2), "application/json");
  };

  renderLib();
  buildPack();
})();
