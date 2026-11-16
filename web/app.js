/* SecureVault web UI. All crypto/AI runs in Python; this file only draws and animates. */
const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const BROWSER = new URLSearchParams(location.search).has('b');
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
async function call(name, ...args) {
  if (!BROWSER) return await window.pywebview.api[name](...args);
  const r = await fetch('/api/' + name, {method: 'POST', headers: {'Content-Type': 'application/json', 'X-SV': '1'}, body: JSON.stringify(args)});
  return r.json();
}
const sleep = ms => new Promise(r => setTimeout(r, ms));
let ALGO = 'AES-256-GCM', OUT = '', REC = null, SIG = '', FILE = null, PERF = null, PSIZE = '102400', lastSig = '', shown = 0, scr = null, HOUT = '';
const KEYLBL = {'Caesar Cipher': 'Shift (number)', 'Vigenère Cipher': 'Key (letters only)', 'AES-256-GCM': 'Password', 'RSA-2048': 'Key (not needed, uses your RSA keys)', 'SHA-256 Hash': 'Key (not needed)'};

/* ---------- navigation ---------- */
function go(page, algo) {
  $('#bBrute').hidden = (algo !== 'Caesar Cipher'); $('#bFreq').hidden = (algo !== 'Vigenère Cipher'); $('#avCard').hidden = (algo !== 'SHA-256 Hash');
  ALGO = algo; $$('.nav').forEach(b => b.classList.toggle('on', b.dataset.algo === algo));
  const pg = $('#p-' + page);
  if (!pg.classList.contains('on')) {
    $$('.page').forEach(p => p.classList.remove('on')); pg.classList.add('on');
    $$('#p-' + page + ' .glass').forEach((c, i) => c.style.setProperty('--i', i));
  }
  if (page === 'vault') { $('#keylbl').textContent = KEYLBL[algo] || 'Key'; $('#key').type = (algo === 'Caesar Cipher' || algo === 'Vigenère Cipher') ? 'text' : 'password'; }
  if (page === 'verify' && SIG) $('#sig').value = SIG;
 $('#tKey').hidden = (algo === 'Caesar Cipher' || algo === 'Vigenère Cipher'); $('#tKey').innerHTML = EYE_ON; $('#tKey').classList.remove('active-eye');
  pwUpdate();
}
$$('.nav').forEach(b => b.addEventListener('click', () => go(b.dataset.page, b.dataset.algo)));

/* ---------- helpers ---------- */
function say(el, text, ok) { el.textContent = text; el.className = 'status ' + (ok ? 'ok' : 'err'); void el.offsetWidth; el.classList.add('pop'); }
function scramble(el, v) {                      // output "decodes" itself character by character
  clearInterval(scr); if (!v) { el.textContent = ''; return; }
  const CH = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz0123456789+/#%'; let f = 0; const n = v.length, step = Math.max(3, Math.ceil(n / 22));
  scr = setInterval(() => {
    f += step; if (f >= n) { el.textContent = v; clearInterval(scr); return; }
    let t = ''; for (let i = 0; i < Math.min(n - f, 160); i++) t += CH[Math.random() * CH.length | 0];
    el.textContent = v.slice(0, f) + t;
  }, 30);
}
function setOut(v) { OUT = v; scramble($('#out'), v); }
function countTo(v) {
  const a = shown, t0 = performance.now(); shown = v;
  (function f(t) { const p = Math.min(1, (t - t0) / 650), x = a + (v - a) * (1 - Math.pow(1 - p, 3));
    $('#risk').textContent = Math.round(x); $('#bar').style.width = x + '%'; if (p < 1) requestAnimationFrame(f); })(t0);
}
function beam() { const b = $('#beam'); b.classList.remove('go'); void b.offsetWidth; b.classList.add('go'); }
async function keyState() { $('#keystate').textContent = (await call('keys_ready')) ? 'RSA-2048 keys ready' : 'No RSA keys yet'; $('#keystate').style.color = (await call('keys_ready')) ? 'var(--acc)' : ''; }

