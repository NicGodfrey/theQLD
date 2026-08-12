/* PROXY GATE by MERIDIAN — AI API reverse-proxy gateway console (local-first). */
'use strict';

const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const LS_KEY = 'meridian.proxygate.v1';
const uid = p => p + Math.random().toString(36).slice(2, 8);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
function download(name, text, mime = 'text/plain') {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([text], { type: mime }));
  a.download = name; a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 4000);
}
let toastT = null;
function toast(msg) {
  const t = $('#toast'); t.textContent = msg; t.classList.add('show');
  clearTimeout(toastT); toastT = setTimeout(() => t.classList.remove('show'), 1800);
}

/* ---------- provider presets ---------- */
const PROVIDERS = {
  openai:   { label: 'OpenAI',   base: 'https://api.openai.com',                       host: 'api.openai.com',                       auth: 'Authorization: Bearer' },
  anthropic:{ label: 'Claude',   base: 'https://api.anthropic.com',                    host: 'api.anthropic.com',                    auth: 'x-api-key' },
  gemini:   { label: 'Gemini',   base: 'https://generativelanguage.googleapis.com',    host: 'generativelanguage.googleapis.com',    auth: 'x-goog-api-key' },
  deepseek: { label: 'DeepSeek', base: 'https://api.deepseek.com',                     host: 'api.deepseek.com',                     auth: 'Authorization: Bearer' },
  custom:   { label: 'Custom',   base: 'https://llm.internal.example',                 host: 'llm.internal.example',                 auth: 'Authorization: Bearer' },
};

/* ---------- state ---------- */
const DEFAULT_STATE = () => ({
  upstreams: [
    { id: 'up1', name: 'openai-main', kind: 'openai', baseUrl: PROVIDERS.openai.base, keySlot: 'k1', enabled: true },
    { id: 'up2', name: 'claude-fallback', kind: 'anthropic', baseUrl: PROVIDERS.anthropic.base, keySlot: 'k2', enabled: true },
  ],
  keys: [
    { id: 'k1', label: 'OPENAI_PRIMARY', value: '' },
    { id: 'k2', label: 'ANTHROPIC_PRIMARY', value: '' },
  ],
  routes: [
    { id: 'r1', path: '/v1/chat/completions', upstreamId: 'up1', rewriteModel: '', streaming: true },
    { id: 'r2', path: '/v1/embeddings', upstreamId: 'up1', rewriteModel: 'text-embedding-3-small', streaming: false },
    { id: 'r3', path: '/anthropic/v1/messages', upstreamId: 'up2', rewriteModel: '', streaming: true },
  ],
  security: {
    rpm: 60, burst: 20, keyBy: 'ip',
    allowlist: [
      { id: 'ip1', cidr: '10.0.0.0/8', note: 'office VPN' },
      { id: 'ip2', cidr: '203.0.113.42/32', note: 'staging box' },
    ],
  },
  serverName: 'gateway.example.com',
  logs: [],
  simTotals: { total: 0, errors: 0 },
});
let state = DEFAULT_STATE();
try {
  const raw = JSON.parse(localStorage.getItem(LS_KEY));
  if (raw && raw.upstreams) state = Object.assign(DEFAULT_STATE(), raw);
} catch (e) { /* fresh */ }
const save = () => localStorage.setItem(LS_KEY, JSON.stringify(state));

/* ---------- render: lists ---------- */
const maskKey = v => !v ? '(empty — export uses env var)' : v.length <= 6 ? '•'.repeat(v.length) : v.slice(0, 3) + '•'.repeat(Math.min(14, v.length - 6)) + v.slice(-3);

