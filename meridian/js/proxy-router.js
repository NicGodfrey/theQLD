/* PROXY ROUTER by MERIDIAN — weighted multi-model routing planner (local-first). */
'use strict';

const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const LS_KEY = 'meridian.proxyrouter.v1';
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
const fmt$ = n => '$' + n.toFixed(n >= 100 ? 0 : 2);

/* ---------- state ---------- */
const DEFAULT_STATE = () => ({
  domain: 'llm.example.com',
  backends: [
    { id: 'b1', name: 'gpt-4o', host: 'api.openai.com', weight: 50, prio: 1, costIn: 2.5, costOut: 10, baseMs: 480, errPct: 1, enabled: true },
    { id: 'b2', name: 'claude-sonnet', host: 'api.anthropic.com', weight: 30, prio: 2, costIn: 3, costOut: 15, baseMs: 560, errPct: 1, enabled: true },
    { id: 'b3', name: 'deepseek-v3', host: 'api.deepseek.com', weight: 20, prio: 3, costIn: 0.27, costOut: 1.1, baseMs: 900, errPct: 3, enabled: true },
  ],
  traffic: { tokIn: 120, tokOut: 30 },
  retries: 2,
});
let state = DEFAULT_STATE();
try {
  const raw = JSON.parse(localStorage.getItem(LS_KEY));
  if (raw && raw.backends) state = Object.assign(DEFAULT_STATE(), raw);
} catch (e) { /* fresh */ }
const save = () => localStorage.setItem(LS_KEY, JSON.stringify(state));

const active = () => state.backends.filter(b => b.enabled);
const totalW = () => active().reduce((a, b) => a + (+b.weight || 0), 0) || 1;
const share = b => (b.enabled ? (+b.weight || 0) / totalW() : 0);
const chain = () => [...active()].sort((a, b) => a.prio - b.prio);

/* ---------- backends UI ---------- */
function renderBackends() {
  $('#backends').innerHTML = state.backends.map(b => `
    <div class="be-card" data-id="${b.id}">
      <div class="be-head">
        <input type="text" data-f="name" value="${esc(b.name)}" title="Backend name">
        <input type="text" data-f="host" value="${esc(b.host)}" title="Host" style="flex:1;min-width:150px;font-family:var(--mono);font-size:12px">
        <input type="number" class="prio" data-f="prio" value="${b.prio}" min="1" max="9" title="Failover priority (1 = first)">
        <label class="switch" title="Enabled"><input type="checkbox" data-f="enabled" ${b.enabled ? 'checked' : ''}><span class="tr"></span></label>
        <button class="btn btn-danger btn-sm" data-act="del" title="Remove">×</button>
      </div>
      <div class="be-grid">
        <div class="cell"><label>$ / 1M in</label><input type="number" data-f="costIn" value="${b.costIn}" min="0" step="0.01"></div>
        <div class="cell"><label>$ / 1M out</label><input type="number" data-f="costOut" value="${b.costOut}" min="0" step="0.01"></div>
        <div class="cell"><label>base latency ms</label><input type="number" data-f="baseMs" value="${b.baseMs}" min="10" step="10"></div>
        <div class="cell"><label>error %</label><input type="number" data-f="errPct" value="${b.errPct}" min="0" max="100" step="0.5"></div>
      </div>
      <div class="wline">
        <input type="range" data-f="weight" min="0" max="100" value="${b.weight}" title="Traffic weight">
        <span class="pct">${Math.round(share(b) * 100)}%</span>
      </div>
    </div>`).join('') || '<p class="hint">No backends — add one.</p>';
  const ch = chain();
  $('#foChain').innerHTML = ch.length
    ? 'failover chain: ' + ch.map(b => esc(b.name)).join(' <span style="color:var(--acid)">→</span> ') + ` · ${state.retries} retries`
    : 'no active backends';
}

