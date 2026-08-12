/* MERIDIAN · Flow Market — AI 营销工作流
   Campaign builder：目标 / 人群 / 渠道 / 预算 / 日历 → 完整方案（钩子、CTA、A/B、KPI）
   导出 CSV + JSON，方案持久化于 localStorage。 */
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
  const pick = (rng, arr) => arr[Math.floor(rng() * arr.length)];
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
  const fmtMoney = n => '¥' + Math.round(n).toLocaleString('zh-CN');
  const fmtNum = n => Math.round(n).toLocaleString('zh-CN');
  function isoDate(d) { return d.toISOString().slice(0, 10); }
  function weekdayCN(d) { return '周' + '日一二三四五六'[d.getDay()]; }

  /* ---------- domain data ---------- */
  const LS_CURRENT = 'meridian.flow-market.current.v1';
  const LS_SAVES = 'meridian.flow-market.saves.v1';

  const CHANNELS = {
    '小红书': { weight: 0.28, perWeek: 3, days: [1, 3, 6], format: '图文笔记', metric: '互动量', unitCost: 2.6 },
    '抖音': { weight: 0.30, perWeek: 4, days: [1, 2, 4, 6], format: '短视频', metric: '播放量', unitCost: 0.06 },
    'Twitter/X': { weight: 0.12, perWeek: 5, days: [1, 2, 3, 4, 5], format: 'Thread / 推文', metric: '曝光量', unitCost: 0.04 },
    'Email': { weight: 0.12, perWeek: 1, days: [4], format: 'Newsletter', metric: '打开率', unitCost: 0.9 },
    'SEO': { weight: 0.18, perWeek: 1, days: [2], format: '长文 / 专题页', metric: '自然点击', unitCost: 1.4 }
  };

  const GOALS = {
    brand: { label: '品牌曝光 Awareness', kpiName: '总曝光', perYuan: 160, cta: ['关注我们，看下一期拆解', '把这篇转给你的同事', '点头像看完整系列'] },
    leads: { label: '线索获取 Leads', kpiName: '合格线索 (MQL)', perYuan: 1 / 85, cta: ['留下邮箱领完整模板', '扫码进群领取资料包', '预约 15 分钟演示'] },
    conversion: { label: '电商转化 Conversion', kpiName: '成交订单', perYuan: 1 / 220, cta: ['限时 72 小时早鸟价', '点击小黄车立即下单', '首单立减，今晚截止'] },
    community: { label: '私域增长 Community', kpiName: '新增私域用户', perYuan: 1 / 12, cta: ['加入 3000 人实践社群', '回复「入群」获取入口', '关注领新人礼包'] },
    launch: { label: '产品发布 Launch', kpiName: '发布页访问', perYuan: 3.2, cta: ['加入等待名单', '抢首发内测名额', '预约发布直播'] }
  };

  const PILLAR_BANK = [
    '痛点放大：没有它之前的一天有多糟', '场景演示：真实使用场景 60 秒走完', '数据证明：用 3 个数字说服理性用户',
    '用户故事：一个真实客户的前后对比', '幕后揭秘：产品/团队的制作过程', '行业观点：对趋势的独家判断',
    '对比横评：和替代方案摆在一起比', '清单干货：立刻能抄走的操作清单'
  ];
  const HOOKS = {
    '小红书': ['救命！这个{P}我怎么现在才知道', '被问爆了！{A}都在用的{P}方法', '无广真实测评：{P}到底值不值', '收藏＝学会！{P}保姆级教程', '月底复盘：靠{P}我省下了 20 小时'],
    '抖音': ['前 3 秒：如果你还在手动做这件事，停下来', '99% 的{A}不知道的隐藏功能', '挑战：一天之内只用{P}完成全部工作', '别刷走，这条视频帮你省一半预算', '我把{P}的全流程拍给你看'],
    'Twitter/X': ['We analyzed {P} so you don\'t have to. Thread 🧵', 'Unpopular opinion about {P}:', '{P} in 5 screenshots:', 'How {A} ship 2x faster with {P}:', 'I spent 30 days testing {P}. Results:'],
    'Email': ['【第 {W} 周】给{A}的一封实操信', '你上次差点错过的{P}更新', '3 分钟读完：{P}本周最重要的一件事', '内部数据首次公开：{P}', '给{A}的周五清单：{P}'],
    'SEO': ['{P}完全指南（2026 最新版）', '{P}是什么？给{A}的入门解释', '{P} vs 传统做法：数据对比', '10 个{P}最佳实践（附模板）', '{P}常见问题 FAQ 汇总']
  };

  /* ---------- state ---------- */
  let campaign = null;
  function loadSaves() { try { return JSON.parse(localStorage.getItem(LS_SAVES)) || {}; } catch (e) { return {}; } }
  function writeSaves(s) { try { localStorage.setItem(LS_SAVES, JSON.stringify(s)); } catch (e) { } }
  function persistCurrent() { try { localStorage.setItem(LS_CURRENT, JSON.stringify({ brief: readBrief(), campaign: campaign })); } catch (e) { } }

  function readBrief() {
    return {
      name: $('#cName').value.trim(),
      goal: $('#cGoal').value,
      audience: $('#cAudience').value.trim(),
      channels: $$('#cChannels input:checked').map(i => i.value),
      budget: Math.max(0, Number($('#cBudget').value) || 0),
      weeks: Math.min(12, Math.max(1, Number($('#cWeeks').value) || 4)),
      start: $('#cStart').value || isoDate(new Date())
    };
  }
  function writeBrief(b) {
    $('#cName').value = b.name || '';
    $('#cGoal').value = b.goal || 'brand';
    $('#cAudience').value = b.audience || '';
    $$('#cChannels input').forEach(i => { i.checked = (b.channels || []).indexOf(i.value) !== -1; });
    $('#cBudget').value = b.budget || 30000;
    $('#cWeeks').value = b.weeks || 4;
    $('#cStart').value = b.start || isoDate(new Date());
  }

  /* ---------- generation ---------- */
  function buildCampaign(brief) {
    const seed = hashStr(JSON.stringify([brief.name, brief.goal, brief.audience, brief.channels, brief.budget, brief.weeks, brief.start]));
    const rng = mulberry(seed);
    const goal = GOALS[brief.goal];
    const A = brief.audience ? brief.audience.slice(0, 12) : '目标用户';
    const P = brief.name || '本产品';

    const totalW = brief.channels.reduce((s, c) => s + CHANNELS[c].weight, 0) || 1;
    const allocation = brief.channels.map(c => ({
      channel: c,
      share: CHANNELS[c].weight / totalW,
      amount: brief.budget * CHANNELS[c].weight / totalW
    }));

    const primaryKpi = { name: goal.kpiName, target: Math.max(1, Math.round(brief.budget * goal.perYuan)) };
    const channelKpis = allocation.map(a => {
      const ch = CHANNELS[a.channel];
      return { channel: a.channel, metric: ch.metric, target: Math.max(1, Math.round(a.amount / ch.unitCost)), budget: a.amount };
    });

    const pillars = [];
    const bank = PILLAR_BANK.slice();
    for (let i = 0; i < 5 && bank.length; i++) {
      pillars.push(bank.splice(Math.floor(rng() * bank.length), 1)[0]);
    }

    const posts = [];
    const start = new Date(brief.start + 'T00:00:00');
    let pi = 0;
    for (let w = 0; w < brief.weeks; w++) {
      brief.channels.forEach(c => {
        const ch = CHANNELS[c];
        ch.days.slice(0, ch.perWeek).forEach(dow => {
          const d = new Date(start);
          const offset = (dow - start.getDay() + 7) % 7;
          d.setDate(start.getDate() + w * 7 + offset);
          const pillar = pillars[pi % pillars.length]; pi++;
          const hookTpl = HOOKS[c];
          const fill = t => t.replace(/\{P\}/g, P).replace(/\{A\}/g, A).replace(/\{W\}/g, String(w + 1));
          const hookA = fill(pick(rng, hookTpl));
          let hookB; do { hookB = fill(pick(rng, hookTpl)); } while (hookB === hookA && hookTpl.length > 1);
          posts.push({
            date: isoDate(d), week: w + 1, channel: c, format: ch.format,
            pillar: pillar.split('：')[0],
            hookA: hookA, hookB: hookB,
            cta: pick(rng, goal.cta)
          });
        });
      });
    }
    posts.sort((a, b) => a.date < b.date ? -1 : a.date > b.date ? 1 : a.channel < b.channel ? -1 : 1);

    return {
      meta: { product: 'meridian-flow-market', version: 1, generatedAt: new Date().toISOString() },
      brief: brief, goalLabel: goal.label,
      allocation: allocation, primaryKpi: primaryKpi, channelKpis: channelKpis,
      pillars: pillars, posts: posts
    };
  }

  /* ---------- rendering ---------- */
  function render() {
    if (!campaign) {
      $('#planPanel').style.display = 'none';
      $('#calendarPanel').style.display = 'none';
      $('#emptyPanel').style.display = '';
      return;
    }
    $('#emptyPanel').style.display = 'none';
    $('#planPanel').style.display = '';
    $('#calendarPanel').style.display = '';
    $('#planTitle').textContent = campaign.brief.name || '未命名 Campaign';

    const alloc = campaign.allocation.map((a, i) => `
      <div>
        <div class="row-between small"><span>${esc(a.channel)} <span class="muted">· ${esc(CHANNELS[a.channel].format)}</span></span>
        <span><b>${fmtMoney(a.amount)}</b> <span class="muted">(${Math.round(a.share * 100)}%)</span></span></div>
        <div class="meter"><i class="${i % 2 ? 'copper' : ''}" style="width:${Math.max(4, Math.round(a.share * 100))}%"></i></div>
      </div>`).join('');

    const kpiRows = campaign.channelKpis.map(k => `
      <tr><td>${esc(k.channel)}</td><td>${esc(k.metric)}</td><td class="right"><b>${fmtNum(k.target)}</b></td><td class="right">${fmtMoney(k.budget)}</td></tr>`).join('');

    $('#planSummary').innerHTML = `
      <div class="row" style="gap:8px">
        <span class="chip ink">${esc(campaign.goalLabel)}</span>
        <span class="chip">周期 ${campaign.brief.weeks} 周</span>
        <span class="chip">总预算 ${fmtMoney(campaign.brief.budget)}</span>
        <span class="chip acid">${esc(campaign.primaryKpi.name)} 目标 ${fmtNum(campaign.primaryKpi.target)}</span>
      </div>
      <div class="subpanel">
        <div class="panel-kicker">Audience / 人群</div>
        <p class="small mb-0">${esc(campaign.brief.audience || '（未填写人群描述）')}</p>
      </div>
      <div class="cols-2">
        <div class="subpanel stack">
          <div class="panel-kicker">Budget / 预算分配</div>
          ${alloc}
        </div>
        <div class="subpanel">
          <div class="panel-kicker">Pillars / 内容支柱</div>
          <ol class="small" style="margin:0;padding-left:18px">${campaign.pillars.map(p => '<li>' + esc(p) + '</li>').join('')}</ol>
        </div>
      </div>
      <div class="subpanel">
        <div class="panel-kicker">KPI / 渠道指标</div>
        <div class="table-scroll" style="background:transparent;border:none">
          <table class="data" style="min-width:420px">
            <thead><tr><th>渠道</th><th>指标</th><th class="right">目标</th><th class="right">预算</th></tr></thead>
            <tbody>${kpiRows}</tbody>
          </table>
        </div>
      </div>`;

    $('#calHint').textContent = campaign.posts.length + ' 条发布 · ' + campaign.brief.channels.join(' / ');
    let html = '';
    let curWeek = 0;
    campaign.posts.forEach(p => {
      if (p.week !== curWeek) {
        if (curWeek) html += '</tbody></table></div>';
        curWeek = p.week;
        html += `<div class="week-label">Week ${p.week}</div>
          <div class="table-scroll"><table class="data">
          <thead><tr><th>日期</th><th>渠道</th><th>形式</th><th>支柱</th><th>钩子 A</th><th>钩子 B</th><th>CTA</th></tr></thead><tbody>`;
      }
      const d = new Date(p.date + 'T00:00:00');
      html += `<tr>
        <td style="white-space:nowrap">${p.date.slice(5)} ${weekdayCN(d)}</td>
        <td><span class="chip">${esc(p.channel)}</span></td>
        <td class="muted">${esc(p.format)}</td>
        <td>${esc(p.pillar)}</td>
        <td>${esc(p.hookA)}</td>
        <td class="muted">${esc(p.hookB)}</td>
        <td>${esc(p.cta)}</td></tr>`;
    });
    if (curWeek) html += '</tbody></table></div>';
    $('#calendar').innerHTML = html || '<p class="muted">没有生成任何发布（请至少选择一个渠道）。</p>';
  }

  function renderSaves() {
    const saves = loadSaves();
    const names = Object.keys(saves);
    const el = $('#savedList');
    if (!names.length) {
      el.innerHTML = '<p class="small muted mb-0">还没有保存过方案。生成后点「保存当前方案」。</p>';
      return;
    }
    el.innerHTML = names.map(n => `
      <div class="subpanel row-between" data-name="${esc(n)}">
        <div>
          <strong>${esc(n)}</strong>
          <div class="small muted">${esc(saves[n].goalLabel || '')} · ${saves[n].posts ? saves[n].posts.length : 0} 条发布</div>
        </div>
        <span class="row">
          <button class="btn btn-sm btn-ghost" data-load>载入</button>
          <button class="btn btn-sm btn-danger" data-del>删除</button>
        </span>
      </div>`).join('');
  }

  /* ---------- events ---------- */
  $('#generate').addEventListener('click', () => {
    const brief = readBrief();
    if (!brief.channels.length) { toast('请至少选择一个投放渠道'); return; }
    if (!brief.name) { brief.name = '未命名 Campaign'; $('#cName').value = brief.name; }
    campaign = buildCampaign(brief);
    render(); persistCurrent();
    toast('方案已生成：' + campaign.posts.length + ' 条发布排期');
    $('#planPanel').scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  $('#heroExample').addEventListener('click', () => {
    writeBrief({
      name: 'Meridian 效率工具首发战役',
      goal: 'launch',
      audience: '25-38 岁互联网从业者与独立创作者，重度效率工具用户，愿意为省时间付费',
      channels: ['小红书', '抖音', 'Twitter/X', 'Email'],
      budget: 50000, weeks: 4, start: isoDate(new Date())
    });
    campaign = buildCampaign(readBrief());
    render(); persistCurrent(); renderSaves();
    document.getElementById('studio').scrollIntoView({ behavior: 'smooth' });
    toast('示例方案已生成');
  });

  $('#saveCampaign').addEventListener('click', () => {
    if (!campaign) { toast('请先生成方案'); return; }
    const name = campaign.brief.name || '未命名 Campaign';
    const saves = loadSaves();
    saves[name] = campaign;
    writeSaves(saves); renderSaves();
    toast('已保存「' + name + '」');
  });

  $('#savedList').addEventListener('click', e => {
    const item = e.target.closest('[data-name]'); if (!item) return;
    const name = item.dataset.name;
    const saves = loadSaves();
    if (e.target.closest('[data-load]')) {
      campaign = saves[name]; if (!campaign) return;
      writeBrief(campaign.brief);
      render(); persistCurrent();
      toast('已载入「' + name + '」');
    }
    if (e.target.closest('[data-del]')) {
      delete saves[name]; writeSaves(saves); renderSaves();
      toast('已删除「' + name + '」');
    }
  });

  /* ---------- exports ---------- */
  $('#exportCsv').addEventListener('click', () => {
    if (!campaign) return;
    const q = v => '"' + String(v == null ? '' : v).replace(/"/g, '""') + '"';
    const rows = [['date', 'week', 'channel', 'format', 'pillar', 'hook_a', 'hook_b', 'cta']];
    campaign.posts.forEach(p => rows.push([p.date, p.week, p.channel, p.format, p.pillar, p.hookA, p.hookB, p.cta]));
    const csv = '\uFEFF' + rows.map(r => r.map(q).join(',')).join('\r\n');
    download(slug(campaign.brief.name) + '.calendar.csv', csv, 'text/csv');
    toast('已导出日历 CSV（含 BOM，Excel 可直接打开）');
  });

  $('#exportJson').addEventListener('click', () => {
    if (!campaign) return;
    download(slug(campaign.brief.name) + '.campaign.json', JSON.stringify(campaign, null, 2), 'application/json');
    toast('已导出方案 JSON');
  });

  function slug(s) {
    const a = String(s || 'meridian-campaign').trim().replace(/[\\/:*?"<>|\s]+/g, '-');
    return a || 'meridian-campaign';
  }

  /* ---------- init ---------- */
  $('#cStart').value = isoDate(new Date());
  try {
    const cur = JSON.parse(localStorage.getItem(LS_CURRENT));
    if (cur && cur.brief) writeBrief(cur.brief);
    if (cur && cur.campaign) { campaign = cur.campaign; render(); }
  } catch (e) { }
  renderSaves();
})();