function renderUpstreams() {
  $('#upstreams').innerHTML = state.upstreams.map(u => `
    <div class="itemrow up-row" data-id="${u.id}">
      <input type="text" data-f="name" value="${esc(u.name)}" placeholder="name" title="Upstream name">
      <select data-f="kind" title="Provider">${Object.entries(PROVIDERS).map(([k, p]) => `<option value="${k}" ${u.kind === k ? 'selected' : ''}>${p.label}</option>`).join('')}</select>
      <input type="url" data-f="baseUrl" value="${esc(u.baseUrl)}" placeholder="base url" title="Base URL">
      <select data-f="keySlot" title="Key slot">
        <option value="">— no key —</option>
        ${state.keys.map(k => `<option value="${k.id}" ${u.keySlot === k.id ? 'selected' : ''}>${esc(k.label)}</option>`).join('')}
      </select>
      <label class="switch" title="Enabled"><input type="checkbox" data-f="enabled" ${u.enabled ? 'checked' : ''}><span class="tr"></span></label>
      <button class="btn btn-danger btn-sm kill" data-act="del-up" title="Remove">×</button>
    </div>`).join('') || '<p class="hint">No upstreams. Add one to start routing.</p>';
  $('#statUp').textContent = state.upstreams.filter(u => u.enabled).length;
}
function renderKeys() {
  $('#keys').innerHTML = state.keys.map(k => `
    <div class="itemrow key-row" data-id="${k.id}">
      <input type="text" data-f="label" value="${esc(k.label)}" placeholder="ENV_NAME" title="Slot label (becomes env var)">
      <input type="password" data-f="value" value="${esc(k.value)}" placeholder="${esc(maskKey(k.value))}" title="Secret value (stays in this browser)">
      <button class="btn btn-sm" data-act="reveal" title="Show / hide">👁</button>
      <button class="btn btn-danger btn-sm kill" data-act="del-key" title="Remove">×</button>
    </div>`).join('') || '<p class="hint">No key slots yet.</p>';
}
function renderRoutes() {
  $('#routes').innerHTML = state.routes.map(r => `
    <div class="itemrow route-row" data-id="${r.id}">
      <input type="text" data-f="path" value="${esc(r.path)}" placeholder="/v1/chat/completions" title="Inbound path">
      <select data-f="upstreamId" title="Upstream">
        ${state.upstreams.map(u => `<option value="${u.id}" ${r.upstreamId === u.id ? 'selected' : ''}>${esc(u.name)}</option>`).join('')}
      </select>
      <input type="text" data-f="rewriteModel" value="${esc(r.rewriteModel)}" placeholder="model pin (opt)" title="Force model">
      <label class="switch" title="SSE streaming"><input type="checkbox" data-f="streaming" ${r.streaming ? 'checked' : ''}><span class="tr"></span></label>
      <button class="btn btn-danger btn-sm kill" data-act="del-route" title="Remove">×</button>
    </div>`).join('') || '<p class="hint">No routes yet.</p>';
  $('#statRoutes').textContent = state.routes.length;
}
function renderAllowlist() {
  $('#allowlist').innerHTML = state.security.allowlist.map(a => `
    <div class="itemrow ip-row" data-id="${a.id}">
      <input type="text" data-f="cidr" value="${esc(a.cidr)}" placeholder="203.0.113.0/24" title="CIDR">
      <input type="text" data-f="note" value="${esc(a.note)}" placeholder="note" title="Note">
      <button class="btn btn-danger btn-sm kill" data-act="del-ip" title="Remove">×</button>
    </div>`).join('') || '<p class="hint">Empty allowlist = open to the world (export adds a warning).</p>';
}
function renderSecurity() {
  $('#rlRpm').value = state.security.rpm;
  $('#rlBurst').value = state.security.burst;
  $('#rlKey').value = state.security.keyBy;
}

/* ---------- config generation ---------- */
const envName = k => 'PG_KEY_' + (k.label || 'SLOT').replace(/[^A-Za-z0-9]+/g, '_').toUpperCase();
const upHost = u => { try { return new URL(u.baseUrl).host; } catch (e) { return (PROVIDERS[u.kind] || PROVIDERS.custom).host; } };