/* ---------- route graph (SVG) ---------- */
function renderGraph() {
  const list = state.backends;
  const H = Math.max(240, 90 + list.length * 62);
  const W = 560;
  const rx = 300, ry = H / 2;
  let s = `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" font-family="IBM Plex Mono,monospace">`;
  s += `<defs><marker id="arr" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L8 4L0 8z" fill="#C8F542"/></marker>
        <marker id="arrDim" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L8 4L0 8z" fill="#D9773F"/></marker></defs>`;
  // client node
  s += `<rect x="14" y="${ry - 24}" width="94" height="48" rx="12" fill="#132F3F" stroke="rgba(243,240,231,.25)"/>
        <text x="61" y="${ry - 2}" text-anchor="middle" font-size="12" fill="#F3F0E7">clients</text>
        <text x="61" y="${ry + 14}" text-anchor="middle" font-size="9" fill="rgba(243,240,231,.45)">sdk / app</text>`;
  // router node
  s += `<line x1="108" y1="${ry}" x2="${rx - 46}" y2="${ry}" stroke="#C8F542" stroke-width="2.4" marker-end="url(#arr)"/>
        <circle cx="${rx}" cy="${ry}" r="42" fill="#0E2836" stroke="#C8F542" stroke-width="2"/>
        <text x="${rx}" y="${ry - 4}" text-anchor="middle" font-size="11" fill="#C8F542" font-weight="600">ROUTER</text>
        <text x="${rx}" y="${ry + 12}" text-anchor="middle" font-size="9" fill="rgba(243,240,231,.5)">weighted</text>`;
  // backends
  const bx = 440;
  list.forEach((b, i) => {
    const by = 48 + i * 62;
    const pct = Math.round(share(b) * 100);
    const on = b.enabled;
    const col = on ? '#C8F542' : 'rgba(243,240,231,.18)';
    const sw = on ? Math.max(1.4, pct / 14) : 1;
    const midX = (rx + 42 + bx - 8) / 2;
    s += `<path d="M ${rx + 40} ${ry} C ${midX} ${ry}, ${midX} ${by}, ${bx - 10} ${by}" fill="none" stroke="${col}" stroke-width="${sw}" ${on ? 'marker-end="url(#arr)"' : 'stroke-dasharray="4 4"'} opacity="${on ? .9 : .5}"/>`;
    if (on) s += `<rect x="${midX - 20}" y="${(ry + by) / 2 - 10}" width="40" height="17" rx="5" fill="#0B1F2A" stroke="rgba(200,245,66,.4)"/>
                  <text x="${midX}" y="${(ry + by) / 2 + 2}" text-anchor="middle" font-size="10" fill="#C8F542">${pct}%</text>`;
    s += `<rect x="${bx}" y="${by - 21}" width="108" height="42" rx="10" fill="${on ? '#132F3F' : '#0c1d27'}" stroke="${on ? 'rgba(243,240,231,.3)' : 'rgba(243,240,231,.12)'}"/>
          <text x="${bx + 54}" y="${by - 3}" text-anchor="middle" font-size="10.5" fill="${on ? '#F3F0E7' : 'rgba(243,240,231,.35)'}">${esc(b.name.slice(0, 14))}</text>
          <text x="${bx + 54}" y="${by + 12}" text-anchor="middle" font-size="8.5" fill="rgba(243,240,231,.4)">p${b.prio} · ${b.baseMs}ms</text>`;
  });
  // failover dashed edges along chain
  const ch = chain();
  for (let i = 0; i < ch.length - 1; i++) {
    const i1 = list.indexOf(ch[i]), i2 = list.indexOf(ch[i + 1]);
    const y1 = 48 + i1 * 62, y2 = 48 + i2 * 62;
    s += `<path d="M ${bx + 112} ${y1} C ${bx + 142} ${y1}, ${bx + 142} ${y2}, ${bx + 112} ${y2}" fill="none" stroke="#D9773F" stroke-width="1.6" stroke-dasharray="5 4" marker-end="url(#arrDim)" opacity=".85"/>`;
  }
  if (ch.length > 1) {
    const midY = (48 + list.indexOf(ch[0]) * 62 + 48 + list.indexOf(ch[ch.length - 1]) * 62) / 2;
    s += `<text x="${bx + 130}" y="${midY}" font-size="8.5" fill="#D9773F" transform="rotate(90 ${bx + 148} ${midY})" text-anchor="middle">failover</text>`;
  }
  s += '</svg>';
  $('#graph').innerHTML = s;
}

