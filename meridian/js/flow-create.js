/* MERIDIAN · Flow Create — AI 创作工作流
   纯前端模拟推理引擎：结构上等同于调用真实 API（异步 + 模型参数），
   输出由 (模型 + 提示词) 哈希种子决定，确定性可复现。 */
(function () {
  'use strict';

  /* ---------- helpers ---------- */
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.prototype.slice.call((r || document).querySelectorAll(s));
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const uid = () => 's' + Math.random().toString(36).slice(2, 9);

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

  /* ---------- state ---------- */
  const LS_CURRENT = 'meridian.flow-create.current.v1';
  const LS_SAVES = 'meridian.flow-create.saves.v1';

  const MODELS = [
    { id: 'meridian-spark', label: 'Meridian Spark · 快速起稿' },
    { id: 'meridian-pro', label: 'Meridian Pro · 深度创作' },
    { id: 'gpt-4o-sim', label: 'GPT-4o（模拟）' },
    { id: 'claude-sonnet-sim', label: 'Claude Sonnet（模拟）' },
    { id: 'qwen-max-sim', label: 'Qwen-Max（模拟）' }
  ];

  function defaultSteps() {
    return [
      { id: uid(), title: '灵感 Idea', model: 'meridian-spark', template: '围绕主题「{{topic}}」，面向{{audience}}，用{{tone}}的语气提出 5 个别人没写过的切入角度，每个角度配一句钩子。' },
      { id: uid(), title: '调研 Research', model: 'qwen-max-sim', template: '基于以下切入角度：\n{{prev}}\n\n为每个角度补充可核查的数据点、真实案例或来源占位，并标注可信度（高/中/低）。' },
      { id: uid(), title: '初稿 Draft', model: 'meridian-pro', template: '依据以下调研素材：\n{{prev}}\n\n写出约 800 字初稿。主题「{{topic}}」，读者是{{audience}}，语气{{tone}}。结构：钩子 → 核心论点 → 案例展开 → 行动建议。' },
      { id: uid(), title: '润色 Polish', model: 'claude-sonnet-sim', template: '润色以下初稿：\n{{prev}}\n\n要求：删掉套话、动词前置、每段不超过 4 行，保留{{tone}}的语气，不新增论点。' },
      { id: uid(), title: '导出 Export', model: 'meridian-spark', template: '把以下成稿整理为可直接发布的 Markdown（含主标题、导语、小标题、结尾 CTA）：\n{{prev}}' }
    ];
  }
  function defaultState() {
    return {
      name: '未命名工作流',
      vars: { topic: 'AI 工作流如何改变个人创作', audience: '独立创作者', tone: '克制而锋利' },
      steps: defaultSteps()
    };
  }

  let state;
  try { state = JSON.parse(localStorage.getItem(LS_CURRENT)) || defaultState(); }
  catch (e) { state = defaultState(); }
  if (!Array.isArray(state.steps) || !state.steps.length) state.steps = defaultSteps();
  if (!state.vars || typeof state.vars !== 'object') state.vars = {};

  let running = false;
  let lastRun = null; // { at, results:[{title,model,prompt,output}] }

  function persist() {
    try { localStorage.setItem(LS_CURRENT, JSON.stringify(state)); } catch (e) { /* quota */ }
  }
  function loadSaves() {
    try { return JSON.parse(localStorage.getItem(LS_SAVES)) || {}; } catch (e) { return {}; }
  }
  function writeSaves(saves) {
    try { localStorage.setItem(LS_SAVES, JSON.stringify(saves)); } catch (e) { /* quota */ }
  }

  /* ---------- template engine ---------- */
  function fillTemplate(tpl, vars) {
    return String(tpl || '').replace(/\{\{\s*([\w\u4e00-\u9fa5]+)\s*\}\}/g, (m, key) =>
      Object.prototype.hasOwnProperty.call(vars, key) && vars[key] !== '' ? vars[key] : m);
  }
  function scanVars() {
    const found = [];
    state.steps.forEach(st => {
      const re = /\{\{\s*([\w\u4e00-\u9fa5]+)\s*\}\}/g;
      let m;
      while ((m = re.exec(st.template || ''))) {
        if (m[1] !== 'prev' && found.indexOf(m[1]) === -1) found.push(m[1]);
      }
    });
    return found;
  }

  /* ---------- simulated inference engine ----------
     结构上等价于: await fetch('/api/generate', {model, prompt}) */
  function callModel(model, prompt, stepMeta) {
    return new Promise(resolve => {
      const seed = hashStr(model + '|' + prompt);
      const rng = mulberry(seed);
      const latency = 450 + Math.floor(rng() * 700);
      setTimeout(() => resolve(composeOutput(model, prompt, stepMeta, mulberry(seed ^ 0x9E3779B9))), latency);
    });
  }

  const BANK = {
    angles: ['反直觉对照：大家以为的顺序其实是错的', '成本拆解：把看不见的时间账算出来', '失败逆推：从一次翻车倒推方法论', '工具链公开：完整晒出每一步用什么', '时间线复盘：30 天逐日记录的变化', '数据叙事：用 3 个数字讲完整个故事', '第一人称实验：亲自当小白鼠'],
    hooks: ['「大多数人把顺序搞反了。」', '「我用 30 天验证了这件事，结论和想象完全不同。」', '「这笔账，很少有人认真算过。」', '「先说结论：省下的不是时间，是决策力。」', '「如果只能保留一个习惯，我留这个。」', '「这个方法笨，但它可复制。」'],
    facts: ['行业调研显示，采用结构化流程的创作者产出频率平均提升 2.1 倍', '某内容平台 2025 年数据：带明确钩子的开头完读率高出 47%', '一项对 1200 名创作者的抽样：坚持模板化工作流 8 周后，返工率下降 38%', '公开案例：某独立作者以五步流水线维持连续 40 周周更', '编辑部门统计：结构先行的稿件平均修改轮次从 4.2 降至 1.8'],
    cred: ['可信度：高（多来源交叉）', '可信度：中（单一来源，需复核）', '可信度：高（平台官方数据）', '可信度：中（样本量有限）'],
    claims: ['真正的瓶颈从来不是灵感，而是从灵感到成稿之间缺一条可复用的路径', '把创作拆成流水线，不是消灭个性，而是把体力活外包给流程，把判断力留给自己', '模板不是天花板，是地板——它保证你最差的一稿也不至于失控', '当每一步都有明确的输入与输出，拖延就失去了藏身之处'],
    cases: ['一位周更作者把选题、调研、初稿拆给三个不同的提示词模板，单篇制作时间从 9 小时压到 3.5 小时', '某两人小团队用同一条流水线并行跑 4 个栏目，风格靠变量区分，骨架完全复用', '有人只改了「润色」一步的语气变量，就把同一篇内容适配了公众号与小红书两个渠道'],
    actions: ['今晚就把你最近一篇稿的制作过程写成 5 个步骤，每步一句话', '给每个步骤配一个提示词模板，变量不超过 3 个', '连续跑 3 篇，只优化数据最差的那一步，不要全部推翻'],
    polishNotes: ['已删除 6 处冗余修饰与套话', '已将 4 个被动句改为动词前置', '段落全部压缩至 4 行以内', '保留原有论点结构，未新增观点'],
    closers: ['流程不会替你写作，但它会确保你一直在写。', '先把路修好，灵感来的时候才跑得快。', '可复制的平庸，胜过不可复制的灵光一现——何况流程之上还可以叠加灵光。']
  };

  function composeOutput(model, prompt, stepMeta, rng) {
    const vars = collectRuntimeVars();
    const topic = vars.topic || '你的主题';
    const audience = vars.audience || '目标读者';
    const tone = vars.tone || '真诚';
    const title = (stepMeta.title || '').toLowerCase();
    const kind =
      /灵感|idea/.test(title) ? 'idea' :
      /调研|research/.test(title) ? 'research' :
      /初稿|draft/.test(title) ? 'draft' :
      /润色|polish/.test(title) ? 'polish' :
      /导出|export/.test(title) ? 'export' : 'generic';

    if (kind === 'idea') {
      const lines = [];
      const used = [];
      for (let i = 1; i <= 5; i++) {
        let a; do { a = pick(rng, BANK.angles); } while (used.indexOf(a) !== -1 && used.length < BANK.angles.length);
        used.push(a);
        lines.push(i + '. ' + a + '\n   钩子：' + pick(rng, BANK.hooks));
      }
      return '主题「' + topic + '」· 面向' + audience + ' · 语气：' + tone + '\n\n' + lines.join('\n');
    }
    if (kind === 'research') {
      const lines = [];
      for (let i = 1; i <= 4; i++) {
        lines.push('▸ 素材 ' + i + '：' + pick(rng, BANK.facts) + '。\n  ' + pick(rng, BANK.cred) + ' · 来源占位：[REF-' + (100 + Math.floor(rng() * 900)) + ']');
      }
      return '围绕上一步的切入角度，补充以下可核查素材：\n\n' + lines.join('\n') + '\n\n建议：优先使用「高可信度」素材做核心论据，中等可信度素材仅作旁证。';
    }
    if (kind === 'draft') {
      return [
        pick(rng, BANK.hooks) + ' 这是关于「' + topic + '」最常被忽略的一点。',
        '核心论点：' + pick(rng, BANK.claims) + '。对' + audience + '而言，这意味着你不需要更多天赋，而是需要一条从想法直达发布的传送带。',
        '看一个案例。' + pick(rng, BANK.cases) + '。数字背后的机制很朴素：每一步只解决一个问题，输出即下一步的输入。',
        '再看一组证据：' + pick(rng, BANK.facts) + '。这不是巧合，而是流程带来的复利。',
        '行动建议：\n1) ' + pick(rng, BANK.actions) + '；\n2) ' + pick(rng, BANK.actions) + '；\n3) ' + pick(rng, BANK.actions) + '。',
        pick(rng, BANK.closers)
      ].join('\n\n');
    }
    if (kind === 'polish') {
      const prevText = extractPrev(prompt);
      const polished = prevText
        .replace(/其实|事实上|说白了|某种程度上|基本上/g, '')
        .replace(/\n{3,}/g, '\n\n')
        .trim();
      return polished + '\n\n---\n润色说明（' + model + '）：\n· ' + pick(rng, BANK.polishNotes) + '\n· ' + pick(rng, BANK.polishNotes) + '\n· 语气保持：' + tone;
    }
    if (kind === 'export') {
      const prevText = extractPrev(prompt).replace(/\n*---\n润色说明[\s\S]*$/, '').trim();
      const paras = prevText.split(/\n\n+/);
      const body = paras.map((p, i) => {
        if (i === 0) return '> ' + p.replace(/\n/g, ' ');
        if (i === 1) return '## 为什么是现在\n\n' + p;
        if (/行动建议/.test(p)) return '## 你可以立刻做的三件事\n\n' + p.replace(/^行动建议：\n?/, '');
        if (i === paras.length - 1) return '## 写在最后\n\n' + p;
        return p;
      }).join('\n\n');
      return '# ' + topic + '\n\n' + body + '\n\n---\n**如果这篇对你有用**：把它转给一位正在为“写不出来”发愁的朋友，或者留言说说你的流水线长什么样。';
    }
    // generic
    return '（' + model + '）针对指令生成的结果：\n\n' + pick(rng, BANK.claims) + '。\n\n' + pick(rng, BANK.cases) + '。\n\n' + pick(rng, BANK.closers);
  }

  function extractPrev(prompt) {
    const i = prompt.indexOf('\n');
    const j = prompt.indexOf('：\n');
    if (j !== -1) {
      const rest = prompt.slice(j + 2);
      const k = rest.lastIndexOf('\n\n要求：');
      const k2 = rest.lastIndexOf('\n\n为每个');
      if (k !== -1) return rest.slice(0, k);
      if (k2 !== -1) return rest.slice(0, k2);
      return rest;
    }
    return i !== -1 ? prompt.slice(i + 1) : prompt;
  }

  function collectRuntimeVars() {
    const v = {};
    scanVars().forEach(name => { v[name] = state.vars[name] || ''; });
    return v;
  }

  /* ---------- rendering ---------- */
  const stepsEl = $('#steps');
  const varsEl = $('#vars');
  const savedEl = $('#savedList');
  const nameEl = $('#wfName');

  function modelOptions(sel) {
    return MODELS.map(m => '<option value="' + m.id + '"' + (m.id === sel ? ' selected' : '') + '>' + esc(m.label) + '</option>').join('');
  }

  function renderSteps() {
    stepsEl.innerHTML = state.steps.map((st, i) => `
      <div class="step-card" data-id="${st.id}">
        <div class="row" style="margin-bottom:10px">
          <span class="badge-num">${i + 1}</span>
          <input type="text" class="grow" data-k="title" value="${esc(st.title)}" placeholder="步骤名称" style="max-width:240px;font-weight:600">
          <select data-k="model" style="max-width:230px">${modelOptions(st.model)}</select>
          <span class="spacer"></span>
          <span class="status queued" data-status>待运行</span>
          <button class="btn-icon btn" data-act="up" title="上移" ${i === 0 ? 'disabled' : ''}>↑</button>
          <button class="btn-icon btn" data-act="down" title="下移" ${i === state.steps.length - 1 ? 'disabled' : ''}>↓</button>
          <button class="btn-icon btn" data-act="del" title="删除">✕</button>
        </div>
        <div class="field">
          <label>提示词模板（支持 {{变量}} 与 {{prev}}）</label>
          <textarea class="code" data-k="template" rows="3">${esc(st.template)}</textarea>
        </div>
        <div class="step-out" style="display:${st.output ? 'block' : 'none'};margin-top:10px">
          <div class="small muted" style="margin-bottom:4px">输出</div>
          <pre class="output" data-out>${esc(st.output || '')}</pre>
        </div>
      </div>`).join('');
    renderVars();
  }

  function renderVars() {
    const names = scanVars();
    if (!names.length) {
      varsEl.innerHTML = '<p class="small muted mb-0">当前模板中没有检测到 {{变量}}。在任意步骤的提示词里写 <span class="mono">{{主题}}</span> 之类的占位符即可。</p>';
      return;
    }
    varsEl.innerHTML = names.map(n => `
      <div class="field">
        <label>{{${esc(n)}}}</label>
        <input type="text" data-var="${esc(n)}" value="${esc(state.vars[n] || '')}" placeholder="填写 ${esc(n)} 的值">
      </div>`).join('');
  }

  function renderSaves() {
    const saves = loadSaves();
    const names = Object.keys(saves);
    if (!names.length) {
      savedEl.innerHTML = '<p class="small muted mb-0">还没有保存过工作流。命名后点「保存当前工作流」。</p>';
      return;
    }
    savedEl.innerHTML = names.map(n => `
      <div class="subpanel row-between" data-name="${esc(n)}">
        <div>
          <strong>${esc(n)}</strong>
          <div class="small muted">${saves[n].steps.length} 步 · ${esc((saves[n].savedAt || '').slice(0, 16).replace('T', ' '))}</div>
        </div>
        <span class="row">
          <button class="btn btn-sm btn-ghost" data-load>载入</button>
          <button class="btn btn-sm btn-danger" data-del>删除</button>
        </span>
      </div>`).join('');
  }

  /* ---------- events ---------- */
  nameEl.value = state.name || '';
  nameEl.addEventListener('input', () => { state.name = nameEl.value; persist(); });

  stepsEl.addEventListener('input', e => {
    const card = e.target.closest('.step-card'); if (!card) return;
    const st = state.steps.find(s => s.id === card.dataset.id); if (!st) return;
    const k = e.target.dataset.k;
    if (k) { st[k] = e.target.value; persist(); }
    if (k === 'template') debounceVars();
  });
  stepsEl.addEventListener('change', e => {
    const card = e.target.closest('.step-card'); if (!card) return;
    const st = state.steps.find(s => s.id === card.dataset.id); if (!st) return;
    if (e.target.dataset.k === 'model') { st.model = e.target.value; persist(); }
  });
  stepsEl.addEventListener('click', e => {
    const btn = e.target.closest('[data-act]'); if (!btn) return;
    const card = btn.closest('.step-card');
    const idx = state.steps.findIndex(s => s.id === card.dataset.id);
    if (idx === -1) return;
    const act = btn.dataset.act;
    if (act === 'del') {
      if (state.steps.length <= 1) { toast('至少保留一个步骤'); return; }
      state.steps.splice(idx, 1);
    }
    if (act === 'up' && idx > 0) {
      const t = state.steps[idx - 1]; state.steps[idx - 1] = state.steps[idx]; state.steps[idx] = t;
    }
    if (act === 'down' && idx < state.steps.length - 1) {
      const t = state.steps[idx + 1]; state.steps[idx + 1] = state.steps[idx]; state.steps[idx] = t;
    }
    persist(); renderSteps();
  });

  let varsTimer;
  function debounceVars() { clearTimeout(varsTimer); varsTimer = setTimeout(renderVars, 400); }

  varsEl.addEventListener('input', e => {
    const n = e.target.dataset.var;
    if (n != null) { state.vars[n] = e.target.value; persist(); }
  });

  $('#addStep').addEventListener('click', () => {
    state.steps.push({ id: uid(), title: '新步骤 ' + (state.steps.length + 1), model: 'meridian-spark', template: '基于上一步输出：\n{{prev}}\n\n（在这里写你的指令，可用 {{topic}} 等变量）' });
    persist(); renderSteps();
    toast('已添加步骤');
  });
  $('#resetSteps').addEventListener('click', () => {
    state.steps = defaultSteps(); persist(); renderSteps();
    toast('已重置为默认五步流水线');
  });

  $('#saveWf').addEventListener('click', () => {
    const name = (state.name || '').trim();
    if (!name || name === '未命名工作流') { toast('请先给工作流起一个名字'); nameEl.focus(); return; }
    const saves = loadSaves();
    saves[name] = { name: name, vars: state.vars, steps: state.steps.map(s => ({ id: s.id, title: s.title, model: s.model, template: s.template })), savedAt: new Date().toISOString() };
    writeSaves(saves); renderSaves();
    toast('已保存「' + name + '」');
  });
  savedEl.addEventListener('click', e => {
    const item = e.target.closest('[data-name]'); if (!item) return;
    const name = item.dataset.name;
    const saves = loadSaves();
    if (e.target.closest('[data-load]')) {
      const wf = saves[name]; if (!wf) return;
      state = { name: wf.name, vars: Object.assign({}, wf.vars), steps: wf.steps.map(s => ({ id: s.id || uid(), title: s.title, model: s.model, template: s.template })) };
      nameEl.value = state.name; persist(); renderSteps();
      toast('已载入「' + name + '」');
    }
    if (e.target.closest('[data-del]')) {
      delete saves[name]; writeSaves(saves); renderSaves();
      toast('已删除「' + name + '」');
    }
  });

  /* ---------- run pipeline ---------- */
  const runBtn = $('#runBtn');
  const runStatus = $('#runStatus');
  const exportMdBtn = $('#exportMd');

  async function runPipeline() {
    if (running) return;
    running = true;
    runBtn.disabled = true;
    runStatus.className = 'status running';
    runStatus.textContent = '运行中…';
    const vars = collectRuntimeVars();
    const results = [];
    let prev = '';
    const cards = $$('.step-card', stepsEl);

    try {
      for (let i = 0; i < state.steps.length; i++) {
        const st = state.steps[i];
        const card = cards[i];
        const statusEl = card && card.querySelector('[data-status]');
        if (statusEl) { statusEl.className = 'status running'; statusEl.textContent = '生成中…'; }
        if (card) card.classList.add('running');

        const prompt = fillTemplate(st.template, Object.assign({}, vars, { prev: prev }));
        const output = await callModel(st.model, prompt, { title: st.title, index: i });

        st.output = output;
        prev = output;
        results.push({ title: st.title, model: st.model, prompt: prompt, output: output });

        if (card) {
          card.classList.remove('running'); card.classList.add('done');
          const outWrap = card.querySelector('.step-out');
          const outPre = card.querySelector('[data-out]');
          if (outWrap && outPre) { outWrap.style.display = 'block'; outPre.textContent = output; }
          if (statusEl) { statusEl.className = 'status done'; statusEl.textContent = '完成'; }
        }
      }
      lastRun = { at: new Date().toISOString(), results: results };
      runStatus.className = 'status done';
      runStatus.textContent = '全部完成 · ' + results.length + ' 步';
      exportMdBtn.disabled = false;
      persist();
      toast('流水线运行完成');
    } catch (err) {
      runStatus.className = 'status error';
      runStatus.textContent = '运行出错';
      toast('运行出错：' + err.message);
    } finally {
      running = false;
      runBtn.disabled = false;
    }
  }
  runBtn.addEventListener('click', runPipeline);

  $('#heroExample').addEventListener('click', () => {
    state = defaultState();
    state.name = '示例 · 深度文五步流水线';
    nameEl.value = state.name;
    persist(); renderSteps();
    document.getElementById('studio').scrollIntoView({ behavior: 'smooth' });
    setTimeout(runPipeline, 500);
  });

  /* ---------- exports ---------- */
  $('#exportJson').addEventListener('click', () => {
    const payload = {
      meta: { product: 'meridian-flow-create', version: 1, exportedAt: new Date().toISOString() },
      name: state.name,
      vars: collectRuntimeVars(),
      steps: state.steps.map(s => ({ title: s.title, model: s.model, template: s.template }))
    };
    download(slug(state.name) + '.workflow.json', JSON.stringify(payload, null, 2), 'application/json');
    toast('已导出工作流 JSON');
  });

  exportMdBtn.addEventListener('click', () => {
    if (!lastRun) { toast('请先运行流水线'); return; }
    const vars = collectRuntimeVars();
    const md = [
      '# ' + (state.name || 'MERIDIAN 工作流成稿'),
      '',
      '> 由 MERIDIAN Flow Create 生成 · ' + lastRun.at.slice(0, 16).replace('T', ' '),
      '',
      '**变量**：' + (Object.keys(vars).map(k => k + ' = ' + vars[k]).join(' · ') || '（无）'),
      ''
    ];
    lastRun.results.forEach((r, i) => {
      md.push('---', '', '## 步骤 ' + (i + 1) + '：' + r.title, '', '- 模型：`' + r.model + '`', '', '<details><summary>提示词</summary>', '', '```', r.prompt, '```', '', '</details>', '', r.output, '');
    });
    download(slug(state.name) + '.result.md', md.join('\n'), 'text/markdown');
    toast('已导出成稿 Markdown');
  });

  function slug(s) {
    const a = String(s || 'meridian-workflow').trim().replace(/[\\/:*?"<>|\s]+/g, '-');
    return a || 'meridian-workflow';
  }

  /* ---------- init ---------- */
  renderSteps();
  renderSaves();
})();
