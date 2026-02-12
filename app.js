function parseScopeFromUrl() {
  const p = new URLSearchParams(window.location.search);
  return p.get('scope') || 'all';
}

function setScopeInUrl(scope) {
  const u = new URL(window.location.href);
  u.searchParams.set('scope', scope);
  window.history.replaceState({}, '', u);
}

function formatRelative(iso) {
  if (!iso) return 'n/a';
  const ts = new Date(iso).getTime();
  if (Number.isNaN(ts)) return 'n/a';
  const diffMs = ts - Date.now();
  const abs = Math.abs(diffMs);
  const min = Math.round(abs / 60000);
  if (min < 1) return diffMs < 0 ? 'hace instantes' : 'en instantes';
  if (min < 60) return diffMs < 0 ? `hace ${min}m` : `en ${min}m`;
  const h = Math.round(min / 60);
  if (h < 24) return diffMs < 0 ? `hace ${h}h` : `en ${h}h`;
  const d = Math.round(h / 24);
  return diffMs < 0 ? `hace ${d}d` : `en ${d}d`;
}

function formatAbsolute(iso, tz = 'America/Argentina/Buenos_Aires') {
  if (!iso) return 'n/a';
  const dt = new Date(iso);
  if (Number.isNaN(dt.getTime())) return 'n/a';
  return new Intl.DateTimeFormat('es-AR', {
    timeZone: tz,
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  }).format(dt).replace(',', '') + ' ART';
}

function compactTimeText(text, tz = 'America/Argentina/Buenos_Aires') {
  if (!text) return text;
  return String(text)
    .replace(/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+\-]\d{2}:?\d{2})?/g, (m) => formatAbsolute(m, tz))
    .replace(/\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}(?::\d{2})?\s*ART/g, (m) => {
      const isoLike = m.replace(' ART', '').replace(' ', 'T') + '-03:00';
      return formatAbsolute(isoLike, tz);
    });
}

function limitLine(text, max = 92) {
  const t = String(text || '');
  return t.length > max ? `${t.slice(0, max - 1)}…` : t;
}

function classForStatus(txt) {
  const t = (txt || '').toLowerCase();
  if (t.includes('🔴') || t.includes('blocked') || t.includes('down') || t.includes('error')) return 'bad';
  if (t.includes('🟡') || t.includes('stale') || t.includes('pending') || t.includes('waiting') || t.includes('p1')) return 'warn';
  return 'ok';
}

function renderList(id, items, opts = {}) {
  const ul = document.querySelector(`#${id} ul`);
  if (!ul) return;
  ul.innerHTML = '';
  const safeItems = Array.isArray(items) ? items : [];
  safeItems.forEach(item => {
    const li = document.createElement('li');
    li.textContent = limitLine(item, opts.maxLine || 96);
    li.className = opts.classFor ? (opts.classFor(item) || '') : '';
    ul.appendChild(li);
  });
}

function getScopeStructure(d, scope) {
  const raw = d.structureByScope?.[scope] || d.structureNav || d.structureTree || [];
  const base = Array.isArray(raw) ? raw : ['Sin estructura'];
  if (scope === 'all') return base.slice(0, 6);
  return base
    .filter(x => String(x).toLowerCase().includes(scope))
    .slice(0, 6);
}

function getOpsUnified(d, scope) {
  const fromScope = (d.changelogByScope?.[scope] || []).map(x => `Scope: ${x}`);
  const fromLive = (d.liveOps || []).map(x => `Ops: ${x}`);
  const fromStatus = (d.statusBoard || []).map(x => `Estado: ${x}`);

  const merged = [...fromScope, ...fromLive, ...fromStatus]
    .map(x => compactTimeText(x, d.timezone))
    .filter(Boolean);

  return [...new Set(merged)].slice(0, 8);
}

function getEvidence(d) {
  const ev = [];
  if (Array.isArray(d.statusBoard) && d.statusBoard[0]) ev.push(`Evidencia: ${d.statusBoard[0]}`);
  if (Array.isArray(d.liveOps) && d.liveOps[2]) ev.push(`Evidencia: ${d.liveOps[2]}`);
  if (!ev.length) ev.push('Evidencia: sin señal explícita en data');
  return ev.slice(0, 2);
}

async function load() {
  const res = await fetch('./data.json', { cache: 'no-store' });
  const d = await res.json();

  const scopeSelect = document.getElementById('scopeSelect');
  const valid = ['all', 'work', 'personal', 'general'];
  const scope = valid.includes(parseScopeFromUrl()) ? parseScopeFromUrl() : 'all';
  scopeSelect.value = scope;

  const updatedIso = d.updatedAtIso || null;
  const nextIso = d.nextEstimatedUpdateAtIso || null;
  const updatedText = updatedIso ? `${formatRelative(updatedIso)} · ${formatAbsolute(updatedIso, d.timezone)}` : compactTimeText(d.updatedAt || 'n/a', d.timezone);
  const nextText = nextIso ? `${formatRelative(nextIso)} · ${formatAbsolute(nextIso, d.timezone)}` : compactTimeText(d.nextEstimatedUpdateAt || 'n/a', d.timezone);

  document.getElementById('meta').textContent = `Act: ${updatedText} · Próx: ${nextText} · Freq ${d.refreshEveryMinutes || 'n/a'}m · ${d.timezone || 'ART'}`;

  const ql = document.getElementById('quicklinks');
  ql.innerHTML = '';
  (d.quickLinks || []).slice(0, 4).forEach(l => {
    const a = document.createElement('a');
    a.href = l.url;
    a.target = '_blank';
    a.rel = 'noreferrer';
    a.textContent = l.label;
    ql.appendChild(a);
  });

  const na = d.nextAction || {};
  const nextItems = [
    na.recommended || 'Sin recomendación explícita (fallback operativo)',
    `Prioridad ${na.priority || 'P2'} · ${na.source || 'SISTEMA'}`,
    `ETA ${na.etaMinutes || 10}m · Conf ${na.confidence ?? 'n/a'}`,
    ...getEvidence(d)
  ].map(x => compactTimeText(x, d.timezone)).slice(0, 5);

  renderList('nextaction', nextItems, {
    classFor: classForStatus,
    maxLine: 110
  });

  const sys = [
    `NEXT ${d.system?.nextActive ?? 'n/a'}/3`,
    `BLOCKED ${d.system?.blocked ?? 'n/a'}`,
    `WAITING ${d.system?.waiting ?? 'n/a'}`
  ];

  renderList('system', sys, {
    classFor: classForStatus,
    maxLine: 60
  });

  const renderScopeAndOps = (selectedScope) => {
    renderList(
      'scopeview',
      getScopeStructure(d, selectedScope).map(x => compactTimeText(x, d.timezone)),
      { classFor: classForStatus, maxLine: 96 }
    );

    renderList('opsfeed', getOpsUnified(d, selectedScope), {
      classFor: classForStatus,
      maxLine: 100
    });
  };

  renderScopeAndOps(scope);

  scopeSelect.addEventListener('change', (e) => {
    const selected = e.target.value;
    setScopeInUrl(selected);
    renderScopeAndOps(selected);
  });
}

load().catch(err => {
  document.getElementById('meta').textContent = `Error cargando data.json: ${err.message}`;
});