/* ---------- cost table ---------- */
function renderCost() {
  const { tokIn, tokOut } = state.traffic;
  let total = 0;
  const rows = state.backends.map(b => {
    const sh = share(b);
    const cost = sh * (tokIn * b.costIn + tokOut * b.costOut);
    total += cost;
    return `<tr style="${b.enabled ? '' : 'opacity:.35'}">
      <td><b>${esc(b.name)}</b></td>
      <td style="font-family:var(--mono)">${Math.round(sh * 100)}%</td>
      <td style="font-family:var(--mono)">${b.costIn} · ${b.costOut}</td>
      <td style="font-family:var(--mono);color:var(--acid)">${fmt$(cost)}</td></tr>`;
  }).join('');
  const blend = (tokIn + tokOut) ? total / (tokIn + tokOut) : 0;
  $('#costBody').innerHTML = rows +
    `<tr><td colspan="3" style="text-align:right;color:var(--dim)">blended <span style="font-family:var(--mono)">${fmt$(blend)}/1M</span> · total</td>
     <td style="font-family:var(--mono);font-weight:600;color:var(--copper)">${fmt$(total)}/mo</td></tr>`;
}

/* ---------- latency simulation ---------- */
function logNormal() {
  // Box–Muller → exp(σZ) jitter around 1
  const u = Math.random() || 1e-9, v = Math.random();
  const z = Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
  return Math.exp(0.35 * z);
}
function pickWeighted() {
  const act = active();
  const tw = totalW();
  let roll = Math.random() * tw;
  for (const b of act) { roll -= (+b.weight || 0); if (roll <= 0) return b; }
  return act[act.length - 1];
}
function runSim() {
  const act = active();
  if (!act.length) return toast('Enable at least one backend');
  const N = parseInt($('#simN').value, 10);
  const ch = chain();
  const lats = [];
  const perBackend = {};
  let failovers = 0, hardFails = 0;
  for (let i = 0; i < N; i++) {
    let b = pickWeighted();
    let total = 0, attempts = 0, ok = false;
    while (attempts <= state.retries) {
      const lat = b.baseMs * logNormal();
      total += lat;
      if (Math.random() * 100 >= b.errPct) { ok = true; break; }
      attempts++;
      const idx = ch.indexOf(b);
      const next = ch[(idx + 1) % ch.length];
      if (next === b) break;
      b = next; failovers++;
    }
    if (!ok) { hardFails++; continue; }
    lats.push(total);
    perBackend[b.name] = (perBackend[b.name] || 0) + 1;
  }
  lats.sort((a, b) => a - b);
  const q = p => lats.length ? Math.round(lats[Math.min(lats.length - 1, Math.floor(p * lats.length))]) : 0;
  const kpis = [
    ['p50', q(0.5) + 'ms'], ['p95', q(0.95) + 'ms'], ['p99', q(0.99) + 'ms'],
    ['failovers', failovers], ['dropped', hardFails],
  ];
  $('#simKpi').innerHTML = kpis.map(([k, v]) => `<div class="stat"><div class="v">${v}</div><div class="k">${k}</div></div>`).join('');
  renderHisto(lats, perBackend, N);
  $('#simStamp').textContent = `${N} req · ${new Date().toTimeString().slice(0, 8)}`;
}
function renderHisto(lats, perBackend, N) {
  if (!lats.length) { $('#histo').innerHTML = '<p class="hint" style="padding:12px">All requests dropped — check error rates.</p>'; return; }
  const W = 900, H = 220, PAD = 34;
  const max = lats[lats.length - 1];
  const BINS = 36;
  const bins = new Array(BINS).fill(0);
  lats.forEach(l => bins[Math.min(BINS - 1, Math.floor((l / max) * BINS))]++);
  const bmax = Math.max(...bins);
  const bw = (W - PAD * 2) / BINS;
  let s = `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" font-family="IBM Plex Mono,monospace">`;
  bins.forEach((c, i) => {
    const h = c / bmax * (H - 70);
    const hot = (i / BINS) * max > lats[Math.floor(0.95 * lats.length)] * 0.999;
    s += `<rect x="${PAD + i * bw + 1}" y="${H - 38 - h}" width="${bw - 2}" height="${h}" rx="2" fill="${hot ? '#D9773F' : '#C8F542'}" opacity="${hot ? .85 : .8}"/>`;
  });
  s += `<line x1="${PAD}" y1="${H - 38}" x2="${W - PAD}" y2="${H - 38}" stroke="rgba(243,240,231,.25)"/>`;
  [0, 0.25, 0.5, 0.75, 1].forEach(p => {
    s += `<text x="${PAD + p * (W - PAD * 2)}" y="${H - 20}" text-anchor="middle" font-size="10" fill="rgba(243,240,231,.45)">${Math.round(p * max)}ms</text>`;
  });
  const served = Object.entries(perBackend).map(([n, c]) => `${n} ${Math.round(c / N * 100)}%`).join(' · ');
  s += `<text x="${PAD}" y="18" font-size="11" fill="rgba(243,240,231,.6)">served: ${esc(served)}</text>`;
  s += `<text x="${W - PAD}" y="18" text-anchor="end" font-size="10" fill="#D9773F">▮ above p95</text>`;
  s += '</svg>';
  $('#histo').innerHTML = s;
}