/* ---------- AI scanner + advisor ---------- */
let deb; $('#msg').addEventListener('input', () => { clearTimeout(deb); deb = setTimeout(scan, 180); });
async function scan() {
  const r = await call('scan', $('#msg').value), box = $('#finds'); REC = r.rec;
  const sig = r.findings.map(f => f.name + f.sev).join('|'), fresh = sig !== lastSig; box.innerHTML = '';
  r.findings.forEach((f, i) => {
    const d = document.createElement('div'); d.className = 'find ' + (f.sev === 'High' ? 'hi' : 'md') + (fresh ? ' shake' : '');
    d.innerHTML = `<span>${esc(f.name)} ·</span><b>${esc(f.sev)}</b>`; d.style.animationDelay = fresh ? (500 + i * 140) + 'ms' : '0s'; if (!fresh) d.style.animation = 'none'; box.append(d);
  });
  if (!r.findings.length && r.rec) box.innerHTML = '<div class="ok">No sensitive data detected</div>';
  if (fresh && r.findings.length) beam();
  lastSig = sig; countTo(r.risk);
  const adv = $('#advAlg'), name = r.rec ? 'Use ' + r.rec.algorithm : '—';
  if (adv.textContent !== name) { adv.textContent = name; adv.classList.remove('flash'); void adv.offsetWidth; adv.classList.add('flash'); }
  $('#advWhy').textContent = r.rec ? r.rec.reason : 'Type a message to get a recommendation.';
}
$('#bMask').onclick = async () => { $('#msg').value = (await call('mask', $('#msg').value)).text; scan(); };
$('#bApply').onclick = () => { if (!REC) return; const a = REC.algorithm, target = a.startsWith('RSA') ? 'RSA-2048' : a.startsWith('SHA') ? 'SHA-256 Hash' : 'AES-256-GCM'; go('vault', target); say($('#status'), `AI switched algorithm to ${target}`, true); };
$('#bBrute').onclick = async () => { const r = await call('brute_force', OUT || $('#msg').value); if (!r.ok) return say($('#status'), r.error, false); setOut(r.results.map(x => `Shift ${String(x.shift).padStart(2, '0')}: ${x.text}`).join('\n')); say($('#status'), `Brute force (25 shifts) · ${r.ms} ms`, true); };
$('#bAv').onclick = async () => { const r = await call('avalanche', $('#msg').value, $('#avMsg2').value); if (!r.ok) return say($('#avRes'), r.error, false); say($('#avRes'), `${r.diff_bits}/256 bits changed (${r.percent}%)\nH1: ${r.hash1.slice(0,24)}...\nH2: ${r.hash2.slice(0,24)}...`, true); };
$('#bFreq').onclick = async () => { const r = await call('freq_analysis', OUT || $('#msg').value); if (!r.ok) return say($('#status'), r.error, false); if (!r.top.length) return say($('#status'), 'No letters to analyze', false); setOut('Top 5 Most Frequent Letters (English E ≈ 12.7%):\n' + r.top.map(x => `${x.char} : ${x.count} times (${x.percent}%)`).join('\n')); say($('#status'), `Frequency analysis · ${r.ms} ms`, true); };
$('#bCopy').onclick = () => { if (!OUT) return; navigator.clipboard.writeText(OUT); say($('#status'), 'Output copied to clipboard!', true); };
$('#bSwap').onclick = () => { if (!OUT) return; $('#msg').value = OUT; scan(); say($('#status'), 'Moved output to message box', true); };
const EYE_ON = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align:-3px;margin-right:5px"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>Show', EYE_OFF = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align:-3px;margin-right:5px"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>Hide';
const togPw = (inp, btn) => { const show = inp.type === 'password'; inp.type = show ? 'text' : 'password'; btn.innerHTML = show ? EYE_OFF : EYE_ON; btn.classList.toggle('active-eye', show); btn.classList.remove('flash'); void btn.offsetWidth; btn.classList.add('flash'); };
$('#tKey').onclick = () => togPw($('#key'), $('#tKey'));
$('#tFpw').onclick = () => togPw($('#fpw'), $('#tFpw'));
/* ---------- vault actions ---------- */
function show(r, label) { if (r.ok) { setOut(r.out); say($('#status'), `${label} OK · ${r.ms} ms`, true); } else { setOut(''); say($('#status'), r.error, false); } return r.ok; }
$('#bEnc').onclick = async () => show(await call('crypt', ALGO, 'encrypt', $('#msg').value, $('#key').value), 'Encrypt');
$('#bDec').onclick = async () => show(await call('crypt', ALGO, 'decrypt', OUT || $('#msg').value, $('#key').value), 'Decrypt');
$('#bHash').onclick = async () => show(await call('hash', $('#msg').value), 'SHA-256');
$('#bSign').onclick = async () => { const r = await call('sign', $('#msg').value); if (show(r, 'Sign')) SIG = r.out; keyState(); };
$('#genkeys').onclick = async () => { await call('gen_keys'); keyState(); };
$('#savepub').onclick = async () => {
  if (!BROWSER) { const r = await call('save_public_key'); if (r.ok) keyState(); return; }
  const r = await call('public_pem'); download('public_key.pem', btoa(r.pem)); keyState();
};
function download(name, b64) { const a = document.createElement('a'); a.href = 'data:application/octet-stream;base64,' + b64; a.download = name; document.body.append(a); a.click(); a.remove(); }

