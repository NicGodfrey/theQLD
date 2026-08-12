/* MERIDIAN · Flow Content — AI 内容工作流
   选题 → 大纲 → 长文 → 社媒切片 → SEO Meta 多标签工作台。
   全部产物由确定性模板引擎在浏览器内生成，可编辑、可持久化，
   最终通过 Blob 触发多文件 Markdown 下载（zip-like）。 */
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
    setTimeout(() => { URL.revokeObjectURL(url); a.remove(); }, 800);
  }
  function toast(msg) {
    let t = $('.toast');
    if (!t) { t = document.createElement('div'); t.className = 'toast'; document.body.appendChild(t); }
    t.textContent = msg; t.classList.add('show');
    clearTimeout(toast._t); toast._t = setTimeout(() => t.classList.remove('show'), 2400);
  }

  /* ---------- state ---------- */
  const LS_CURRENT = 'meridian.flow-content.current.v1';
  const LS_SAVES = 'meridian.flow-content.saves.v1';

  function blankState() {
    return {
      name: '',
      topic: '', keyword: '', keywords2: '', audience: '', tone: '务实直接', sections: 5,
      outline: '', longform: '',
      social: { xhs: '', douyin: '', twitter: '', email: '' },
      seo: { title: '', desc: '', slug: '', keywords: '', anchors: '' }
    };
  }
  let state = blankState();
  try {
    const s = JSON.parse(localStorage.getItem(LS_CURRENT));
    if (s && typeof s === 'object') state = Object.assign(blankState(), s);
  } catch (e) { }

  let persistTimer;
  function persist() {
    clearTimeout(persistTimer);
    persistTimer = setTimeout(() => {
      try { localStorage.setItem(LS_CURRENT, JSON.stringify(state)); } catch (e) { }
    }, 250);
  }
  function loadSaves() { try { return JSON.parse(localStorage.getItem(LS_SAVES)) || {}; } catch (e) { return {}; } }
  function writeSaves(s) { try { localStorage.setItem(LS_SAVES, JSON.stringify(s)); } catch (e) { } }

  /* ---------- tabs ---------- */
  $('#tabs').addEventListener('click', e => {
    const btn = e.target.closest('button[data-tab]'); if (!btn) return;
    $$('#tabs button').forEach(b => b.classList.toggle('active', b === btn));
    $$('.tab-body').forEach(b => b.classList.toggle('active', b.dataset.body === btn.dataset.tab));
    if (btn.dataset.tab === 'export') renderFileList();
    if (btn.dataset.tab === 'longform') analyzeDensity();
  });
  function gotoTab(name) {
    const btn = $('#tabs button[data-tab="' + name + '"]');
    if (btn) btn.click();
  }

  /* ---------- generators ---------- */
  const SECTION_PATTERNS = [
    { h2: '为什么「{T}」现在值得认真对待', h3: ['被低估的信号', '{A}正在遇到的真实瓶颈'] },
    { h2: '{K}的底层逻辑：一次讲清', h3: ['三个核心概念', '常见误解与纠偏'] },
    { h2: '实操路径：从零开始跑通{K}', h3: ['第一周做什么', '工具与模板清单', '容易踩的坑'] },
    { h2: '案例拆解：真实团队怎么用', h3: ['背景与目标', '关键动作复盘', '可迁移的经验'] },
    { h2: '数据视角：{K}到底带来多少变化', h3: ['三个关键指标', '如何度量你自己的进展'] },
    { h2: '进阶策略：把{K}用到 120 分', h3: ['组合打法', '规模化的前提'] },
    { h2: '常见问题与反对意见', h3: ['「我们团队太小」', '「没时间学新东西」'] }
  ];
  const OPENERS = [
    '过去一年，「{T}」从小圈子讨论变成了{A}绕不开的话题。但大部分讨论停留在概念层，真正落地的路径很少有人讲透。',
    '如果你是{A}，大概率已经感受到：{T}不再是「要不要做」的问题，而是「怎么做才不浪费时间」的问题。',
    '这篇文章不贩卖焦虑。我们把{T}拆成可执行的步骤，配上数据与案例，读完你可以直接开始动手。'
  ];
  const PARA_TPL = [
    '先说结论：{K}的价值不在于「新」，而在于它把原本靠天赋和运气的环节，变成了可复制的流程。对{A}来说，这是把产能从个人能力中解绑的关键一步。',
    '很多人第一次接触{K}时会高估它的门槛、低估它的复利。第一周的收益可能只有 10%，但坚持一个月后，节省的时间会以肉眼可见的速度累积。',
    '实践中，建议从最小闭环开始：选一个真实任务，用{K}完整跑一遍，记录每一步的耗时与产出质量，再决定扩大到什么范围。',
    '一个容易被忽略的细节是度量。如果不给{K}设定明确的指标（时间、质量、频率），三周后你将无法回答「它到底有没有用」。',
    '{A}最常见的失败模式，是试图一次性改造所有环节。更稳的路径是每次只替换一个环节，验证后再叠加下一个。',
    '把{K}引入团队时，先解决「谁负责维护模板」的问题。没有 owner 的流程，三个月后一定退化。'
  ];
  const XHS_TAGS = ['#效率提升', '#工作流', '#AI工具', '#干货分享', '#自我提升', '#内容创作'];

  function genOutline() {
    const rng = mulberry(hashStr('outline|' + state.topic + '|' + state.keyword + '|' + state.sections));
    const T = state.topic || '未命名主题';
    const K = state.keyword || T;
    const A = state.audience || '目标读者';
    const fill = s => s.replace(/\{T\}/g, T).replace(/\{K\}/g, K).replace(/\{A\}/g, A);
    const n = Math.min(7, Math.max(5, Number(state.sections) || 5));
    const patterns = SECTION_PATTERNS.slice();
    const chosen = [];
    for (let i = 0; i < n && patterns.length; i++) {
      chosen.push(patterns.splice(Math.floor(rng() * patterns.length), 1)[0]);
    }
    const lines = ['# ' + T, '', '> 读者：' + A + ' · 核心关键词：' + K + ' · 语气：' + state.tone, ''];
    chosen.forEach((p, i) => {
      lines.push('## ' + (i + 1) + '. ' + fill(p.h2));
      p.h3.forEach(h => lines.push('- ' + fill(h)));
      lines.push('');
    });
    lines.push('## 结语与行动清单', '- 三步行动清单', '- 下一篇预告');
    return lines.join('\n');
  }

  function genLongform() {
    const rng = mulberry(hashStr('longform|' + state.topic + '|' + state.keyword + '|' + state.outline.length));
    const T = state.topic || '未命名主题';
    const K = state.keyword || T;
    const A = state.audience || '目标读者';
    const fill = s => s.replace(/\{T\}/g, T).replace(/\{K\}/g, K).replace(/\{A\}/g, A);

    const h2s = (state.outline.match(/^## .+$/gm) || []).map(h => h.replace(/^## /, ''));
    const out = ['# ' + T, '', fill(pick(rng, OPENERS)), ''];
    const paras = PARA_TPL.slice();
    h2s.forEach(h => {
      out.push('## ' + h, '');
      const cnt = 2 + Math.floor(rng() * 2);
      for (let i = 0; i < cnt; i++) {
        if (!paras.length) paras.push.apply(paras, PARA_TPL);
        out.push(fill(paras.splice(Math.floor(rng() * paras.length), 1)[0]), '');
      }
    });
    if (!h2s.length) {
      out.push('（提示：先生成大纲，长文会按大纲小标题展开。以下为通用正文。）', '');
      PARA_TPL.forEach(p => out.push(fill(p), ''));
    }
    out.push('---', '', '**行动清单**：', '1. 用 ' + K + ' 跑通一个最小闭环任务；', '2. 记录前后耗时与质量差异；', '3. 一周后复盘，决定下一个要替换的环节。');
    return out.join('\n');
  }

  function genSocial() {
    const rng = mulberry(hashStr('social|' + state.topic + '|' + state.keyword));
    const T = state.topic || '未命名主题';
    const K = state.keyword || T;
    const A = state.audience || '目标读者';
    const tags = [];
    const bank = XHS_TAGS.slice();
    for (let i = 0; i < 4 && bank.length; i++) tags.push(bank.splice(Math.floor(rng() * bank.length), 1)[0]);

    const xhs = ['💡 ' + T + '｜看完这篇就能上手', '', '最近好多姐妹问我 ' + K + ' 到底怎么入门，一条笔记讲清楚👇', '', '1️⃣ 先跑最小闭环：挑一个真实任务完整走一遍', '2️⃣ 记录数据：前后耗时对比，别凭感觉', '3️⃣ 每次只换一个环节，稳扎稳打', '', '亲测一个月，产出频率翻倍，返工率肉眼可见下降📉', '', '完整长文放在评论区置顶啦～', '', tags.join(' ')].join('\n');

    const douyin = ['【抖音口播脚本 · 60 秒】', '', '(0-3s 钩子) 如果你还在用老办法做「' + T.slice(0, 18) + '」，这条视频帮你省一半时间。', '', '(3-15s 痛点) ' + A + '每天都在重复劳动，真正的问题不是不努力，是没有流程。', '', '(15-40s 干货) 记住三步：第一，跑通最小闭环；第二，记录数据；第三，每次只替换一个环节。' + K + ' 的复利就是这么滚起来的。', '', '(40-55s 案例) 我们实测一个月：制作时间从 9 小时压到 3.5 小时。', '', '(55-60s CTA) 完整方法论在主页长文，点关注慢慢看。'].join('\n');

    const twitter = ['🧵 1/5 ' + T, '', '2/5 Most people overestimate the learning curve of ' + K + ' and underestimate its compounding returns.', '', '3/5 The playbook: ship one minimal loop → measure time saved → replace one more step. Repeat.', '', '4/5 Real numbers from our test: production time 9h → 3.5h in 4 weeks. Rework rate down 38%.', '', '5/5 Full write-up (in Chinese) + templates below. Follow for the English version. 🔗'].join('\n');

    const email = ['主题：' + T + '（3 分钟实操版）', '', 'Hi，', '', '这周只讲一件事：' + K + '。', '', '为什么值得你花 3 分钟：', '· 它把「靠灵感」变成「靠流程」；', '· 第一周就能看到 10% 的时间节省；', '· 我们准备了可直接套用的模板。', '', '三步开始：', '1. 挑一个真实任务，完整跑一遍最小闭环；', '2. 记录前后耗时；', '3. 回信告诉我你的数字，我们下期公开汇总。', '', '—— MERIDIAN Studio'].join('\n');

    return { xhs: xhs, douyin: douyin, twitter: twitter, email: email };
  }

  function genSeo() {
    const T = state.topic || '未命名主题';
    const K = state.keyword || T;
    const k2 = state.keywords2.split(/[,，]/).map(s => s.trim()).filter(Boolean);
    let title = K + '：' + T;
    if (title.length > 57) title = title.slice(0, 57) + '…';
    title += ' | MERIDIAN';
    let desc = '本文面向' + (state.audience || '希望提效的读者') + '，系统讲解' + K + '的底层逻辑、实操路径与真实案例，附可直接套用的模板与三步行动清单。';
    if (desc.length > 158) desc = desc.slice(0, 155) + '…';
    const ascii = (K + ' ' + T).replace(/[^A-Za-z0-9\s-]/g, ' ').trim().toLowerCase().replace(/\s+/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '');
    const slugStr = ascii.length >= 3 ? ascii.slice(0, 60) : 'guide-' + (hashStr(T + K) % 100000).toString(36);
    const anchors = [K + ' 入门指南', K + ' 最佳实践', T.slice(0, 20) + ' 案例拆解', K + ' 常见问题'];
    return {
      title: title, desc: desc, slug: slugStr,
      keywords: [K].concat(k2).join(', '),
      anchors: anchors.join('\n')
    };
  }

  /* ---------- keyword density ---------- */
  function countOccur(text, kw) {
    if (!kw) return 0;
    let n = 0, i = 0;
    const lower = text.toLowerCase(), k = kw.toLowerCase();
    while ((i = lower.indexOf(k, i)) !== -1) { n++; i += k.length; }
    return n;
  }
  function analyzeDensity() {
    const box = $('#densityBox');
    const text = state.longform || '';
    const total = text.replace(/\s/g, '').length;
    $('#lfStats').textContent = total.toLocaleString('zh-CN') + ' 字';
    if (!text || !state.keyword) {
      box.innerHTML = '<p class="muted mb-0">' + (!text ? '生成或粘贴长文后自动分析。' : '请先在「选题」页填写核心关键词。') + '</p>';
      return;
    }
    const rows = [];
    const kws = [{ kw: state.keyword, primary: true }].concat(
      state.keywords2.split(/[,，]/).map(s => s.trim()).filter(Boolean).map(k => ({ kw: k, primary: false }))
    );
    kws.forEach(item => {
      const c = countOccur(text, item.kw);
      const density = total ? (c * item.kw.length / total * 100) : 0;
      let cls = 'chip', label = '偏低';
      if (item.primary) {
        if (density >= 0.5 && density <= 2.5) { cls = 'chip acid'; label = '理想'; }
        else if (density > 2.5) { cls = 'chip copper'; label = '过高'; }
      } else {
        label = c > 0 ? '已覆盖' : '未出现';
        if (c > 0) cls = 'chip acid';
      }
      rows.push('<div class="row-between"><span>' + esc(item.kw) + (item.primary ? ' <b class="muted">核心</b>' : '') + '</span>' +
        '<span class="row" style="gap:6px"><span class="muted">' + c + ' 次 · ' + density.toFixed(2) + '%</span><span class="' + cls + '">' + label + '</span></span></div>');
    });
    box.innerHTML = rows.join('');
  }

  /* ---------- form binding ---------- */
  const FIELDS = [
    ['#tTopic', 'topic'], ['#tKeyword', 'keyword'], ['#tKeywords2', 'keywords2'],
    ['#tAudience', 'audience'], ['#tTone', 'tone'], ['#tLength', 'sections'],
    ['#aOutline', 'outline'], ['#aLongform', 'longform']
  ];
  function syncToDom() {
    FIELDS.forEach(f => { $(f[0]).value = state[f[1]] != null ? state[f[1]] : ''; });
    $('#sXhs').value = state.social.xhs; $('#sDouyin').value = state.social.douyin;
    $('#sTwitter').value = state.social.twitter; $('#sEmail').value = state.social.email;
    $('#seoTitle').value = state.seo.title; $('#seoDesc').value = state.seo.desc;
    $('#seoSlug').value = state.seo.slug; $('#seoKeywords').value = state.seo.keywords;
    $('#seoAnchors').value = state.seo.anchors;
    $('#projName').value = state.name || '';
    seoCounters(); analyzeDensity();
  }
  FIELDS.forEach(f => {
    $(f[0]).addEventListener('input', e => {
      state[f[1]] = e.target.value; persist();
      if (f[1] === 'longform') analyzeDensity();
    });
  });
  [['#sXhs', 'xhs'], ['#sDouyin', 'douyin'], ['#sTwitter', 'twitter'], ['#sEmail', 'email']].forEach(f => {
    $(f[0]).addEventListener('input', e => { state.social[f[1]] = e.target.value; persist(); });
  });
  [['#seoTitle', 'title'], ['#seoDesc', 'desc'], ['#seoSlug', 'slug'], ['#seoKeywords', 'keywords'], ['#seoAnchors', 'anchors']].forEach(f => {
    $(f[0]).addEventListener('input', e => { state.seo[f[1]] = e.target.value; persist(); seoCounters(); });
  });
  $('#projName').addEventListener('input', e => { state.name = e.target.value; persist(); });

  function seoCounters() {
    $('#seoTitleCount').textContent = '(' + state.seo.title.length + '/60)';
    $('#seoDescCount').textContent = '(' + state.seo.desc.length + '/160)';
  }

  /* ---------- generate actions ---------- */
  function generateAll() {
    if (!state.topic) { toast('请先填写选题 / 主题'); gotoTab('topic'); return; }
    state.outline = genOutline();
    state.longform = genLongform();
    state.social = genSocial();
    state.seo = genSeo();
    persist(); syncToDom();
    gotoTab('outline');
    toast('已生成：大纲 / 长文 / 社媒切片 / SEO Meta');
  }
  $('#genAll').addEventListener('click', generateAll);

  $$('button[data-regen]').forEach(btn => {
    btn.addEventListener('click', () => {
      const what = btn.dataset.regen;
      if (!state.topic) { toast('请先填写选题 / 主题'); gotoTab('topic'); return; }
      if (what === 'outline') state.outline = genOutline();
      if (what === 'longform') state.longform = genLongform();
      if (what === 'social') state.social = genSocial();
      if (what === 'seo') state.seo = genSeo();
      persist(); syncToDom();
      toast('已重新生成');
    });
  });

  $('#heroExample').addEventListener('click', () => {
    state = Object.assign(blankState(), {
      name: '示例 · AI 工作流选题',
      topic: 'AI 工作流如何帮 3 人小团队追平大厂产能',
      keyword: 'AI 工作流', keywords2: '自动化, 提示词, 效率工具',
      audience: '3-10 人的小型创业团队', tone: '务实直接', sections: 6
    });
    generateAll();
    document.getElementById('studio').scrollIntoView({ behavior: 'smooth' });
  });

  /* ---------- projects ---------- */
  function renderProjList() {
    const saves = loadSaves();
    const sel = $('#projList');
    sel.innerHTML = '<option value="">载入已存项目…</option>' +
      Object.keys(saves).map(n => '<option value="' + esc(n) + '">' + esc(n) + '</option>').join('');
  }
  $('#saveProj').addEventListener('click', () => {
    const name = (state.name || '').trim();
    if (!name) { toast('请先填写项目名称'); $('#projName').focus(); return; }
    const saves = loadSaves();
    saves[name] = JSON.parse(JSON.stringify(state));
    saves[name].savedAt = new Date().toISOString();
    writeSaves(saves); renderProjList();
    $('#projList').value = name;
    toast('已保存项目「' + name + '」');
  });
  $('#projList').addEventListener('change', e => {
    const name = e.target.value; if (!name) return;
    const saves = loadSaves();
    if (saves[name]) {
      state = Object.assign(blankState(), saves[name]);
      persist(); syncToDom();
      toast('已载入「' + name + '」');
    }
  });
  $('#delProj').addEventListener('click', () => {
    const name = $('#projList').value;
    if (!name) { toast('先在下拉框选择要删除的项目'); return; }
    const saves = loadSaves();
    delete saves[name]; writeSaves(saves); renderProjList();
    toast('已删除「' + name + '」');
  });

  /* ---------- export (multi-file via Blob) ---------- */
  function buildFiles() {
    const socialMd = ['# 社媒切片 · ' + (state.topic || '未命名'), '', '## 小红书笔记', '', state.social.xhs, '', '## 抖音口播脚本', '', state.social.douyin, '', '## Twitter/X Thread', '', state.social.twitter, '', '## Email Newsletter', '', state.social.email].join('\n');
    const seoMd = ['# SEO Meta · ' + (state.topic || '未命名'), '', '- **Title**: ' + state.seo.title, '- **Description**: ' + state.seo.desc, '- **Slug**: `' + state.seo.slug + '`', '- **Keywords**: ' + state.seo.keywords, '', '## 建议内链锚文本', '', state.seo.anchors.split('\n').filter(Boolean).map(a => '- ' + a).join('\n')].join('\n');
    return [
      { name: '01-outline.md', content: state.outline || '（空）', mime: 'text/markdown' },
      { name: '02-longform.md', content: state.longform || '（空）', mime: 'text/markdown' },
      { name: '03-social.md', content: socialMd, mime: 'text/markdown' },
      { name: '04-seo.md', content: seoMd, mime: 'text/markdown' },
      { name: 'project.json', content: JSON.stringify({ meta: { product: 'meridian-flow-content', version: 1, exportedAt: new Date().toISOString() }, project: state }, null, 2), mime: 'application/json' }
    ];
  }
  function renderFileList() {
    const files = buildFiles();
    $('#fileList').innerHTML = files.map((f, i) => `
      <div class="subpanel row-between">
        <span><span class="mono">${esc(f.name)}</span> <span class="muted small">· ${(new Blob([f.content]).size / 1024).toFixed(1)} KB</span></span>
        <button class="btn btn-sm btn-ghost" data-file="${i}">单独下载</button>
      </div>`).join('');
  }
  $('#fileList').addEventListener('click', e => {
    const btn = e.target.closest('[data-file]'); if (!btn) return;
    const f = buildFiles()[Number(btn.dataset.file)];
    if (f) { download(f.name, f.content, f.mime); toast('已下载 ' + f.name); }
  });
  $('#exportAll').addEventListener('click', () => {
    const files = buildFiles();
    files.forEach((f, i) => setTimeout(() => download(f.name, f.content, f.mime), i * 350));
    toast('正在连续下载 ' + files.length + ' 个文件…');
  });

  /* ---------- init ---------- */
  syncToDom();
  renderProjList();
})();
