/* MERIDIAN · Flow Ops — AI 用户运营工作流
   生命周期五阶段（获取→激活→留存→增购→推荐）：Drip 序列、分群规则、
   健康分五因子模型、队列留存 Canvas 模拟，Playbook JSON/MD 导出。 */
(function () {
  'use strict';

  /* ---------- helpers ---------- */
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.prototype.slice.call((r || document).querySelectorAll(s));
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  function hashStr(s) {
    let h = 2166136261;
    for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); }
    return h >>> 0;
  }
  function mulberry(seed) {
    return function () {
      seed |= 0; seed = seed + 0x6D2B79F5 | 0;
      let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }
  function download(filename, content, mime) {
    const blob = new Blob([content], { type: (mime || 'text/plain') + ';charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = filename;
    document.body.appendChild(a); a.click();
    setTimeout(() => { URL.revokeObjectURL(url); a.remove(); }, 400);
  }
  function toast(msg) {
    let t = $('.toast');
    if (!t) { t = document.createElement('div'); t.className = 'toast'; document.body.appendChild(t); }
    t.textContent = msg; t.classList.add('show');
    clearTimeout(toast._t); toast._t = setTimeout(() => t.classList.remove('show'), 2400);
  }

  /* ---------- domain ---------- */
  const LS_CURRENT = 'meridian.flow-ops.current.v1';
  const LS_SAVES = 'meridian.flow-ops.saves.v1';

  const STAGE_DEFS = [
    { id: 'acquire', cn: '获取', en: 'Acquire' },
    { id: 'activate', cn: '激活', en: 'Activate' },
    { id: 'retain', cn: '留存', en: 'Retain' },
    { id: 'expand', cn: '增购', en: 'Expand' },
    { id: 'refer', cn: '推荐', en: 'Refer' }
  ];
  const CHANNELS = ['邮件', '短信', '微信', '站内信', 'Push'];
  const RULE_FIELDS = ['注册天数', '月登录天数', '核心功能使用次数', 'NPS 评分', '付费计划', '团队人数'];
  const RULE_OPS = ['>', '<', '=', '≥', '≤', '包含'];

  function defaultStage(id) {
    const presets = {
      acquire: {
        goal: '把渠道流量转化为注册用户', metric: '周新增注册数',
        seq: [
          { day: 0, channel: '邮件', title: '欢迎加入 {{product}}', body: 'Hi {{name}}，欢迎！这是 3 分钟快速上手指南，完成第一步即可解锁模板库。' },
          { day: 1, channel: 'Push', title: '你的工作台已就绪', body: '{{name}}，昨天的注册还差最后一步——创建你的第一个项目，只需 2 分钟。' }
        ],
        rules: [{ field: '注册天数', op: '≤', value: '3' }]
      },
      activate: {
        goal: '让新用户完成关键动作（Aha Moment）', metric: '7 日激活率',
        seq: [
          { day: 0, channel: '站内信', title: '完成你的第一条工作流', body: '{{name}}，用示例模板 10 分钟跑通第一条流水线，体验 {{product}} 的核心价值。' },
          { day: 2, channel: '邮件', title: '还差一步就能看到效果', body: '数据显示完成首次运行的用户，30 天留存高 2.4 倍。这是你的专属快捷入口。' },
          { day: 5, channel: '微信', title: '1 对 1 上手协助', body: '{{name}}，如果卡在配置环节，回复「帮助」预约 15 分钟人工协助。' }
        ],
        rules: [{ field: '注册天数', op: '≤', value: '7' }, { field: '核心功能使用次数', op: '<', value: '1' }]
      },
      retain: {
        goal: '维持活跃频率，防止静默流失', metric: '周活跃留存率',
        seq: [
          { day: 0, channel: '邮件', title: '本周你错过的 3 个更新', body: '{{name}}，你关注的模板库新增了 3 个高分模板，点击查看。' },
          { day: 7, channel: 'Push', title: '你的工作流在想你', body: '已经 7 天没有运行了，你上次的项目还差最后一步导出。' }
        ],
        rules: [{ field: '月登录天数', op: '<', value: '4' }]
      },
      expand: {
        goal: '推动付费升级与席位扩展', metric: '月增购收入 (Expansion MRR)',
        seq: [
          { day: 0, channel: '邮件', title: '你已用满免费额度的 80%', body: '{{name}}，本月运行次数即将达到上限。升级 Pro 解锁无限运行 + 团队协作。' },
          { day: 3, channel: '站内信', title: '给团队的专属方案', body: '3 人以上团队可享席位折扣，账单页一键升级。' }
        ],
        rules: [{ field: '付费计划', op: '=', value: 'Free' }, { field: '核心功能使用次数', op: '>', value: '20' }]
      },
      refer: {
        goal: '把满意用户变成增长渠道', metric: '月推荐注册数 (K-factor)',
        seq: [
          { day: 0, channel: '邮件', title: '送你和朋友各一个月 Pro', body: '{{name}}，邀请 1 位朋友注册，你们各得 30 天 Pro。你的专属链接在此。' },
          { day: 14, channel: '站内信', title: '你的邀请还剩 2 个名额', body: '本月邀请名额即将重置，别浪费你的 Pro 奖励。' }
        ],
        rules: [{ field: 'NPS 评分', op: '≥', value: '9' }]
      }
    };
    return JSON.parse(JSON.stringify(presets[id]));
  }
  function defaultState() {
    const stages = {};
    STAGE_DEFS.forEach(s => { stages[s.id] = defaultStage(s.id); });
    return {
      name: '默认 Playbook',
      product: 'Meridian',
      stages: stages,
      sim: { act: 62, churn: 14, lift: 20 }
    };
  }

  let state;
  try { state = JSON.parse(localStorage.getItem(LS_CURRENT)) || defaultState(); }
  catch (e) { state = defaultState(); }
  if (!state.stages) state = defaultState();
  let activeStage = 'activate';

  function persist() { try { localStorage.setItem(LS_CURRENT, JSON.stringify(state)); } catch (e) { } }
  function loadSaves() { try { return JSON.parse(localStorage.getItem(LS_SAVES)) || {}; } catch (e) { return {}; } }
  function writeSaves(s) { try { localStorage.setItem(LS_SAVES, JSON.stringify(s)); } catch (e) { } }

  /* ---------- stage pipeline ---------- */
  function renderStages() {
    $('#stages').innerHTML = STAGE_DEFS.map(s => `
      <button class="stage ${s.id === activeStage ? 'active' : ''}" data-stage="${s.id}">
        ${s.cn}<small>${s.en}</small>
      </button>`).join('');
    const st = state.stages[activeStage];
    $('#stGoal').value = st.goal || '';
    $('#stMetric').value = st.metric || '';
    const def = STAGE_DEFS.find(d => d.id === activeStage);
    $('#dripTitle').textContent = def.cn + '阶段 · Drip 序列';
    $('#segTitle').textContent = def.cn + '阶段 · 进入条件';
    if (st.logic) $('#segLogic').value = st.logic;
  }
  $('#stages').addEventListener('click', e => {
    const btn = e.target.closest('[data-stage]'); if (!btn) return;
    activeStage = btn.dataset.stage;
    renderStages(); renderDrip(); renderRules();
  });
  $('#stGoal').addEventListener('input', e => { state.stages[activeStage].goal = e.target.value; persist(); });
  $('#stMetric').addEventListener('input', e => { state.stages[activeStage].metric = e.target.value; persist(); });

  /* ---------- drip sequences ---------- */
  function renderDrip() {
    const seq = state.stages[activeStage].seq;
    $('#dripList').innerHTML = seq.length ? seq.map((m, i) => `
      <div class="subpanel stack" data-i="${i}" style="gap:10px">
        <div class="row">
          <span class="badge-num">${i + 1}</span>
          <div class="field" style="width:86px">
            <label>Day</label>
            <input type="number" min="0" max="90" value="${m.day}" data-k="day">
          </div>
          <div class="field" style="width:110px">
            <label>渠道</label>
            <select data-k="channel">${CHANNELS.map(c => '<option' + (c === m.channel ? ' selected' : '') + '>' + c + '</option>').join('')}</select>
          </div>
          <div class="field grow">
            <label>标题</label>
            <input type="text" value="${esc(m.title)}" data-k="title">
          </div>
          <span class="row" style="align-self:end">
            <button class="btn-icon btn" data-act="up" ${i === 0 ? 'disabled' : ''}>↑</button>
            <button class="btn-icon btn" data-act="down" ${i === seq.length - 1 ? 'disabled' : ''}>↓</button>
            <button class="btn-icon btn" data-act="del">✕</button>
          </span>
        </div>
        <div class="field">
          <label>内容模板</label>
          <textarea class="code" rows="2" data-k="body">${esc(m.body)}</textarea>
        </div>
      </div>`).join('') : '<p class="small muted mb-0">此阶段还没有消息，点「＋ 添加消息」。</p>';
  }
  $('#dripList').addEventListener('input', e => {
    const wrap = e.target.closest('[data-i]'); if (!wrap) return;
    const m = state.stages[activeStage].seq[Number(wrap.dataset.i)]; if (!m) return;
    const k = e.target.dataset.k; if (!k) return;
    m[k] = k === 'day' ? Math.max(0, Number(e.target.value) || 0) : e.target.value;
    persist();
  });
  $('#dripList').addEventListener('click', e => {
    const btn = e.target.closest('[data-act]'); if (!btn) return;
    const i = Number(btn.closest('[data-i]').dataset.i);
    const seq = state.stages[activeStage].seq;
    const act = btn.dataset.act;
    if (act === 'del') seq.splice(i, 1);
    if (act === 'up' && i > 0) { const t = seq[i - 1]; seq[i - 1] = seq[i]; seq[i] = t; }
    if (act === 'down' && i < seq.length - 1) { const t = seq[i + 1]; seq[i + 1] = seq[i]; seq[i] = t; }
    persist(); renderDrip();
  });
  $('#addMsg').addEventListener('click', () => {
    const seq = state.stages[activeStage].seq;
    const lastDay = seq.length ? seq[seq.length - 1].day : 0;
    seq.push({ day: lastDay + 2, channel: '邮件', title: '新消息标题', body: 'Hi {{name}}，……' });
    persist(); renderDrip();
  });
  $('#previewDrip').addEventListener('click', () => {
    const seq = state.stages[activeStage].seq;
    const pre = $('#dripPreview');
    if (!seq.length) { toast('此阶段还没有消息'); return; }
    const m = seq[0];
    const fill = s => String(s).replace(/\{\{\s*name\s*\}\}/g, '林小满').replace(/\{\{\s*product\s*\}\}/g, state.product || 'Meridian');
    pre.style.display = 'block';
    pre.textContent = '[Day ' + m.day + ' · ' + m.channel + ']\n标题：' + fill(m.title) + '\n\n' + fill(m.body);
  });

  /* ---------- segment rules ---------- */
  function renderRules() {
    const st = state.stages[activeStage];
    $('#ruleList').innerHTML = st.rules.length ? st.rules.map((r, i) => `
      <div class="row" data-i="${i}">
        <select data-k="field" style="max-width:170px">${RULE_FIELDS.map(f => '<option' + (f === r.field ? ' selected' : '') + '>' + f + '</option>').join('')}</select>
        <select data-k="op" style="width:86px">${RULE_OPS.map(o => '<option' + (o === r.op ? ' selected' : '') + '>' + o + '</option>').join('')}</select>
        <input type="text" data-k="value" value="${esc(r.value)}" placeholder="值" class="grow" style="max-width:140px">
        <button class="btn-icon btn" data-act="del">✕</button>
      </div>`).join('') : '<p class="small muted mb-0">没有规则 = 面向该阶段全部用户。</p>';
    updateCoverage();
  }
  function updateCoverage() {
    const st = state.stages[activeStage];
    if (!st.rules.length) { $('#segCover').textContent = '100%'; return; }
    // 确定性估算：由规则内容哈希导出稳定覆盖率
    const h = hashStr(activeStage + '|' + ($('#segLogic').value || 'AND') + '|' + JSON.stringify(st.rules));
    const base = 18 + (h % 55);
    const cover = ($('#segLogic').value === 'OR') ? Math.min(96, base + 22) : base;
    $('#segCover').textContent = '≈ ' + cover + '%';
  }
  $('#ruleList').addEventListener('input', e => {
    const wrap = e.target.closest('[data-i]'); if (!wrap) return;
    const r = state.stages[activeStage].rules[Number(wrap.dataset.i)]; if (!r) return;
    const k = e.target.dataset.k; if (!k) return;
    r[k] = e.target.value; persist(); updateCoverage();
  });
  $('#ruleList').addEventListener('click', e => {
    const btn = e.target.closest('[data-act="del"]'); if (!btn) return;
    state.stages[activeStage].rules.splice(Number(btn.closest('[data-i]').dataset.i), 1);
    persist(); renderRules();
  });
  $('#addRule').addEventListener('click', () => {
    state.stages[activeStage].rules.push({ field: RULE_FIELDS[0], op: '>', value: '' });
    persist(); renderRules();
  });
  $('#segLogic').addEventListener('change', e => {
    state.stages[activeStage].logic = e.target.value;
    persist(); updateCoverage();
  });

  /* ---------- health score ---------- */
  const H = { login: '#hLogin', adopt: '#hAdopt', nps: '#hNps', ticket: '#hTicket' };
  function calcHealth() {
    const login = Number($(H.login).value);
    const adopt = Number($(H.adopt).value);
    const nps = Number($(H.nps).value);
    const ticket = Number($(H.ticket).value);
    const pay = $('#hPay').value;

    $('#hLoginV').textContent = login + ' 天';
    $('#hAdoptV').textContent = adopt + '%';
    $('#hNpsV').textContent = nps + ' 分';
    $('#hTicketV').textContent = ticket + ' 单';

    let score = (login / 30) * 30 + (adopt / 100) * 30 + (nps / 10) * 25 - Math.min(15, ticket * 2.5);
    if (pay === 'overdue') score -= 15;
    if (pay === 'churned') score -= 40;
    score = Math.max(0, Math.min(100, Math.round(score)));

    const bands = [
      { min: 75, label: '健康 Healthy', cls: '', chip: 'chip acid', advice: '适合推进「增购」与「推荐」序列：发送升级方案或邀请奖励，趁体验高点扩大价值。' },
      { min: 50, label: '观察 Watch', cls: 'copper', chip: 'chip copper', advice: '进入「留存」序列：推送未使用的高价值功能，安排一次轻量回访，防止滑入风险区。' },
      { min: 25, label: '风险 At-Risk', cls: 'copper', chip: 'chip copper', advice: '触发人工干预：客服主动联系 + 定制化再激活 Drip，暂停一切销售类触达。' },
      { min: 0, label: '流失预警 Critical', cls: 'danger', chip: 'chip ink', advice: '进入挽回流程：高管关怀邮件、专属折扣或暂停计费选项，同时记录流失原因。' }
    ];
    const band = bands.find(b => score >= b.min);
    $('#hScore').textContent = score;
    const bar = $('#hBar');
    bar.style.width = score + '%';
    bar.className = band.cls;
    $('#hBand').textContent = band.label;
    $('#hBand').className = band.chip;
    $('#hAdvice').textContent = band.advice;
    return { login: login, adopt: adopt, nps: nps, ticket: ticket, pay: pay, score: score, band: band.label };
  }
  Object.keys(H).forEach(k => $(H[k]).addEventListener('input', calcHealth));
  $('#hPay').addEventListener('change', calcHealth);

  /* ---------- cohort retention simulation ---------- */
  const COHORT_COLORS = ['#0B1F2A', '#2E5A6B', '#5C8577', '#8FB552', '#D9773F', '#9A5B3C'];
  let lastSim = null;

  function simulate() {
    const act = Number($('#simAct').value) / 100;
    const churn = Number($('#simChurn').value) / 100;
    const lift = Number($('#simLift').value) / 100;
    state.sim = { act: act * 100, churn: churn * 100, lift: lift * 100 };
    persist();

    const weeks = 8, cohorts = [];
    for (let c = 0; c < 6; c++) {
      const rng = mulberry(hashStr('cohort|' + c + '|' + act + '|' + churn + '|' + lift));
      const noise = () => (rng() - 0.5) * 0.05;
      const effChurn = churn * (1 - lift);
      const row = { name: 'M' + (c + 1) + ' 队列', values: [], baseline: [] };
      for (let w = 0; w <= weeks; w++) {
        const v = w === 0 ? 1 : Math.max(0.02, act * Math.pow(1 - effChurn, w) * (1 + noise()));
        const b = w === 0 ? 1 : Math.max(0.02, act * Math.pow(1 - churn, w));
        row.values.push(Math.min(1, v));
        row.baseline.push(Math.min(1, b));
      }
      cohorts.push(row);
    }
    lastSim = { weeks: weeks, cohorts: cohorts, params: { activation: act, weeklyChurn: churn, dripLift: lift } };
    drawChart(lastSim);
    renderCohortTable(lastSim);
    toast('模拟完成：6 个队列 × ' + (weeks + 1) + ' 周');
  }

  function drawChart(sim) {
    const canvas = $('#cohortChart');
    const ctx = canvas.getContext('2d');
    const W = canvas.width, Hh = canvas.height;
    const padL = 56, padR = 140, padT = 24, padB = 40;
    const plotW = W - padL - padR, plotH = Hh - padT - padB;

    ctx.clearRect(0, 0, W, Hh);
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, W, Hh);

    // grid + axes
    ctx.strokeStyle = 'rgba(11,31,42,.10)';
    ctx.fillStyle = 'rgba(11,31,42,.55)';
    ctx.font = '12px IBM Plex Sans, sans-serif';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 5; i++) {
      const y = padT + plotH * i / 5;
      ctx.beginPath(); ctx.moveTo(padL, y); ctx.lineTo(padL + plotW, y); ctx.stroke();
      ctx.textAlign = 'right';
      ctx.fillText((100 - i * 20) + '%', padL - 8, y + 4);
    }
    for (let w = 0; w <= sim.weeks; w++) {
      const x = padL + plotW * w / sim.weeks;
      ctx.textAlign = 'center';
      ctx.fillText('W' + w, x, Hh - padB + 20);
    }

    const xy = (w, v) => [padL + plotW * w / sim.weeks, padT + plotH * (1 - v)];

    // baseline（无干预平均）虚线
    const base = [];
    for (let w = 0; w <= sim.weeks; w++) {
      let s = 0;
      sim.cohorts.forEach(c => { s += c.baseline[w]; });
      base.push(s / sim.cohorts.length);
    }
    ctx.setLineDash([5, 5]);
    ctx.strokeStyle = 'rgba(11,31,42,.35)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    base.forEach((v, w) => { const p = xy(w, v); w === 0 ? ctx.moveTo(p[0], p[1]) : ctx.lineTo(p[0], p[1]); });
    ctx.stroke();
    ctx.setLineDash([]);

    // cohort lines
    sim.cohorts.forEach((c, i) => {
      ctx.strokeStyle = COHORT_COLORS[i % COHORT_COLORS.length];
      ctx.lineWidth = 2.2;
      ctx.beginPath();
      c.values.forEach((v, w) => { const p = xy(w, v); w === 0 ? ctx.moveTo(p[0], p[1]) : ctx.lineTo(p[0], p[1]); });
      ctx.stroke();
      c.values.forEach((v, w) => {
        const p = xy(w, v);
        ctx.fillStyle = COHORT_COLORS[i % COHORT_COLORS.length];
        ctx.beginPath(); ctx.arc(p[0], p[1], 3, 0, Math.PI * 2); ctx.fill();
      });
    });

    // legend
    ctx.textAlign = 'left';
    sim.cohorts.forEach((c, i) => {
      const ly = padT + 8 + i * 22;
      ctx.fillStyle = COHORT_COLORS[i % COHORT_COLORS.length];
      ctx.fillRect(padL + plotW + 16, ly - 8, 14, 4);
      ctx.fillStyle = 'rgba(11,31,42,.8)';
      ctx.fillText(c.name + ' · W8 ' + Math.round(c.values[8] * 100) + '%', padL + plotW + 36, ly - 2);
    });
    ctx.fillStyle = 'rgba(11,31,42,.5)';
    ctx.fillText('— — 无干预基准', padL + plotW + 16, padT + 8 + 6 * 22);
  }

  function renderCohortTable(sim) {
    const wrap = $('#cohortTableWrap');
    const head = '<thead><tr><th>队列</th>' + Array.from({ length: sim.weeks + 1 }, (_, w) => '<th class="right">W' + w + '</th>').join('') + '</tr></thead>';
    const body = '<tbody>' + sim.cohorts.map(c =>
      '<tr><td><b>' + esc(c.name) + '</b></td>' + c.values.map(v => '<td class="right">' + Math.round(v * 100) + '%</td>').join('') + '</tr>'
    ).join('') + '</tbody>';
    $('#cohortTable').innerHTML = head + body;
    wrap.style.display = '';
  }

  ['simAct', 'simChurn', 'simLift'].forEach(id => {
    $('#' + id).addEventListener('input', () => {
      $('#simActV').textContent = $('#simAct').value + '%';
      $('#simChurnV').textContent = $('#simChurn').value + '%';
      $('#simLiftV').textContent = $('#simLift').value + '%';
    });
  });
  $('#runSim').addEventListener('click', simulate);

  /* ---------- playbook exports ---------- */
  function playbookData() {
    return {
      meta: { product: 'meridian-flow-ops', version: 1, exportedAt: new Date().toISOString() },
      name: state.name || '未命名 Playbook',
      lifecycle: STAGE_DEFS.map(d => ({
        stage: d.id, label: d.cn + ' ' + d.en,
        goal: state.stages[d.id].goal, metric: state.stages[d.id].metric,
        segmentLogic: state.stages[d.id].logic || 'AND',
        segmentRules: state.stages[d.id].rules,
        dripSequence: state.stages[d.id].seq
      })),
      healthModel: {
        factors: [
          { name: '月登录天数', weight: 0.30, scale: '0-30 天' },
          { name: '核心功能采用率', weight: 0.30, scale: '0-100%' },
          { name: 'NPS 评分', weight: 0.25, scale: '0-10' },
          { name: '近 30 天工单数', weight: -0.15, scale: '0-10（惩罚项，封顶 -15）' },
          { name: '订阅状态', weight: 0, scale: '正常 0 / 逾期 -15 / 已取消 -40（修正项）' }
        ],
        bands: [{ band: '健康', range: '75-100' }, { band: '观察', range: '50-74' }, { band: '风险', range: '25-49' }, { band: '流失预警', range: '0-24' }]
      },
      retentionSim: lastSim || { note: '尚未运行模拟', params: state.sim }
    };
  }
  $('#exportJson').addEventListener('click', () => {
    download(slug(state.name) + '.playbook.json', JSON.stringify(playbookData(), null, 2), 'application/json');
    toast('已导出 Playbook JSON');
  });
  $('#exportMd').addEventListener('click', () => {
    const d = playbookData();
    const md = ['# ' + d.name + ' · 用户运营 Playbook', '', '> 由 MERIDIAN Flow Ops 生成 · ' + d.meta.exportedAt.slice(0, 16).replace('T', ' '), ''];
    d.lifecycle.forEach(st => {
      md.push('## ' + st.label, '', '- **目标**：' + (st.goal || '—'), '- **北极星指标**：' + (st.metric || '—'), '');
      md.push('### 进入条件（' + st.segmentLogic + '）', '');
      if (st.segmentRules.length) st.segmentRules.forEach(r => md.push('- ' + r.field + ' ' + r.op + ' ' + r.value));
      else md.push('- 全部用户');
      md.push('', '### Drip 序列', '');
      if (st.dripSequence.length) {
        md.push('| Day | 渠道 | 标题 | 内容 |', '|---|---|---|---|');
        st.dripSequence.forEach(m => md.push('| ' + m.day + ' | ' + m.channel + ' | ' + m.title.replace(/\|/g, '\\|') + ' | ' + m.body.replace(/\|/g, '\\|').replace(/\n/g, ' ') + ' |'));
      } else md.push('（无）');
      md.push('');
    });
    md.push('## 健康分模型', '');
    d.healthModel.factors.forEach(f => md.push('- ' + f.name + '：权重 ' + f.weight + '（' + f.scale + '）'));
    md.push('', '分档：' + d.healthModel.bands.map(b => b.band + ' ' + b.range).join(' · '), '');
    if (lastSim) {
      md.push('## 留存模拟（' + Math.round(lastSim.params.activation * 100) + '% 激活 / ' + Math.round(lastSim.params.weeklyChurn * 100) + '% 周流失 / +' + Math.round(lastSim.params.dripLift * 100) + '% 干预）', '');
      md.push('| 队列 | ' + Array.from({ length: lastSim.weeks + 1 }, (_, w) => 'W' + w).join(' | ') + ' |');
      md.push('|' + '---|'.repeat(lastSim.weeks + 2));
      lastSim.cohorts.forEach(c => md.push('| ' + c.name + ' | ' + c.values.map(v => Math.round(v * 100) + '%').join(' | ') + ' |'));
    }
    download(slug(state.name) + '.playbook.md', md.join('\n'), 'text/markdown');
    toast('已导出 Playbook Markdown');
  });
  function slug(s) {
    const a = String(s || 'meridian-playbook').trim().replace(/[\\/:*?"<>|\s]+/g, '-');
    return a || 'meridian-playbook';
  }

  /* ---------- playbook library ---------- */
  function renderPbList() {
    const saves = loadSaves();
    $('#pbList').innerHTML = '<option value="">载入已存…</option>' +
      Object.keys(saves).map(n => '<option value="' + esc(n) + '">' + esc(n) + '</option>').join('');
  }
  $('#pbName').addEventListener('input', e => { state.name = e.target.value; persist(); });
  $('#savePb').addEventListener('click', () => {
    const name = (state.name || '').trim();
    if (!name) { toast('请先填写 Playbook 名称'); $('#pbName').focus(); return; }
    const saves = loadSaves();
    saves[name] = JSON.parse(JSON.stringify(state));
    writeSaves(saves); renderPbList();
    $('#pbList').value = name;
    toast('已保存「' + name + '」');
  });
  $('#pbList').addEventListener('change', e => {
    const name = e.target.value; if (!name) return;
    const saves = loadSaves();
    if (saves[name]) {
      state = saves[name]; persist();
      $('#pbName').value = state.name || '';
      renderStages(); renderDrip(); renderRules();
      toast('已载入「' + name + '」');
    }
  });
  $('#delPb').addEventListener('click', () => {
    const name = $('#pbList').value;
    if (!name) { toast('先在下拉框选择要删除的 Playbook'); return; }
    const saves = loadSaves();
    delete saves[name]; writeSaves(saves); renderPbList();
    toast('已删除「' + name + '」');
  });

  $('#heroExample').addEventListener('click', () => {
    state = defaultState();
    state.name = '示例 · SaaS 全周期 Playbook';
    $('#pbName').value = state.name;
    persist();
    activeStage = 'activate';
    renderStages(); renderDrip(); renderRules();
    simulate();
    document.getElementById('studio').scrollIntoView({ behavior: 'smooth' });
    toast('示例 Playbook 已载入');
  });

  /* ---------- init ---------- */
  $('#pbName').value = state.name || '';
  if (state.sim) {
    $('#simAct').value = Math.round(state.sim.act);
    $('#simChurn').value = Math.round(state.sim.churn);
    $('#simLift').value = Math.round(state.sim.lift);
    $('#simActV').textContent = Math.round(state.sim.act) + '%';
    $('#simChurnV').textContent = Math.round(state.sim.churn) + '%';
    $('#simLiftV').textContent = Math.round(state.sim.lift) + '%';
  }
  renderStages(); renderDrip(); renderRules(); renderPbList();
  calcHealth();
  simulate();
})();