/* ---------- verify page ---------- */
const vs = (t, ok) => say($('#vstatus'), t, ok);
$('#vSign').onclick = async () => { const r = await call('sign', $('#vmsg').value); if (r.ok) { $('#sig').value = r.out; SIG = r.out; vs('Message signed with your RSA private key.', true); keyState(); } else vs(r.error, false); };
$('#vVerify').onclick = async () => { const r = await call('verify', $('#vmsg').value, $('#sig').value); if (!r.ok) return vs(r.error, false);
  vs(r.valid ? 'Signature VALID - message is authentic.' : 'Signature INVALID - message modified or wrong signature.', r.valid); };
$('#vTests').onclick = async () => {
  const r = await call('run_tests', $('#vmsg').value); if (!r.ok) return vs(r.error, false); $('#sig').value = r.sig; SIG = r.sig; keyState();
  r.tests.forEach(async (t, i) => { await sleep(i * 240); const c = $('#t' + (i + 1)); c.className = 'glass card res ' + t.state; void c.offsetWidth; c.classList.add('show');
    c.querySelector('.big').textContent = t.title; c.querySelector('p').textContent = t.desc; });
};

/* ---------- file vault ---------- */
const fs = (t, ok) => say($('#fstatus'), t, ok), fmt = n => n.toLocaleString() + ' bytes';
$('#fpick').onclick = async () => {
  if (!BROWSER) { const r = await call('choose_file'); if (!r.ok) return; FILE = r; $('#fname').textContent = r.name; $('#finfo').textContent = `${fmt(r.size)} · SHA-256: ${r.sha256}`; }
  else $('#finput').click();
};
$('#finput').onchange = () => { const f = $('#finput').files[0]; if (!f) return; FILE = {file: f, name: f.name}; $('#fname').textContent = f.name; $('#finfo').textContent = fmt(f.size); };
async function fileOp(op) {
  if (!FILE) return fs('Choose a file first', false);
  let r;
  if (!BROWSER) r = await call('file_op', op, FILE.path, $('#fpw').value);
  else { const buf = new Uint8Array(await FILE.file.arrayBuffer()); let s = ''; for (let i = 0; i < buf.length; i += 8192) s += String.fromCharCode(...buf.subarray(i, i + 8192));
    r = await call('file_op_b64', op, FILE.name, btoa(s), $('#fpw').value); if (r.ok) download(r.name, r.b64); }
  fs(r.ok ? `${op === 'encrypt' ? 'Encrypt' : 'Decrypt'} OK · ${r.ms} ms\nSaved: ${r.path || r.name}\nSHA-256 of result: ${r.sha256}` : r.error, r.ok);
}
$('#fEnc').onclick = () => fileOp('encrypt'); $('#fDec').onclick = () => fileOp('decrypt');

