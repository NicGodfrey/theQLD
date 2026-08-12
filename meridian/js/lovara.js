/* LOVARA by MERIDIAN — AI design agent (local, deterministic-seeded). */
'use strict';

const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const LS_KEY = 'meridian.lovara.v1';

/* ---------- utils ---------- */
function hashStr(str) {
  let h = 2166136261;
  for (let i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); }
  return h >>> 0;
}
function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const rnd = (r, a, b) => a + r() * (b - a);
const pick = (r, arr) => arr[Math.floor(r() * arr.length)];
function hslHex(h, s, l) {
  h = ((h % 360) + 360) % 360; s = Math.max(0, Math.min(100, s)) / 100; l = Math.max(0, Math.min(100, l)) / 100;
  const k = n => (n + h / 30) % 12;
  const a = s * Math.min(l, 1 - l);
  const f = n => l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)));
  const to = x => Math.round(255 * x).toString(16).padStart(2, '0');
  return ('#' + to(f(0)) + to(f(8)) + to(f(4))).toUpperCase();
}
function luminance(hex) {
  const n = parseInt(hex.slice(1), 16);
  const r = (n >> 16) & 255, g = (n >> 8) & 255, b = n & 255;
  return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255;
}
const textOn = hex => (luminance(hex) > 0.55 ? '#0B1F2A' : '#F3F0E7');
const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
function download(name, text, mime = 'text/plain') {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([text], { type: mime }));
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 4000);
}
let toastT = null;
function toast(msg) {
  const t = $('#toast'); t.textContent = msg; t.classList.add('show');
  clearTimeout(toastT); toastT = setTimeout(() => t.classList.remove('show'), 1800);
}

/* ---------- creative data ---------- */
const VIBES = {
  electric:  { hue: [72, 205], sat: [68, 95], dark: true,  shapes: ['bars', 'rings', 'orbs'] },
  editorial: { hue: [18, 62],  sat: [10, 28], dark: false, shapes: ['rules', 'blocks'] },
  brutalist: { hue: [0, 360],  sat: [0, 10],  dark: true,  shapes: ['blocks', 'bars'] },
  organic:   { hue: [66, 168], sat: [24, 52], dark: false, shapes: ['blobs', 'orbs'] },
  luxe:      { hue: [18, 46],  sat: [34, 68], dark: true,  shapes: ['rings', 'rules'] },
  playful:   { hue: [0, 360],  sat: [62, 92], dark: false, shapes: ['orbs', 'blobs'] },
};
const TYPE_PAIRS = [
  { display: 'Bricolage Grotesque', body: 'IBM Plex Sans',   note: 'House pairing — confident grotesque over engineered sans.' },
  { display: 'Clash Display',       body: 'Archivo',          note: 'Sharp fashion display with a sturdy workhorse.' },
  { display: 'Space Grotesk',       body: 'Inter',            note: 'Techy curves, neutral reading rhythm.' },
  { display: 'Fraunces',            body: 'Work Sans',        note: 'Wonky serif warmth against clean geometry.' },
  { display: 'Unbounded',           body: 'Manrope',          note: 'Wide futurist headline, soft humanist body.' },
  { display: 'Zodiak',              body: 'General Sans',     note: 'Editorial serif with quiet contemporary support.' },
  { display: 'Monument Extended',   body: 'Roboto Mono',      note: 'Billboard weight display, terminal-precise captions.' },
  { display: 'Gambetta',            body: 'Karla',            note: 'Literary italic energy, friendly and legible below.' },
  { display: 'Cabinet Grotesk',     body: 'IBM Plex Sans',    note: 'Rounded authority over systematic body text.' },
  { display: 'Bodoni Moda',         body: 'IBM Plex Mono',    note: 'High-contrast luxury cut against raw mono.' },
];
const LAYER_DEFS = [
  { id: 'bg',       name: 'Base fill',        kind: 'fill' },
  { id: 'wash',     name: 'Atmosphere wash',  kind: 'fx' },
  { id: 'grid',     name: 'Grid rules',       kind: 'guide' },
  { id: 'shapes',   name: 'Composition',      kind: 'vector' },
  { id: 'content',  name: 'Type & content',   kind: 'text' },
  { id: 'swatches', name: 'Palette strip',    kind: 'spec' },
  { id: 'mark',     name: 'LOVARA mark',      kind: 'brand' },
];
const STOP = new Set(['for', 'the', 'and', 'with', 'a', 'an', 'of', 'to', 'in', 'on', 'that', 'this', 'its', 'is', 'are', 'bit', 'very']);