function genNginx() {
  const s = state.security;
  const key = s.keyBy === 'ip' ? '$binary_remote_addr' : '$http_x_api_key';
  const lines = [];
  lines.push('# =============================================================');
  lines.push('# gateway.conf.template — generated by PROXY GATE by MERIDIAN');
  lines.push(`# ${new Date().toISOString()}`);
  lines.push('# Rendered by the official nginx image via envsubst at startup.');
  lines.push('# =============================================================');
  lines.push('');
  lines.push(`limit_req_zone ${key} zone=pg_ratelimit:10m rate=${s.rpm}r/m;`);
  lines.push('');
  lines.push('map $http_upgrade $connection_upgrade {');
  lines.push('    default upgrade;');
  lines.push("    ''      close;");
  lines.push('}');
  lines.push('');
  lines.push('server {');
  lines.push('    listen 443 ssl;');
  lines.push('    http2 on;');
  lines.push(`    server_name ${state.serverName};`);
  lines.push('');
  lines.push('    ssl_certificate     /etc/nginx/certs/fullchain.pem;');
  lines.push('    ssl_certificate_key /etc/nginx/certs/privkey.pem;');
  lines.push('    ssl_protocols TLSv1.2 TLSv1.3;');
  lines.push('');
  lines.push('    # --- hardening ---');
  lines.push('    server_tokens off;');
  lines.push('    client_max_body_size 10m;');
  lines.push('    add_header X-Content-Type-Options nosniff always;');
  lines.push('    add_header Referrer-Policy no-referrer always;');
  lines.push('');
  if (s.allowlist.length) {
    lines.push('    # --- IP allowlist ---');
    s.allowlist.forEach(a => lines.push(`    allow ${a.cidr};${a.note ? '   # ' + a.note : ''}`));
    lines.push('    deny  all;');
  } else {
    lines.push('    # !! No IP allowlist configured — gateway is reachable from anywhere.');
  }
  lines.push('');
  lines.push('    # --- health ---');
  lines.push("    location = /healthz { return 200 'ok'; add_header Content-Type text/plain; }");
  state.routes.forEach(r => {
    const u = state.upstreams.find(x => x.id === r.upstreamId);
    if (!u || !u.enabled) return;
    const host = upHost(u);
    const keySlot = state.keys.find(k => k.id === u.keySlot);
    const p = PROVIDERS[u.kind] || PROVIDERS.custom;
    let base; try { base = new URL(u.baseUrl); } catch (e) { base = { pathname: '' }; }
    const upstreamPath = (base.pathname && base.pathname !== '/' ? base.pathname.replace(/\/$/, '') : '') + r.path.replace(/^\/(openai|anthropic|gemini|deepseek|custom)/, '');
    lines.push('');
    lines.push(`    # route: ${r.path}  →  ${u.name} (${p.label})`);
    lines.push(`    location = ${r.path} {`);
    lines.push(`        limit_req zone=pg_ratelimit burst=${s.burst} nodelay;`);
    lines.push(`        limit_req_status 429;`);
    lines.push('');
    lines.push(`        proxy_pass https://${host}${upstreamPath};`);
    lines.push('        proxy_http_version 1.1;');
    lines.push('        proxy_ssl_server_name on;');
    lines.push(`        proxy_set_header Host ${host};`);
    lines.push('        proxy_set_header Connection "";');
    if (keySlot) {
      if (p.auth === 'x-api-key') {
        lines.push(`        proxy_set_header x-api-key "\${${envName(keySlot)}}";`);
        lines.push('        proxy_set_header anthropic-version "2023-06-01";');
      } else if (p.auth === 'x-goog-api-key') {
        lines.push(`        proxy_set_header x-goog-api-key "\${${envName(keySlot)}}";`);
      } else {
        lines.push(`        proxy_set_header Authorization "Bearer \${${envName(keySlot)}}";`);
      }
      lines.push('        # strip whatever credential the client sent');
      lines.push('        proxy_set_header X-Api-Key "";');
    }
    if (r.rewriteModel) lines.push(`        # model pinned to "${r.rewriteModel}" — enforce in app layer or njs body filter`);
    if (r.streaming) {
      lines.push('        # SSE / token streaming');
      lines.push('        proxy_buffering off;');
      lines.push('        proxy_cache off;');
      lines.push('        proxy_read_timeout 300s;');
    } else {
      lines.push('        proxy_read_timeout 120s;');
    }
    lines.push('    }');
  });
  lines.push('');
  lines.push('    location / { return 404; }');
  lines.push('}');
  lines.push('');
  lines.push('# HTTP → HTTPS redirect');
  lines.push('server {');
  lines.push('    listen 80;');
  lines.push(`    server_name ${state.serverName};`);
  lines.push('    return 301 https://$host$request_uri;');
  lines.push('}');
  return lines.join('\n');
}
function genCompose() {
  return `# docker-compose.yml — generated by PROXY GATE by MERIDIAN
# ${new Date().toISOString()}
services:
  gateway:
    image: nginx:1.27-alpine
    container_name: proxy-gate
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    env_file:
      - .env
    volumes:
      # nginx image runs envsubst on /etc/nginx/templates/*.template at boot
      - ./gateway.conf.template:/etc/nginx/templates/gateway.conf.template:ro
      - ./certs:/etc/nginx/certs:ro
      - gateway-cache:/var/cache/nginx
    healthcheck:
      test: ["CMD", "wget", "-qO-", "--no-check-certificate", "https://localhost/healthz"]
      interval: 30s
      timeout: 5s
      retries: 3
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "5"

volumes:
  gateway-cache:
`;
}
function genEnv() {
  const lines = [
    '# .env.example — generated by PROXY GATE by MERIDIAN',
    '# Copy to .env and fill with real credentials. NEVER commit .env.',
    '',
  ];
  state.keys.forEach(k => {
    const local = k.value ? `   # slot filled locally (${maskKey(k.value)})` : '   # empty slot';
    lines.push(`${envName(k)}=sk-replace-me${local}`);
  });
  if (!state.keys.length) lines.push('# (no key slots configured)');
  lines.push('');
  lines.push('# envsubst needs the vars listed here:');
  lines.push(`NGINX_ENVSUBST_TEMPLATE_SUFFIX=.template`);
  return lines.join('\n');
}
const CFG_FILES = {
  nginx:   { name: 'gateway.conf.template', gen: genNginx },
  compose: { name: 'docker-compose.yml',    gen: genCompose },
  env:     { name: '.env.example',          gen: genEnv },
};
let cfgTab = 'nginx';
function renderCfg() { $('#cfgOut').textContent = CFG_FILES[cfgTab].gen(); }