/* ---------- config generation ---------- */
function genCaddy() {
  const act = active();
  const ups = act.map(b => `        to https://${b.host}`).join('\n');
  const weights = act.map(b => Math.max(1, Math.round(share(b) * 100))).join(' ');
  return `# Caddyfile — generated by PROXY ROUTER by MERIDIAN
# ${new Date().toISOString()}
# caddy 2.8+ — weighted_round_robin carries your tuned split.

${state.domain} {
    encode zstd gzip

    reverse_proxy /v1/* {
${ups}

        lb_policy weighted_round_robin ${weights}
        lb_try_duration 4s
        lb_retries ${state.retries}

        health_uri /v1/models
        health_interval 15s
        health_timeout 4s

        header_up Host {upstream_hostport}
        transport http {
            tls
            tls_server_name {upstream_hostport}
            read_timeout 300s
        }

        # streaming (SSE)
        flush_interval -1
    }

    handle {
        respond "proxy-router: route not found" 404
    }

    log {
        output file /var/log/caddy/router.log
        format json
    }
}`;
}
function genNginx() {
  const act = active();
  const ch = chain();
  const servers = act.map(b => {
    const w = Math.max(1, Math.round(share(b) * 100));
    const backup = ch.indexOf(b) > 0 && share(b) === 0 ? ' backup' : '';
    return `    server ${b.host}:443 weight=${w} max_fails=2 fail_timeout=15s${backup};   # ${b.name}`;
  }).join('\n');
  return `# nginx.conf (http context) — generated by PROXY ROUTER by MERIDIAN
# ${new Date().toISOString()}

upstream model_pool {
${servers}
    keepalive 32;
}

server {
    listen 443 ssl;
    http2 on;
    server_name ${state.domain};

    ssl_certificate     /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;

    location /v1/ {
        proxy_pass https://model_pool;
        proxy_http_version 1.1;
        proxy_ssl_server_name on;
        proxy_set_header Connection "";

        # failover: retry next upstream on failure (${state.retries} tries)
        proxy_next_upstream error timeout http_502 http_503 http_429;
        proxy_next_upstream_tries ${state.retries + 1};
        proxy_next_upstream_timeout 10s;

        # streaming (SSE)
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 300s;
    }

    location / { return 404; }
}`;
}
function genTraefik() {
  const act = active();
  const svcList = act.map(b => `          - name: svc-${b.name.replace(/[^a-z0-9]+/gi, '-').toLowerCase()}
            weight: ${Math.max(1, Math.round(share(b) * 100))}`).join('\n');
  const services = act.map(b => {
    const key = 'svc-' + b.name.replace(/[^a-z0-9]+/gi, '-').toLowerCase();
    return `    ${key}:
      loadBalancer:
        serversTransport: tls-sni
        servers:
          - url: "https://${b.host}"
        healthCheck:
          path: /v1/models
          interval: 15s
          timeout: 4s`;
  }).join('\n');
  return `# traefik-dynamic.yml — generated by PROXY ROUTER by MERIDIAN
# ${new Date().toISOString()}
http:
  routers:
    model-router:
      rule: "Host(\`${state.domain}\`) && PathPrefix(\`/v1\`)"
      entryPoints: [websecure]
      tls: {}
      service: model-pool

  services:
    model-pool:
      weighted:
        services:
${svcList}

${services}

  serversTransports:
    tls-sni:
      serverName: ""
      insecureSkipVerify: false`;
}
const CFG = {
  caddy:   { name: 'Caddyfile', gen: genCaddy },
  nginx:   { name: 'router-nginx.conf', gen: genNginx },
  traefik: { name: 'traefik-dynamic.yml', gen: genTraefik },
};
let cfgTab = 'caddy';
const renderCfg = () => { $('#cfgOut').textContent = CFG[cfgTab].gen(); };