/* ---------- hybrid ---------- */
$('#hmsg').value = 'Long message '.repeat(40);
const hs = (t, ok) => say($('#hstatus'), t, ok);
$('#hEnc').onclick = async () => { const r = await call('hybrid', 'encrypt', $('#hmsg').value); if (r.ok) { HOUT = r.out; scramble($('#hout'), r.out); hs(`Encrypt OK · ${r.ms} ms`, true); keyState(); } else hs(r.error, false); };
$('#hDec').onclick = async () => { const r = await call('hybrid', 'decrypt', HOUT); if (r.ok) { $('#hmsg').value = r.out; hs(`Decrypt OK · ${r.ms} ms`, true); } else hs(r.error, false); };

/* ---------- performance ---------- */
const COL = {'Caesar': 'linear-gradient(90deg,#F5B84B,#ffd98a)', 'Vigenère': 'linear-gradient(90deg,#F5B84B,#ffd98a)', 'AES-256-GCM': 'linear-gradient(90deg,#2DD4BF,#7ff0e0)', 'SHA-256': 'linear-gradient(90deg,#7AA7FF,#b4cdff)'};
$('#pRun').onclick = async () => { $('#pnote').textContent = 'Running…'; const r = await call('benchmark'); if (!r.ok) { $('#pnote').textContent = r.error; return; }
  PERF = r; $('#prsa').textContent = Object.entries(r.rsa).map(([k, v]) => `${k}: ${v.toFixed(2)} ms`).join('   '); drawBars(); };
$$('.tab').forEach(b => b.onclick = () => { $$('.tab').forEach(x => x.classList.toggle('on', x === b)); PSIZE = b.dataset.size; if (PERF) drawBars(); });
function drawBars() {
  const d = PERF.sizes[PSIZE], box = $('#bars'), hi = Math.log10(Math.max(...Object.values(d))) + 3; box.innerHTML = '';
  Object.entries(d).forEach(([k, ms], i) => {
    const w = Math.max(2, (Math.log10(Math.max(ms, .001)) + 3) / hi * 100), row = document.createElement('div'); row.className = 'brow';
    row.innerHTML = `<div>${esc(k)}</div><div class="track"><div class="fill" style="background:${COL[k]}"></div><span class="val">${ms.toFixed(3)} ms</span></div>`; box.append(row);
    setTimeout(() => row.querySelector('.fill').style.width = w + '%', 60 + i * 130);
  });
  const aes = d['AES-256-GCM'], vig = d['Vigenère'], lbl = {'1024': '1 KB', '102400': '100 KB', '1048576': '1 MB'}[PSIZE];
  $('#pnote').textContent = `At ${lbl}: AES-256-GCM is ${Math.round(vig / aes)}× faster than our Vigenère and also far stronger. (AES timing excludes the password-derivation step, which is intentionally slow to resist guessing.)`;
}

/* ---------- password strength meter (AI) ---------- */
let pwDeb;
$('#key').addEventListener('input', () => { clearTimeout(pwDeb); pwDeb = setTimeout(pwUpdate, 150); });
async function pwUpdate() {
  const box = $('#pwm'); if (!box) return;
  const on = ALGO === 'AES-256-GCM' && $('#p-vault').classList.contains('on') && $('#key').value; box.hidden = !on; if (!on) return;
  const r = await call('password_strength', $('#key').value); if (!r.ok) return;
  $('#pwbar').style.width = Math.max(6, r.score) + '%'; $('#pwbar').className = r.label; $('#pwlbl').textContent = r.label.toUpperCase() + ' · ' + r.score + '/100'; $('#pwlbl').className = r.label;
  $('#pwtips').textContent = r.tips.join(' · ');
}