/* ---------- log simulator ---------- */
let simTimer = null;
let obsWindow = [];
const IPS_OK = () => state.security.allowlist.map(a => a.cidr.split('/')[0]);
const IPS_BAD = ['45.83.12.9', '91.240.118.4', '185.220.101.7'];
function simOne(force = {}) {
  if (!state.routes.length) return null;
  const r = state.routes[Math.floor(Math.random() * state.routes.length)];
  const u = state.upstreams.find(x => x.id === r.upstreamId);
  const okIps = IPS_OK();
  const useBadIp = state.security.allowlist.length && Math.random() < 0.12;
  const ip = useBadIp ? IPS_BAD[Math.floor(Math.random() * IPS_BAD.length)]
    : okIps.length ? okIps[Math.floor(Math.random() * okIps.length)] : '198.51.100.' + (1 + Math.floor(Math.random() * 250));
  // observed rpm over last 60s
  const now = Date.now();
  obsWindow = obsWindow.filter(t => now - t < 60000);
  obsWindow.push(now);
  const overLimit = obsWindow.length > state.security.rpm + state.security.burst;
  let status;
  if (useBadIp) status = 403;
  else if (force.status) status = force.status;
  else if (overLimit && Math.random() < 0.8) status = 429;
  else if (!u || !u.enabled) status = 502;
  else {
    const roll = Math.random();
    status = roll < 0.9 ? 200 : roll < 0.94 ? 401 : roll < 0.97 ? 429 : 502;
  }
  const latency = status === 403 ? 2 + Math.random() * 4 : status === 429 ? 1 + Math.random() * 3 :
    Math.round(180 + Math.random() * (r.streaming ? 2200 : 900));
  const tokens = status === 200 ? Math.round(80 + Math.random() * 1800) : 0;
  const entry = {
    t: new Date().toTimeString().slice(0, 8),
    method: 'POST', path: r.path, up: u ? u.name : '—',
    status, latency: Math.round(latency), tokens, ip,
  };
  state.logs.push(entry);
  if (state.logs.length > 400) state.logs.splice(0, state.logs.length - 400);
  state.simTotals.total++;
  if (status >= 400) state.simTotals.errors++;
  return entry;
}
function renderLog(scroll = true) {
  const wrap = $('#logwrap');
  wrap.innerHTML = state.logs.slice(-200).map(l => {
    const cls = l.status < 400 ? 'st-2xx' : l.status < 500 ? 'st-4xx' : 'st-5xx';
    return `<div class="logline"><span class="t">${l.t}</span><span class="st ${cls}">${l.status}</span><span class="m">${l.method}</span><span class="p">${esc(l.path)}</span><span class="u">→ ${esc(l.up)}</span><span class="u">${l.ip}</span><span class="lat">${l.latency}ms · ${l.tokens}tok</span></div>`;
  }).join('') || '<span style="color:var(--dim-2)">No traffic yet. Hit “Start traffic” to simulate load against your routes.</span>';
  if (scroll) wrap.scrollTop = wrap.scrollHeight;
  const tot = state.simTotals.total || 0;
  $('#statReq').textContent = tot > 999 ? (tot / 1000).toFixed(1) + 'k' : tot;
  $('#statErr').textContent = tot ? Math.round((state.simTotals.errors / tot) * 100) + '%' : '0%';
  $('#chipRate').textContent = `${obsWindow.length} rpm observed / limit ${state.security.rpm}+${state.security.burst}`;
}
function setSim(on) {
  if (on && !simTimer) {
    simTimer = setInterval(() => { simOne(); renderLog(); save(); }, 650);
    $('#btnSim').textContent = '⏸ Stop traffic';
    $('#pulse').classList.add('live');
  } else if (!on && simTimer) {
    clearInterval(simTimer); simTimer = null;
    $('#btnSim').textContent = '▶ Start traffic';
    $('#pulse').classList.remove('live');
  }
}

