(() => {
  const svg = document.getElementById("artboard");
  let history = Meridian.load("lovara:history", []);
  let current = null;

  const palettes = {
    工业未来: ["#0B1F2A", "#C8F542", "#1F6F78", "#F3F0E7", "#D9773F"],
    编辑杂志: ["#1A1A1A", "#F2EDE4", "#B23A2E", "#C7A27C", "#2F5D50"],
    日系清新: ["#F7F3EA", "#2C6E49", "#F4A261", "#E9C46A", "#264653"],
    Brutalist: ["#111111", "#F5F5F5", "#FF3B00", "#00FF85", "#FFE600"],
  };

  function dims(ratio) {
    if (ratio === "16x9") return { w: 1280, h: 720 };
    if (ratio === "1x1") return { w: 900, h: 900 };
    return { w: 800, h: 1000 };
  }

  function generate() {
    const brief = document.getElementById("brief").value.trim();
    const style = document.getElementById("style").value;
    const ratio = document.getElementById("ratio").value;
    const { w, h } = dims(ratio);
    const rnd = Meridian.seed(brief + style + Date.now() % 1000);
    const colors = palettes[style];
    const title = brief.slice(0, 18) || "MERIDIAN";
    const subtitle = style + " · AI Design Agent";

    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const shapes = [];
    shapes.push(`<rect width="${w}" height="${h}" fill="${colors[0]}"/>`);
    shapes.push(`<circle cx="${w * (0.15 + rnd() * 0.2)}" cy="${h * 0.2}" r="${Math.min(w, h) * (0.12 + rnd() * 0.1)}" fill="${colors[1]}" fill-opacity="0.9"/>`);
    shapes.push(`<rect x="${w * 0.45}" y="${h * 0.12}" width="${w * 0.42}" height="${h * 0.28}" rx="28" fill="${colors[2]}" fill-opacity="0.85"/>`);
    shapes.push(`<path d="M ${w * 0.08} ${h * 0.72} C ${w * 0.3} ${h * 0.55}, ${w * 0.55} ${h * 0.9}, ${w * 0.92} ${h * 0.62}" stroke="${colors[1]}" stroke-width="${8 + rnd() * 10}" fill="none"/>`);
    shapes.push(`<text x="${w * 0.08}" y="${h * 0.58}" fill="${colors[3]}" font-size="${Math.floor(w * 0.08)}" font-family="Bricolage Grotesque, sans-serif" font-weight="800">${title}</text>`);
    shapes.push(`<text x="${w * 0.08}" y="${h * 0.64}" fill="${colors[3]}" fill-opacity="0.85" font-size="${Math.floor(w * 0.028)}" font-family="IBM Plex Sans, sans-serif">${subtitle}</text>`);
    shapes.push(`<text x="${w * 0.08}" y="${h * 0.9}" fill="${colors[4]}" font-size="${Math.floor(w * 0.03)}" font-family="IBM Plex Sans, sans-serif">LOVARA by MERIDIAN</text>`);
    svg.innerHTML = shapes.join("");

    const layers = ["背景底", "光斑", "信息块", "动线", "主标题", "副标题", "品牌锁"];
    current = { brief, style, ratio, colors, layers, svg: svg.innerHTML, at: new Date().toISOString() };
    history.unshift(current);
    history = history.slice(0, 12);
    Meridian.save("lovara:history", history);
    renderMeta();
    Meridian.toast("设计板已生成");
  }

  function renderMeta() {
    if (!current) return;
    document.getElementById("swatches").innerHTML = current.colors
      .map((c) => `<div class="swatch" title="${c}" style="background:${c}"></div>`)
      .join("");
    document.getElementById("layers").innerHTML =
      "<strong>图层</strong><br>" + current.layers.map((l, i) => `${i + 1}. ${l}`).join("<br>");
    document.getElementById("history").innerHTML = history
      .map(
        (h, i) => `<button class="list-item" data-i="${i}" type="button" style="width:100%;text-align:left;cursor:pointer">
        <span>${h.style} · ${h.brief.slice(0, 20)}</span></button>`
      )
      .join("");
  }

  document.getElementById("history").addEventListener("click", (e) => {
    const btn = e.target.closest("[data-i]");
    if (!btn) return;
    current = history[Number(btn.dataset.i)];
    const { w, h } = dims(current.ratio);
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    svg.innerHTML = current.svg;
    renderMeta();
  });

  document.getElementById("genBtn").onclick = generate;
  document.getElementById("exportSvg").onclick = () => {
    if (!current) generate();
    const { w, h } = dims(current.ratio);
    const out = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}">${current.svg}</svg>`;
    Meridian.download("lovara-board.svg", out, "image/svg+xml");
  };
  document.getElementById("exportJson").onclick = () => {
    if (!current) generate();
    Meridian.download("lovara-board.json", JSON.stringify(current, null, 2), "application/json");
  };

  if (history[0]) {
    current = history[0];
    const { w, h } = dims(current.ratio);
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    svg.innerHTML = current.svg;
    renderMeta();
  }
})();
