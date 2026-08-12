(() => {
  const svg = document.getElementById("board");
  let state = Meridian.load("canvas-studio", {
    nodes: [
      { id: "n1", type: "brand", x: 80, y: 80, text: "MERIDIAN · 酸绿工程美学" },
      { id: "n2", type: "style", x: 360, y: 120, text: "工业未来 / 宽字距海报" },
      { id: "n3", type: "image", x: 640, y: 200, text: "反代网关控制台的英雄视觉，夜光线路" },
    ],
    edges: [{ from: "n1", to: "n2" }, { from: "n2", to: "n3" }],
  });
  let selected = [];
  let drag = null;

  const colors = { image: "#1F6F78", style: "#D9773F", copy: "#0B1F2A", brand: "#6B8F2A" };

  function render() {
    const edgeLines = state.edges
      .map((e) => {
        const a = state.nodes.find((n) => n.id === e.from);
        const b = state.nodes.find((n) => n.id === e.to);
        if (!a || !b) return "";
        return `<line x1="${a.x + 90}" y1="${a.y + 36}" x2="${b.x}" y2="${b.y + 36}" stroke="#0B1F2A" stroke-opacity="0.35" stroke-width="3"/>`;
      })
      .join("");
    const nodes = state.nodes
      .map((n) => {
        const active = selected.includes(n.id);
        return `<g class="node" data-id="${n.id}" transform="translate(${n.x},${n.y})" style="cursor:grab">
          <rect width="180" height="72" rx="14" fill="${colors[n.type] || "#0B1F2A"}" fill-opacity="${active ? 1 : 0.88}" stroke="${active ? "#C8F542" : "transparent"}" stroke-width="4"/>
          <text x="14" y="28" fill="#F3F0E7" font-size="12" font-family="IBM Plex Sans">${n.type.toUpperCase()}</text>
          <text x="14" y="50" fill="#F3F0E7" font-size="13" font-family="IBM Plex Sans">${(n.text || "").slice(0, 16)}</text>
        </g>`;
      })
      .join("");
    svg.innerHTML = edgeLines + nodes;
  }

  function nodeAt(id) {
    return state.nodes.find((n) => n.id === id);
  }

  svg.addEventListener("pointerdown", (e) => {
    const g = e.target.closest("g.node");
    if (!g) return;
    const id = g.dataset.id;
    if (!selected.includes(id)) {
      selected = e.shiftKey ? selected.concat(id).slice(-2) : [id];
    }
    document.getElementById("editor").value = nodeAt(id).text;
    drag = { id, ox: e.clientX, oy: e.clientY, x: nodeAt(id).x, y: nodeAt(id).y };
    svg.setPointerCapture(e.pointerId);
    render();
  });
  svg.addEventListener("pointermove", (e) => {
    if (!drag) return;
    const n = nodeAt(drag.id);
    n.x = Math.max(0, drag.x + (e.clientX - drag.ox) * 1.2);
    n.y = Math.max(0, drag.y + (e.clientY - drag.oy) * 1.2);
    render();
  });
  svg.addEventListener("pointerup", () => {
    drag = null;
    Meridian.save("canvas-studio", state);
  });

  document.getElementById("editor").oninput = (e) => {
    if (selected[0]) {
      nodeAt(selected[0]).text = e.target.value;
      Meridian.save("canvas-studio", state);
      render();
    }
  };

  document.querySelectorAll("[data-type]").forEach((btn) => {
    btn.onclick = () => {
      const type = btn.dataset.type;
      const defaults = { image: "新的图像提示", style: "新风格关键词", copy: "主文案", brand: "品牌约束" };
      state.nodes.push({ id: Meridian.uid("n"), type, x: 120 + state.nodes.length * 30, y: 80 + state.nodes.length * 20, text: defaults[type] });
      Meridian.save("canvas-studio", state);
      render();
    };
  });

  document.getElementById("linkBtn").onclick = () => {
    if (selected.length < 2) return Meridian.toast("请先选两个节点（Shift 点选）");
    const [from, to] = selected;
    if (!state.edges.some((e) => e.from === from && e.to === to)) state.edges.push({ from, to });
    Meridian.save("canvas-studio", state);
    render();
    Meridian.toast("已连接");
  };

  document.getElementById("exportBtn").onclick = () => {
    const pack = {
      nodes: state.nodes,
      edges: state.edges,
      prompts: state.nodes.map((n) => `[${n.type}] ${n.text}`),
      combined: state.nodes.map((n) => n.text).join("；"),
    };
    Meridian.download("prompt-pack.json", JSON.stringify(pack, null, 2), "application/json");
    Meridian.download("prompt-pack.txt", pack.combined);
  };

  render();
})();