/* ---------- events ---------- */
$('#btnAddUp').addEventListener('click', () => {
  state.upstreams.push({ id: uid('up'), name: 'upstream-' + (state.upstreams.length + 1), kind: 'openai', baseUrl: PROVIDERS.openai.base, keySlot: '', enabled: true });
  save(); renderUpstreams(); renderRoutes(); renderCfg();
});
$('#btnAddKey').addEventListener('click', () => {
  state.keys.push({ id: uid('k'), label: 'KEY_' + (state.keys.length + 1), value: '' });
  save(); renderKeys(); renderUpstreams(); renderCfg();
});
$('#btnAddRoute').addEventListener('click', () => {
  if (!state.upstreams.length) return toast('Add an upstream first');
  state.routes.push({ id: uid('r'), path: '/v1/route-' + (state.routes.length + 1), upstreamId: state.upstreams[0].id, rewriteModel: '', streaming: true });
  save(); renderRoutes(); renderCfg();
});
$('#btnAddIp').addEventListener('click', () => {
  state.security.allowlist.push({ id: uid('ip'), cidr: '192.0.2.0/24', note: '' });
  save(); renderAllowlist(); renderCfg();
});

document.addEventListener('click', e => {
  const btn = e.target.closest('[data-act]');
  if (!btn) return;
  const row = btn.closest('.itemrow');
  const id = row && row.dataset.id;
  const act = btn.dataset.act;
  if (act === 'del-up') { state.upstreams = state.upstreams.filter(u => u.id !== id); state.routes.forEach(r => { if (r.upstreamId === id) r.upstreamId = state.upstreams[0]?.id || ''; }); renderUpstreams(); renderRoutes(); }
  else if (act === 'del-key') { state.keys = state.keys.filter(k => k.id !== id); state.upstreams.forEach(u => { if (u.keySlot === id) u.keySlot = ''; }); renderKeys(); renderUpstreams(); }
  else if (act === 'del-route') { state.routes = state.routes.filter(r => r.id !== id); renderRoutes(); }
  else if (act === 'del-ip') { state.security.allowlist = state.security.allowlist.filter(a => a.id !== id); renderAllowlist(); }
  else if (act === 'reveal') {
    const inp = row.querySelector('input[data-f="value"]');
    inp.type = inp.type === 'password' ? 'text' : 'password';
    return;
  }
  save(); renderCfg();
});