/* ---------- events ---------- */
function rerenderAll() { renderBackends(); renderGraph(); renderCost(); renderCfg(); }

$('#btnAddBe').addEventListener('click', () => {
  state.backends.push({ id: uid('b'), name: 'backend-' + (state.backends.length + 1), host: 'api.example.com', weight: 10, prio: state.backends.length + 1, costIn: 1, costOut: 3, baseMs: 600, errPct: 2, enabled: true });
  save(); rerenderAll();
});
$('#btnNormalize').addEventListener('click', () => {
  const act = active();
  if (!act.length) return;
  const even = Math.floor(100 / act.length);
  act.forEach((b, i) => { b.weight = i === 0 ? 100 - even * (act.length - 1) : even; });
  save(); rerenderAll(); toast('Weights normalized');
});
$('#backends').addEventListener('click', e => {
  const btn = e.target.closest('[data-act="del"]');
  if (!btn) return;
  const id = btn.closest('.be-card').dataset.id;
  state.backends = state.backends.filter(b => b.id !== id);
  save(); rerenderAll();
});
$('#backends').addEventListener('input', e => {
  const inp = e.target.closest('[data-f]');
  if (!inp) return;
  const card = inp.closest('.be-card');
  const b = state.backends.find(x => x.id === card.dataset.id);
  if (!b) return;
  const f = inp.dataset.f;
  if (inp.type === 'checkbox') b[f] = inp.checked;
  else if (inp.type === 'number' || inp.type === 'range') b[f] = parseFloat(inp.value) || 0;
  else b[f] = inp.value;
  save();
  if (f === 'weight') {
    // live-update percentage labels without rebuilding (keeps slider drag smooth)
    $$('#backends .be-card').forEach(c => {
      const bb = state.backends.find(x => x.id === c.dataset.id);
      c.querySelector('.pct').textContent = Math.round(share(bb) * 100) + '%';
    });
    renderGraph(); renderCost(); renderCfg();
  } else if (f === 'enabled' || f === 'prio' || f === 'name') { rerenderAll(); }
  else { renderCost(); renderCfg(); }
});
['tokIn', 'tokOut'].forEach(id => $('#' + id).addEventListener('input', () => {
  state.traffic.tokIn = Math.max(0, parseFloat($('#tokIn').value) || 0);
  state.traffic.tokOut = Math.max(0, parseFloat($('#tokOut').value) || 0);
  save(); renderCost();
}));
$('#btnRunSim').addEventListener('click', runSim);
$('#cfgTabs').addEventListener('click', e => {
  const b = e.target.closest('[data-cfg]');
  if (!b) return;
  cfgTab = b.dataset.cfg;
  $$('#cfgTabs button').forEach(x => x.classList.toggle('on', x === b));
  renderCfg();
});
$('#btnDlCfg').addEventListener('click', () => { const f = CFG[cfgTab]; download(f.name, f.gen()); toast(f.name + ' downloaded'); });
$('#btnCopyCfg').addEventListener('click', () => {
  navigator.clipboard && navigator.clipboard.writeText(CFG[cfgTab].gen()).then(() => toast('Copied')).catch(() => toast('Copy failed'));
});
$('#btnExportState').addEventListener('click', () => {
  download('proxy-router-state.json', JSON.stringify({ tool: 'PROXY ROUTER by MERIDIAN', version: 1, exportedAt: new Date().toISOString(), ...state }, null, 2), 'application/json');
  toast('Router state exported');
});

/* ---------- boot ---------- */
(function boot() {
  $('#tokIn').value = state.traffic.tokIn;
  $('#tokOut').value = state.traffic.tokOut;
  rerenderAll();
  runSim();
})();