/* ---------- AI Lab ---------- */
function cm(box, labels, m) {
  box.innerHTML = ''; box.style.gridTemplateColumns = `110px repeat(${labels.length}, 1fr)`;
  const cell = (t, c) => { const d = document.createElement('div'); d.className = c; d.textContent = t; box.append(d); return d; };
  cell('real ↓ / pred →', 'cmh'); labels.forEach(l => cell(l, 'cmh'));
  m.forEach((row, i) => { cell(labels[i], 'cmh'); const tot = row.reduce((a, b) => a + b, 0) || 1;
    row.forEach((v, j) => { const d = cell(v, 'cmc' + (i === j ? ' diag' : v ? ' bad' : '')); d.style.setProperty('--a', (v / tot).toFixed(2)); d.style.animationDelay = (i * 5 + j) * 25 + 'ms'; }); });
}
$('#aiRun').onclick = async () => {
  $('#ainote').textContent = 'Running…'; const r = await call('ai_report'); if (!r.ok) { $('#ainote').textContent = r.error; return; }
  const a = r.report.advisor, p = r.report.password; $('#ainote').textContent = ''; $('#aicards').hidden = false;
  $('#adAcc').textContent = `${(a.accuracy * 100).toFixed(1)}% on ${a.test} unseen sentences · cross-validation ${(a.cv_accuracy * 100).toFixed(1)}% · trained on ${a.train}`;
  cm($('#adCM'), a.labels, a.matrix); $('#adErr').textContent = a.errors.length ? 'Mistakes: ' + a.errors.map(e => `“${e.text}” (${e.expected} → ${e.got})`).join('  ·  ') : 'No mistakes.';
  $('#pwAcc').textContent = `${(p.hand_accuracy * 100).toFixed(1)}% on ${18} hand-written passwords · ${(p.accuracy * 100).toFixed(1)}% on ${p.test} generated`;
  cm($('#pwCM'), p.labels, p.matrix); $('#pwErr').textContent = 'The generated test uses the same generator as training, so the hand-written score is the honest one.';
};

/* ---------- global effects: spotlight on glass, magnetic + ripple buttons ---------- */
document.addEventListener('pointermove', e => {
  const g = e.target.closest('.glass'); if (g) { const r = g.getBoundingClientRect(); g.style.setProperty('--x', e.clientX - r.left + 'px'); g.style.setProperty('--y', e.clientY - r.top + 'px'); }
  const b = e.target.closest('.btn'); if (b) { const r = b.getBoundingClientRect(); b.style.transform = `translate(${(e.clientX - r.left - r.width / 2) * .16}px,${(e.clientY - r.top - r.height / 2) * .26 - 2}px)`; }
});
document.addEventListener('pointerout', e => { const b = e.target.closest('.btn'); if (b && !b.contains(e.relatedTarget)) b.style.transform = ''; });
document.addEventListener('click', e => {
  const b = e.target.closest('.btn'); if (!b) return; const r = b.getBoundingClientRect(), d = Math.max(r.width, r.height) * 2, s = document.createElement('span');
  s.className = 'rip'; s.style.cssText = `width:${d}px;height:${d}px;left:${e.clientX - r.left - d / 2}px;top:${e.clientY - r.top - d / 2}px`; b.append(s); setTimeout(() => s.remove(), 700);
});

/* ---------- boot ---------- */
async function boot() {
  if (!BROWSER && !(window.pywebview && window.pywebview.api)) await new Promise(r => { window.addEventListener('pywebviewready', r, {once: true}); setTimeout(r, 5000); });
  $$('#p-vault .glass').forEach((c, i) => c.style.setProperty('--i', i)); go('vault', 'AES-256-GCM'); keyState(); scan();
}
window.addEventListener('DOMContentLoaded', boot);