/* ---------- state ---------- */
let state = { current: null, history: [], showZones: false };
try {
  const raw = JSON.parse(localStorage.getItem(LS_KEY));
  if (raw && typeof raw === 'object' && raw.history) state = Object.assign(state, raw);
} catch (e) { /* fresh start */ }
const save = () => localStorage.setItem(LS_KEY, JSON.stringify(state));

/* ---------- generation ---------- */
function briefWords(brief) {
  const words = (brief || '').toUpperCase().replace(/[^A-Z0-9\s&'-]/g, ' ').split(/\s+/)
    .filter(w => w.length > 2 && !STOP.has(w.toLowerCase()));
  if (!words.length) return ['SIGNAL', 'SHIFT'];
  return words.slice(0, 3);
}
function makePalette(r, vibeKey) {
  const v = VIBES[vibeKey];
  const h = rnd(r, v.hue[0], v.hue[1]);
  const s = rnd(r, v.sat[0], v.sat[1]);
  const scheme = pick(r, ['analogous', 'complement', 'triad', 'split']);
  const spin = scheme === 'complement' ? 180 : scheme === 'triad' ? 120 : scheme === 'split' ? 150 : rnd(r, 24, 48);
  let base, surface;
  if (v.dark) {
    base = hslHex(h, s * 0.5, rnd(r, 6, 12));
    surface = hslHex(h + 8, s * 0.42, rnd(r, 14, 20));
  } else {
    base = hslHex(h, s * 0.32, rnd(r, 88, 95));
    surface = hslHex(h + 6, s * 0.3, rnd(r, 78, 85));
  }
  const primary = hslHex(h, s, v.dark ? rnd(r, 56, 68) : rnd(r, 32, 44));
  const accent = hslHex(h + spin, Math.min(96, s + 18), rnd(r, 52, 64));
  const signal = hslHex(h + spin + (scheme === 'split' ? 60 : 30), Math.min(92, s + 8), v.dark ? rnd(r, 68, 80) : rnd(r, 46, 58));
  return {
    scheme,
    colors: [
      { name: 'Base',    role: 'background', hex: base },
      { name: 'Surface', role: 'panels',     hex: surface },
      { name: 'Primary', role: 'brand',      hex: primary },
      { name: 'Accent',  role: 'action',     hex: accent },
      { name: 'Signal',  role: 'highlight',  hex: signal },
    ],
  };
}
function makeShapes(r, vibeKey, W, H) {
  const kind = pick(r, VIBES[vibeKey].shapes);
  const n = 4 + Math.floor(r() * 5);
  const shapes = [];
  for (let i = 0; i < n; i++) {
    const ci = 2 + Math.floor(r() * 3); // primary/accent/signal
    const op = rnd(r, 0.55, 0.95);
    if (kind === 'orbs') {
      shapes.push({ kind: 'circle', cx: rnd(r, 0.08, 0.92) * W, cy: rnd(r, 0.08, 0.8) * H, rr: rnd(r, 0.04, 0.2) * W, ci, op });
    } else if (kind === 'rings') {
      shapes.push({ kind: 'ring', cx: rnd(r, 0.1, 0.9) * W, cy: rnd(r, 0.1, 0.75) * H, rr: rnd(r, 0.05, 0.22) * W, sw: rnd(r, 3, 16), ci, op });
    } else if (kind === 'bars') {
      shapes.push({ kind: 'bar', x: rnd(r, -0.1, 0.85) * W, y: rnd(r, 0.05, 0.85) * H, w: rnd(r, 0.25, 0.7) * W, h: rnd(r, 0.015, 0.06) * H, rot: pick(r, [-24, -12, 0, 12, 24]), ci, op });
    } else if (kind === 'blocks') {
      shapes.push({ kind: 'rect', x: rnd(r, 0.04, 0.7) * W, y: rnd(r, 0.06, 0.7) * H, w: rnd(r, 0.1, 0.32) * W, h: rnd(r, 0.08, 0.28) * H, ci, op });
    } else if (kind === 'rules') {
      shapes.push({ kind: 'line', x1: rnd(r, 0.05, 0.3) * W, y: rnd(r, 0.1, 0.9) * H, x2: rnd(r, 0.7, 0.95) * W, sw: rnd(r, 1, 4), ci, op });
    } else { // blobs
      const cx = rnd(r, 0.15, 0.85) * W, cy = rnd(r, 0.15, 0.7) * H, rr = rnd(r, 0.06, 0.18) * W;
      const pts = [];
      const seg = 7;
      for (let k = 0; k < seg; k++) {
        const ang = (k / seg) * Math.PI * 2;
        const rad = rr * rnd(r, 0.72, 1.28);
        pts.push([cx + Math.cos(ang) * rad, cy + Math.sin(ang) * rad]);
      }
      shapes.push({ kind: 'blob', pts, ci, op });
    }
  }
  return { style: kind, shapes };
}
const FORMAT_DIMS = { poster: { w: 900, h: 1200 }, brand: { w: 1280, h: 800 }, ui: { w: 1120, h: 780 } };
function makeZones(format, W, H) {
  if (format === 'poster') return [
    { x: W * .07, y: H * .05, w: W * .86, h: H * .07, label: 'masthead' },
    { x: W * .07, y: H * .16, w: W * .86, h: H * .42, label: 'hero visual' },
    { x: W * .07, y: H * .62, w: W * .86, h: H * .2, label: 'headline' },
    { x: W * .07, y: H * .86, w: W * .86, h: H * .09, label: 'meta / palette' },
  ];
  if (format === 'brand') return [
    { x: W * .05, y: H * .08, w: W * .26, h: H * .84, label: 'logo & voice' },
    { x: W * .35, y: H * .08, w: W * .6, h: H * .36, label: 'palette system' },
    { x: W * .35, y: H * .5, w: W * .6, h: H * .42, label: 'type specimens' },
  ];
  return [
    { x: W * .06, y: H * .1, w: W * .88, h: H * .09, label: 'nav' },
    { x: W * .06, y: H * .24, w: W * .5, h: H * .4, label: 'hero copy' },
    { x: W * .6, y: H * .24, w: W * .34, h: H * .4, label: 'hero visual' },
    { x: W * .06, y: H * .7, w: W * .88, h: H * .2, label: 'cards' },
  ];
}
function generateBoard(brief, vibe, format, seeds) {
  const { w: W, h: H } = FORMAT_DIMS[format];
  const rp = mulberry32(hashStr(brief + '|pal|' + seeds.palette));
  const rt = mulberry32(hashStr(brief + '|typ|' + seeds.type));
  const rl = mulberry32(hashStr(brief + '|lay|' + seeds.layout));
  return {
    id: 'b' + Date.now().toString(36) + Math.floor(Math.random() * 999),
    ts: Date.now(),
    brief, vibe, format, seeds,
    palette: makePalette(rp, vibe),
    type: TYPE_PAIRS[Math.floor(rt() * TYPE_PAIRS.length)],
    comp: makeShapes(rl, vibe, W, H),
    zones: makeZones(format, W, H),
    layers: LAYER_DEFS.map(l => ({ ...l, on: true })),
  };
}

/* ---------- SVG rendering ---------- */
function shapeSVG(sh, P) {
  const c = P[sh.ci];
  if (sh.kind === 'circle') return `<circle cx="${sh.cx.toFixed(1)}" cy="${sh.cy.toFixed(1)}" r="${sh.rr.toFixed(1)}" fill="${c}" opacity="${sh.op.toFixed(2)}"/>`;
  if (sh.kind === 'ring') return `<circle cx="${sh.cx.toFixed(1)}" cy="${sh.cy.toFixed(1)}" r="${sh.rr.toFixed(1)}" fill="none" stroke="${c}" stroke-width="${sh.sw.toFixed(1)}" opacity="${sh.op.toFixed(2)}"/>`;
  if (sh.kind === 'bar') return `<rect x="${sh.x.toFixed(1)}" y="${sh.y.toFixed(1)}" width="${sh.w.toFixed(1)}" height="${sh.h.toFixed(1)}" rx="${(sh.h / 2).toFixed(1)}" fill="${c}" opacity="${sh.op.toFixed(2)}" transform="rotate(${sh.rot} ${(sh.x + sh.w / 2).toFixed(1)} ${(sh.y + sh.h / 2).toFixed(1)})"/>`;
  if (sh.kind === 'rect') return `<rect x="${sh.x.toFixed(1)}" y="${sh.y.toFixed(1)}" width="${sh.w.toFixed(1)}" height="${sh.h.toFixed(1)}" fill="${c}" opacity="${sh.op.toFixed(2)}"/>`;
  if (sh.kind === 'line') return `<line x1="${sh.x1.toFixed(1)}" y1="${sh.y.toFixed(1)}" x2="${sh.x2.toFixed(1)}" y2="${sh.y.toFixed(1)}" stroke="${c}" stroke-width="${sh.sw.toFixed(1)}" opacity="${sh.op.toFixed(2)}"/>`;
  if (sh.kind === 'blob') {
    const p = sh.pts;
    let d = `M ${p[0][0].toFixed(1)} ${p[0][1].toFixed(1)} `;
    for (let i = 1; i <= p.length; i++) {
      const a = p[i % p.length], prev = p[i - 1];
      const mx = ((prev[0] + a[0]) / 2).toFixed(1), my = ((prev[1] + a[1]) / 2).toFixed(1);
      d += `Q ${prev[0].toFixed(1)} ${prev[1].toFixed(1)} ${mx} ${my} `;
    }
    return `<path d="${d}Z" fill="${c}" opacity="${sh.op.toFixed(2)}"/>`;
  }
  return '';
}
function renderSVG(board, opts = {}) {
  const { w: W, h: H } = FORMAT_DIMS[board.format];
  const P = board.palette.colors.map(c => c.hex);
  const on = id => { const l = board.layers.find(x => x.id === id); return l ? l.on : true; };
  const words = briefWords(board.brief);
  const ink = textOn(P[0]);
  const dispF = `'${board.type.display}','Bricolage Grotesque',sans-serif`;
  const bodyF = `'${board.type.body}','IBM Plex Sans',sans-serif`;
  let s = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" font-family="${bodyF}">`;
  s += `<defs>
    <radialGradient id="lvwash" cx="30%" cy="18%" r="85%">
      <stop offset="0%" stop-color="${P[4]}" stop-opacity=".34"/>
      <stop offset="55%" stop-color="${P[2]}" stop-opacity=".12"/>
      <stop offset="100%" stop-color="${P[0]}" stop-opacity="0"/>
    </radialGradient>
    <clipPath id="lvclip"><rect width="${W}" height="${H}"/></clipPath>
  </defs><g clip-path="url(#lvclip)">`;
  if (on('bg')) s += `<rect width="${W}" height="${H}" fill="${P[0]}"/>`;
  if (on('wash')) s += `<rect width="${W}" height="${H}" fill="url(#lvwash)"/>`;
  if (on('grid')) {
    const cols = 6;
    for (let i = 1; i < cols; i++) s += `<line x1="${(W / cols) * i}" y1="0" x2="${(W / cols) * i}" y2="${H}" stroke="${ink}" stroke-opacity=".06"/>`;
  }
  if (on('shapes')) s += `<g>${board.comp.shapes.map(sh => shapeSVG(sh, P)).join('')}</g>`;

  if (on('content')) {
    if (board.format === 'poster') {
      s += `<text x="${W * .07}" y="${H * .085}" font-family="${bodyF}" font-size="17" letter-spacing="5" fill="${ink}" opacity=".75">${esc(board.vibe.toUpperCase())} · N°${board.seeds.layout % 97}</text>`;
      s += `<line x1="${W * .07}" y1="${H * .105}" x2="${W * .93}" y2="${H * .105}" stroke="${ink}" stroke-opacity=".3"/>`;
      const fs = Math.min(120, (W * .86) / Math.max(4, Math.max(...words.map(w => w.length))) * 1.7);
      words.forEach((w, i) => {
        s += `<text x="${W * .07}" y="${H * .62 + (i + 1) * fs * 1.02}" font-family="${dispF}" font-weight="800" font-size="${fs}" fill="${i === words.length - 1 ? P[3] : ink}" letter-spacing="1">${esc(w)}</text>`;
      });
      s += `<text x="${W * .07}" y="${H * .935}" font-family="${bodyF}" font-size="15" fill="${ink}" opacity=".62">${esc((board.brief || 'Untitled brief').slice(0, 72))}</text>`;
    } else if (board.format === 'brand') {
      const bx = W * .05, bw = W * .26;
      s += `<rect x="${bx}" y="${H * .08}" width="${bw}" height="${H * .84}" rx="18" fill="${P[1]}"/>`;
      s += `<circle cx="${bx + bw / 2}" cy="${H * .3}" r="${bw * .22}" fill="${P[3]}"/>`;
      s += `<text x="${bx + bw / 2}" y="${H * .3 + bw * .085}" text-anchor="middle" font-family="${dispF}" font-weight="800" font-size="${bw * .24}" fill="${textOn(P[3])}">${esc(words[0][0] || 'L')}</text>`;
      s += `<text x="${bx + bw / 2}" y="${H * .55}" text-anchor="middle" font-family="${dispF}" font-weight="800" font-size="${Math.min(34, bw * .14)}" fill="${textOn(P[1])}">${esc(words[0])}</text>`;
      s += `<text x="${bx + bw / 2}" y="${H * .61}" text-anchor="middle" font-family="${bodyF}" font-size="14" letter-spacing="3" fill="${textOn(P[1])}" opacity=".6">${esc(board.vibe.toUpperCase())} SYSTEM</text>`;
      s += `<text x="${W * .35}" y="${H * .14}" font-family="${bodyF}" font-size="14" letter-spacing="4" fill="${ink}" opacity=".6">PALETTE / ${esc(board.palette.scheme.toUpperCase())}</text>`;
      const cw = (W * .6 - 4 * 14) / 5;
      board.palette.colors.forEach((c, i) => {
        const x = W * .35 + i * (cw + 14);
        s += `<rect x="${x}" y="${H * .18}" width="${cw}" height="${H * .2}" rx="12" fill="${c.hex}" stroke="${ink}" stroke-opacity=".14"/>`;
        s += `<text x="${x + 10}" y="${H * .18 + H * .2 - 12}" font-family="${bodyF}" font-size="12" fill="${textOn(c.hex)}" opacity=".85">${c.hex}</text>`;
      });
      s += `<text x="${W * .35}" y="${H * .56}" font-family="${bodyF}" font-size="14" letter-spacing="4" fill="${ink}" opacity=".6">TYPOGRAPHY</text>`;
      s += `<text x="${W * .35}" y="${H * .69}" font-family="${dispF}" font-weight="800" font-size="64" fill="${ink}">Aa — ${esc(board.type.display)}</text>`;
      s += `<text x="${W * .35}" y="${H * .76}" font-family="${bodyF}" font-size="19" fill="${ink}" opacity=".78">${esc(board.type.body)} · The quick brown fox jumps over the lazy dog, 0123456789.</text>`;
      s += `<text x="${W * .35}" y="${H * .82}" font-family="${bodyF}" font-size="14" fill="${ink}" opacity=".5">${esc(board.type.note)}</text>`;
    } else { // ui
      const fx = W * .05, fy = H * .06, fw = W * .9, fh = H * .86;
      s += `<rect x="${fx}" y="${fy}" width="${fw}" height="${fh}" rx="16" fill="${P[1]}" stroke="${ink}" stroke-opacity=".2"/>`;
      s += `<circle cx="${fx + 26}" cy="${fy + 22}" r="5" fill="${P[3]}"/><circle cx="${fx + 44}" cy="${fy + 22}" r="5" fill="${P[4]}"/><circle cx="${fx + 62}" cy="${fy + 22}" r="5" fill="${P[2]}"/>`;
      s += `<line x1="${fx}" y1="${fy + 42}" x2="${fx + fw}" y2="${fy + 42}" stroke="${ink}" stroke-opacity=".16"/>`;
      const inkP = textOn(P[1]);
      s += `<text x="${fx + 30}" y="${fy + 84}" font-family="${dispF}" font-weight="800" font-size="20" fill="${inkP}">${esc(words[0])}</text>`;
      [0, 1, 2].forEach(i => { s += `<rect x="${fx + fw - 260 + i * 78}" y="${fy + 66}" width="60" height="22" rx="11" fill="${inkP}" opacity=".14"/>`; });
      const hf = Math.min(58, (fw * .48) / Math.max(5, words.join(' ').length) * 2.2);
      s += `<text x="${fx + 30}" y="${fy + 200}" font-family="${dispF}" font-weight="800" font-size="${hf}" fill="${inkP}">${esc(words.slice(0, 2).join(' '))}</text>`;
      s += `<text x="${fx + 30}" y="${fy + 236}" font-family="${bodyF}" font-size="16" fill="${inkP}" opacity=".66">${esc((board.brief || 'Your product, staged.').slice(0, 60))}</text>`;
      s += `<rect x="${fx + 30}" y="${fy + 268}" width="168" height="44" rx="22" fill="${P[3]}"/>`;
      s += `<text x="${fx + 114}" y="${fy + 296}" text-anchor="middle" font-family="${bodyF}" font-weight="600" font-size="15" fill="${textOn(P[3])}">Get started</text>`;
      s += `<rect x="${fx + fw * .55}" y="${fy + 120}" width="${fw * .38}" height="230" rx="14" fill="${P[2]}" opacity=".92"/>`;
      s += `<circle cx="${fx + fw * .74}" cy="${fy + 235}" r="62" fill="${P[4]}" opacity=".85"/>`;
      const cw2 = (fw - 60 - 2 * 20) / 3;
      [0, 1, 2].forEach(i => {
        const cx2 = fx + 30 + i * (cw2 + 20), cy2 = fy + fh - 190;
        s += `<rect x="${cx2}" y="${cy2}" width="${cw2}" height="150" rx="12" fill="${P[0]}" opacity=".9"/>`;
        s += `<rect x="${cx2 + 16}" y="${cy2 + 20}" width="34" height="34" rx="9" fill="${[P[3], P[4], P[2]][i]}"/>`;
        s += `<rect x="${cx2 + 16}" y="${cy2 + 72}" width="${cw2 * .62}" height="10" rx="5" fill="${ink}" opacity=".5"/>`;
        s += `<rect x="${cx2 + 16}" y="${cy2 + 94}" width="${cw2 * .45}" height="10" rx="5" fill="${ink}" opacity=".28"/>`;
      });
    }
  }
  if (on('swatches') && board.format !== 'brand') {
    const sw = 34;
    board.palette.colors.forEach((c, i) => {
      s += `<rect x="${W * .07 + i * (sw + 8)}" y="${H - sw - 18}" width="${sw}" height="${sw}" rx="8" fill="${c.hex}" stroke="${ink}" stroke-opacity=".25"/>`;
    });
  }
  if (on('mark')) {
    s += `<text x="${W - 18}" y="${H - 20}" text-anchor="end" font-family="${bodyF}" font-size="13" letter-spacing="3" fill="${ink}" opacity=".55">LOVARA © MERIDIAN</text>`;
  }
  if (opts.zones) {
    s += board.zones.map(z =>
      `<g><rect x="${z.x}" y="${z.y}" width="${z.w}" height="${z.h}" fill="none" stroke="#C8F542" stroke-width="1.6" stroke-dasharray="7 5" opacity=".9"/>` +
      `<rect x="${z.x}" y="${z.y - 22}" width="${z.label.length * 8.5 + 18}" height="20" rx="5" fill="#C8F542"/>` +
      `<text x="${z.x + 9}" y="${z.y - 8}" font-family="IBM Plex Mono,monospace" font-size="11" fill="#0B1F2A">${esc(z.label)}</text></g>`).join('');
  }
  s += '</g></svg>';
  return s;
}

/* ---------- UI rendering ---------- */
function renderAll() {
  const b = state.current;
  const wrap = $('#artwrap');
  if (!b) { wrap.innerHTML = '<div style="padding:60px 20px;color:var(--dim-2);font-family:var(--mono);font-size:13px;text-align:center">No board yet — write a brief and hit <b style="color:var(--acid)">Generate</b>.</div>'; }
  else wrap.innerHTML = renderSVG(b, { zones: state.showZones });
  $('#chipFormat').textContent = b ? b.format : '—';
  $('#chipVibe').textContent = b ? b.vibe : '—';
  $('#seedline').textContent = b ? `seed ${b.seeds.layout}·${b.seeds.palette}·${b.seeds.type} — ${b.palette.scheme} scheme` : 'seed —';

  // palette
  $('#swatches').innerHTML = !b ? '<span style="color:var(--dim-2);font-size:12px">Palette appears after generation.</span>' :
    b.palette.colors.map(c => `
      <div class="swatch" data-hex="${c.hex}" title="Click to copy">
        <span class="dot" style="background:${c.hex}"></span>
        <span><span class="nm">${c.name}</span><br><span style="font-size:11px;color:var(--dim-2)">${c.role}</span></span>
        <span class="hx">${c.hex}</span>
      </div>`).join('');

  // type
  $('#typecard').innerHTML = !b ? '<span style="color:var(--dim-2);font-size:12px">Pairing appears after generation.</span>' : `
    <div class="disp">${esc(b.type.display)}</div>
    <div class="body" style="font-family:'${esc(b.type.body)}','IBM Plex Sans',sans-serif">${esc(b.type.body)} — The quick brown fox jumps over the lazy dog.</div>
    <div class="meta">${esc(b.type.note)}</div>`;

  // layers
  $('#layers').innerHTML = !b ? '<span style="color:var(--dim-2);font-size:12px">Layer stack appears after generation.</span>' :
    b.layers.map(l => `
      <div class="layer ${l.on ? '' : 'off'}" data-layer="${l.id}">
        <span class="eye">${l.on ? '◉' : '○'}</span><span>${l.name}</span><span class="kind">${l.kind}</span>
      </div>`).join('');

  // history
  $('#hist').innerHTML = state.history.length ? state.history.map(h => `
    <div class="hist-item ${b && h.id === b.id ? 'cur' : ''}" data-id="${h.id}" title="${esc((h.brief || '').slice(0, 60))}">
      ${renderSVG(h, {})}
      <button class="del" data-del="${h.id}" title="Delete">×</button>
    </div>`).join('') : '<span style="color:var(--dim-2);font-size:12px;grid-column:1/-1">Boards you generate stack up here.</span>';
}

/* ---------- actions ---------- */
function newSeeds() { return { layout: Math.floor(Math.random() * 1e6), palette: Math.floor(Math.random() * 1e6), type: Math.floor(Math.random() * 1e6) }; }
function doGenerate(seeds) {
  const brief = $('#brief').value.trim();
  const vibe = $('#vibe').value;
  const format = $('#format').value;
  const board = generateBoard(brief, vibe, format, seeds || newSeeds());
  state.current = board;
  state.history.unshift(board);
  if (state.history.length > 12) state.history.length = 12;
  save(); renderAll();
}
function reroll(part) {
  if (!state.current) return doGenerate();
  const seeds = { ...state.current.seeds, [part]: Math.floor(Math.random() * 1e6) };
  const b = generateBoard(state.current.brief, state.current.vibe, state.current.format, seeds);
  b.layers = state.current.layers.map(l => ({ ...l })); // keep visibility choices
  state.current = b;
  state.history[0] = b; // replace head so partial rerolls don't spam history
  save(); renderAll();
}

$('#btnGenerate').addEventListener('click', () => { doGenerate(); toast('Board generated'); });
$('#btnRegen').addEventListener('click', () => { doGenerate(); toast('Regenerated — new seeds'); });
$('#btnShufPal').addEventListener('click', () => { reroll('palette'); toast('Palette rerolled'); });
$('#btnShufType').addEventListener('click', () => { reroll('type'); toast('Type pairing rerolled'); });
$('#btnShufLayout').addEventListener('click', () => { reroll('layout'); toast('Composition rerolled'); });

$('#toggleZones').addEventListener('change', e => { state.showZones = e.target.checked; save(); renderAll(); });

$('#btnExportSVG').addEventListener('click', () => {
  if (!state.current) return toast('Generate a board first');
  download(`lovara-${state.current.format}-${state.current.seeds.layout}.svg`, renderSVG(state.current, {}), 'image/svg+xml');
  toast('SVG exported');
});
$('#btnExportJSON').addEventListener('click', () => {
  if (!state.current) return toast('Generate a board first');
  const b = state.current;
  const brief = {
    tool: 'LOVARA by MERIDIAN', version: 1, exportedAt: new Date().toISOString(),
    brief: b.brief, vibe: b.vibe, format: b.format, seeds: b.seeds,
    palette: b.palette, typography: b.type,
    layers: b.layers.map(l => ({ id: l.id, name: l.name, visible: l.on })),
    zones: b.zones,
  };
  download(`lovara-brief-${b.seeds.layout}.json`, JSON.stringify(brief, null, 2), 'application/json');
  toast('JSON brief exported');
});
$('#btnClearHist').addEventListener('click', () => {
  if (!state.history.length) return;
  if (!confirm('Clear all board history?')) return;
  state.history = []; save(); renderAll(); toast('History cleared');
});

/* delegated: swatches, layers, history */
document.addEventListener('click', e => {
  const sw = e.target.closest('.swatch');
  if (sw) {
    navigator.clipboard && navigator.clipboard.writeText(sw.dataset.hex).catch(() => {});
    toast(sw.dataset.hex + ' copied');
    return;
  }
  const ly = e.target.closest('.layer');
  if (ly && state.current) {
    const l = state.current.layers.find(x => x.id === ly.dataset.layer);
    if (l) { l.on = !l.on; save(); renderAll(); }
    return;
  }
  const del = e.target.closest('[data-del]');
  if (del) {
    e.stopPropagation();
    state.history = state.history.filter(h => h.id !== del.dataset.del);
    if (state.current && state.current.id === del.dataset.del) state.current = state.history[0] || null;
    save(); renderAll();
    return;
  }
  const hi = e.target.closest('.hist-item');
  if (hi) {
    const b = state.history.find(h => h.id === hi.dataset.id);
    if (b) {
      state.current = b;
      $('#brief').value = b.brief || '';
      $('#vibe').value = b.vibe;
      $('#format').value = b.format;
      save(); renderAll(); toast('Board restored');
    }
  }
});
$$('.brief-hints button').forEach(btn => btn.addEventListener('click', () => {
  $('#brief').value = btn.dataset.hint; $('#brief').focus();
}));

/* ---------- boot ---------- */
(function boot() {
  $('#toggleZones').checked = !!state.showZones;
  if (state.current) {
    $('#brief').value = state.current.brief || '';
    $('#vibe').value = state.current.vibe || 'electric';
    $('#format').value = state.current.format || 'poster';
  }
  renderAll();
})();
