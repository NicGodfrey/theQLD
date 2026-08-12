(() => {
  let pack = null;

  function build() {
    const product = document.getElementById("product").value.trim();
    const north = document.getElementById("north").value.trim();
    const target = Number(document.getElementById("target").value || 30);
    const stage = document.getElementById("stage").value;
    const rnd = Meridian.seed(product + stage + target);

    const sequences = {
      acquire: ["欢迎引导：1 分钟创建第一条路由", "案例邮件：省下 37% 模型账单", "社群邀请：架构答疑直播"],
      activate: ["清单：打通第一个上游", "卡点救援：密钥与 CORS 排查", "成功庆祝：分享第一张流量图"],
      retain: ["周报：成本与延迟", "沉睡唤醒：7 日无请求提醒", "新能力预告：故障转移"],
      expand: ["升级席位：团队协作审计日志", "加购 Router 模块", "行业模板包"],
      refer: ["邀请得积分", "成功故事共创", "代理伙伴计划"],
    };

    const seq = (sequences[stage] || sequences.activate).map((title, i) => ({
      day: `T+${i * 2}`,
      title,
      channel: i % 2 ? "站内" : "Email",
      segment: i === 0 ? "新注册" : i === 1 ? "已创建路由未跑通" : "已产生请求",
    }));

    const health = {
      weights: [
        { name: "激活完成", w: 30 },
        { name: "周请求量", w: 25 },
        { name: "错误率倒挂", w: 20 },
        { name: "邀请行为", w: 15 },
        { name: "付费意向", w: 10 },
      ],
      formula: "score = Σ(指标归一化 × 权重)",
    };

    const retention = Array.from({ length: 7 }, (_, i) => {
      const base = target + 18 - i * (3 + rnd() * 2);
      return Math.max(8, Math.round(base + (rnd() - 0.5) * 6));
    });

    pack = { product, north, target, stage, seq, health, retention };
    Meridian.save("flow-ops:last", pack);
    render();
    Meridian.toast("运营剧本已生成");
  }

  function render() {
    if (!pack) return;
    document.getElementById("seq").innerHTML = pack.seq
      .map(
        (s) => `<div class="list-item" style="flex-direction:column;align-items:flex-start">
        <strong>${s.day} · ${s.channel}</strong>
        <span>${s.title}</span>
        <span class="muted">分群：${s.segment}</span>
      </div>`
      )
      .join("");
    document.getElementById("health").textContent = pack.health.weights
      .map((h) => `${h.name}: ${h.w}`)
      .concat([`公式：${pack.health.formula}`, `北极星：${pack.north}`])
      .join("\n");
    document.getElementById("bars").innerHTML = pack.retention
      .map(
        (v, i) => `<div class="bar-row"><span>D${i + 1}</span><div class="bar"><i style="width:${v}%"></i></div><span>${v}%</span></div>`
      )
      .join("");
    document.getElementById("playbook").textContent = [
      `# ${pack.product} 用户运营剧本`,
      `阶段：${pack.stage}`,
      `目标 D7 留存：${pack.target}%`,
      "",
      ...pack.seq.map((s) => `- ${s.day} [${s.channel}] ${s.title} （${s.segment}）`),
    ].join("\n");
  }

  document.getElementById("buildBtn").onclick = build;
  document.getElementById("exportMd").onclick = () => {
    if (!pack) build();
    Meridian.download("flow-ops.md", document.getElementById("playbook").textContent, "text/markdown");
  };
  document.getElementById("exportJson").onclick = () => {
    if (!pack) build();
    Meridian.download("flow-ops.json", JSON.stringify(pack, null, 2), "application/json");
  };

  pack = Meridian.load("flow-ops:last", null);
  if (pack) render();
})();
