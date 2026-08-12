(() => {
  const channelNames = ["小红书", "抖音", "Twitter/X", "Email", "SEO/博客"];
  let selected = Meridian.load("flow-market:channels", ["小红书", "Email", "SEO/博客"]);
  let lastPlan = Meridian.load("flow-market:last", null);

  const chEl = document.getElementById("channels");
  chEl.innerHTML = channelNames
    .map(
      (c) => `<label class="list-item" style="justify-content:flex-start;gap:.6rem;cursor:pointer">
      <input type="checkbox" value="${c}" ${selected.includes(c) ? "checked" : ""} /> ${c}
    </label>`
    )
    .join("");

  function collectChannels() {
    selected = [...chEl.querySelectorAll("input:checked")].map((i) => i.value);
    return selected;
  }

  function build() {
    const goal = document.getElementById("goal").value.trim();
    const audience = document.getElementById("audience").value.trim();
    const budget = Number(document.getElementById("budget").value || 0);
    const channels = collectChannels();
    const rnd = Meridian.seed(goal + channels.join());
    const per = channels.length ? Math.round(budget / channels.length) : 0;
    const days = Array.from({ length: 7 }, (_, i) => {
      const ch = channels[i % Math.max(channels.length, 1)] || "Email";
      const hooks = ["反常识数据", "前后对比", "用户原声", "限时权益", "拆解教程"];
      return {
        day: `D${i + 1}`,
        channel: ch,
        hook: hooks[Math.floor(rnd() * hooks.length)],
        title: `${goal.slice(0, 12)}｜${ch}触点 ${i + 1}`,
        cta: i % 2 ? "领取试用" : "预约演示",
        variantA: "利益点前置",
        variantB: "故事感开场",
        kpi: i < 3 ? "CTR" : i < 5 ? "激活率" : "付费转化",
        spend: Math.round(per * (0.7 + rnd() * 0.6)),
      };
    });

    lastPlan = { goal, audience, budget, channels, days, kpis: ["CAC", "激活率", "7日留存", "试用→付费"] };
    Meridian.save("flow-market:last", lastPlan);
    Meridian.save("flow-market:channels", channels);
    render();
    Meridian.toast("战役已生成");
  }

  function render() {
    if (!lastPlan) return;
    document.getElementById("plan").textContent = [
      `# ${lastPlan.goal}`,
      `受众：${lastPlan.audience}`,
      `预算：¥${lastPlan.budget}｜渠道：${lastPlan.channels.join("、")}`,
      `核心 KPI：${lastPlan.kpis.join(" · ")}`,
      "",
      "投放原则：前 3 天测钩子，中 2 天放量，后 2 天收割。",
      "A/B：标题利益点 vs 叙事开场；每日保留胜出变体。",
    ].join("\n");
    document.getElementById("calendar").innerHTML = lastPlan.days
      .map(
        (d) => `<div class="list-item" style="flex-direction:column;align-items:flex-start">
        <strong>${d.day} · ${d.channel}</strong>
        <span>${d.title}</span>
        <span class="muted">钩子：${d.hook}｜CTA：${d.cta}｜KPI：${d.kpi}｜¥${d.spend}</span>
        <span class="pill">A: ${d.variantA}</span> <span class="pill">B: ${d.variantB}</span>
      </div>`
      )
      .join("");
  }

  document.getElementById("genBtn").onclick = build;
  document.getElementById("saveBtn").onclick = () => {
    if (!lastPlan) build();
    const lib = Meridian.load("flow-market:library", []);
    lib.unshift({ ...lastPlan, savedAt: new Date().toISOString() });
    Meridian.save("flow-market:library", lib.slice(0, 20));
    Meridian.toast("战役已保存");
  };
  document.getElementById("exportJson").onclick = () => {
    if (!lastPlan) build();
    Meridian.download("flow-market.json", JSON.stringify(lastPlan, null, 2), "application/json");
  };
  document.getElementById("exportCsv").onclick = () => {
    if (!lastPlan) build();
    const header = "day,channel,title,hook,cta,kpi,spend,variantA,variantB";
    const rows = lastPlan.days.map((d) =>
      [d.day, d.channel, d.title, d.hook, d.cta, d.kpi, d.spend, d.variantA, d.variantB]
        .map((x) => `"${String(x).replace(/"/g, '""')}"`)
        .join(",")
    );
    Meridian.download("flow-market.csv", [header, ...rows].join("\n"), "text/csv");
  };

  render();
})();