document.addEventListener('input', e => {
  const inp = e.target.closest('.itemrow [data-f]');
  if (!inp) return;
  const row = inp.closest('.itemrow'); const id = row.dataset.id; const f = inp.dataset.f;
  const val = inp.type === 'checkbox' ? inp.checked : inp.value;
  const coll = row.classList.contains('up-row') ? state.upstreams
    : row.classList.contains('key-row') ? state.keys
    : row.classList.contains('route-row') ? state.routes
    : state.security.allowlist;
  const item = coll.find(x => x.id === id);
  if (!item) return;
  item[f] = val;
  if (f === 'kind' && PROVIDERS[val]) {
    item.baseUrl = PROVIDERS[val].base;
    row.querySelector('input[data-f="baseUrl"]').value = item.baseUrl;
  }
  save(); renderCfg();
  if (f === 'name' || f === 'label') { renderUpstreams(); renderRoutes(); }
  if (f === 'enabled') renderUpstreams();
});

['rlRpm', 'rlBurst', 'rlKey'].forEach(idSel => {
  $('#' + idSel).addEventListener('input', () => {
    state.security.rpm = Math.max(1, parseInt($('#rlRpm').value, 10) || 60);
    state.security.burst = Math.max(0, parseInt($('#rlBurst').value, 10) || 0);
    state.security.keyBy = $('#rlKey').value;
    save(); renderCfg(); renderLog(false);
  });
});

$('#cfgTabs').addEventListener('click', e => {
  const b = e.target.closest('[data-cfg]');
  if (!b) return;
  cfgTab = b.dataset.cfg;
  $$('#cfgTabs button').forEach(x => x.classList.toggle('on', x === b));
  renderCfg();
});
$('#btnDlCfg').addEventListener('click', () => { const f = CFG_FILES[cfgTab]; download(f.name, f.gen()); toast(f.name + ' downloaded'); });
$('#btnDlAll').addEventListener('click', () => {
  Object.values(CFG_FILES).forEach((f, i) => setTimeout(() => download(f.name, f.gen()), i * 250));
  toast('Deploy bundle downloading (3 files)');
});
$('#btnCopyCfg').addEventListener('click', () => {
  navigator.clipboard && navigator.clipboard.writeText(CFG_FILES[cfgTab].gen()).then(() => toast('Copied')).catch(() => toast('Copy failed'));
});

$('#btnSim').addEventListener('click', () => setSim(!simTimer));
$('#btnBurst').addEventListener('click', () => {
  for (let i = 0; i < 20; i++) simOne();
  renderLog(); save(); toast('Burst of 20 requests fired');
});
$('#btnClearLog').addEventListener('click', () => {
  state.logs = []; state.simTotals = { total: 0, errors: 0 }; obsWindow = [];
  save(); renderLog(); toast('Log cleared');
});

/* ---------- boot ---------- */
(function boot() {
  renderUpstreams(); renderKeys(); renderRoutes(); renderAllowlist(); renderSecurity();
  renderCfg(); renderLog(false);
})();
