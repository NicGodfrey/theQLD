(() => {
  const tabs = document.getElementById("tabs");
  tabs.addEventListener("click", (e) => {
    const btn = e.target.closest("button[data-tab]");
    if (!btn) return;
    tabs.querySelectorAll("button").forEach((b) => b.classList.toggle("active", b === btn));
    document.querySelectorAll(".tabpane").forEach((p) => p.classList.toggle("active", p.id === btn.dataset.tab));
  });

  let pack = Meridian.load("flow-content:last", null);

  function generate() {
    const topic = document.getElementById("topic").value.trim();
    const keyword = document.getElementById("keyword").value.trim();
    const words = Number(document.getElementById("words").value || 1000);
    const rnd = Meridian.seed(topic + keyword);

    const outline = [
      `# 大纲 · ${topic}`,
      `1. 开场冲突：团队在多模型账单上踩坑`,
      `2. 概念澄清：什么是真正的「${keyword}」`,
      `3. 架构图：客户端 → 网关 → 上游模型`,
      `4. 成本打法：缓存 / 路由 / 降级`,
      `5. 落地清单：一周内可上线的最小网关`,
      `6. 结尾 CTA：试用 MERIDIAN Proxy Gate`,
    ].join("\n");

    const paras = [];
    let count = 0;
    const seeds = [
      `很多人把「${keyword}」理解成简单转发，其实关键在路由策略与可观测性。`,
      `围绕「${topic}」，先把流量按延迟与价格分层，再谈模型效果。`,
      `实践里，失败重试如果没有幂等键，会把成本放大数倍。`,
      `把热门提示词结果短缓存 30–120 秒，往往比换更贵模型更划算。`,
      `对内提供 OpenAI 兼容接口，对外屏蔽上游差异，是团队协作的分水岭。`,
    ];
    while (count < words) {
      const s = seeds[Math.floor(rnd() * seeds.length)] + " ";
      paras.push(s);
      count += s.length;
    }
    const longform = `# ${topic}\n\n${paras.join("\n\n")}`;

    const social = [
      `# 社交切片`,
      `小红书：三张图讲清 ${keyword} —— 省钱、稳定、可切换。`,
      `抖音口播：开头 3 秒甩账单截图，再给出网关架构一句话。`,
      `Twitter/X：Thread 5 条，拆解路由权重与故障转移。`,
      `Email：主题「把模型账单砍半的清单」，正文给 3 个检查项。`,
    ].join("\n");

    const seo = [
      `# SEO Meta`,
      `Title: ${topic}｜${keyword}实战指南`,
      `Description: 面向增长与工程团队的${keyword}落地方法，覆盖路由、缓存与成本控制。`,
      `Slug: ai-proxy-gateway-cost-guide`,
      `H2 建议: 架构 / 路由策略 / 观测指标 / 上线清单`,
      `内链: Proxy Gate, Proxy Router, Agent Factory`,
    ].join("\n");

    pack = { topic, keyword, outline, longform, social, seo };
    const dens = ((longform.split(keyword).length - 1) / Math.max(longform.length / keyword.length, 1)) * 100;
    document.getElementById("density").textContent = `「${keyword}」约出现 ${longform.split(keyword).length - 1} 次；粗密度 ${(dens).toFixed(2)}%（仅供参考）`;
    document.getElementById("out-outline").textContent = outline;
    document.getElementById("out-longform").textContent = longform;
    document.getElementById("out-social").textContent = social;
    document.getElementById("out-seo").textContent = seo;
    Meridian.save("flow-content:last", pack);
    Meridian.toast("内容包已生成");
  }

  document.getElementById("genBtn").onclick = generate;
  document.getElementById("saveBtn").onclick = () => {
    if (!pack) generate();
    Meridian.toast("已保存到本地");
  };
  document.getElementById("exportBtn").onclick = async () => {
    if (!pack) generate();
    // sequential downloads as lightweight multi-file export
    Meridian.download("01-outline.md", pack.outline, "text/markdown");
    setTimeout(() => Meridian.download("02-longform.md", pack.longform, "text/markdown"), 200);
    setTimeout(() => Meridian.download("03-social.md", pack.social, "text/markdown"), 400);
    setTimeout(() => Meridian.download("04-seo.md", pack.seo, "text/markdown"), 600);
    Meridian.toast("已导出 4 个 Markdown");
  };

  if (pack) {
    document.getElementById("topic").value = pack.topic;
    document.getElementById("keyword").value = pack.keyword;
    document.getElementById("out-outline").textContent = pack.outline;
    document.getElementById("out-longform").textContent = pack.longform;
    document.getElementById("out-social").textContent = pack.social;
    document.getElementById("out-seo").textContent = pack.seo;
  }
})();
