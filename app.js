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
  if (min < 60) return diffMs < 0 ? `hace ${min} min` : `en ${min} min`;
  const h = Math.round(min / 60);
  if (h < 24) return diffMs < 0 ? `hace ${h} h` : `en ${h} h`;
  const d = Math.round(h / 24);
  return diffMs < 0 ? `hace ${d} d` : `en ${d} d`;
}

function formatAbsolute(iso, tz = 'America/Argentina/Buenos_Aires') {
  if (!iso) return 'n/a';
  const dt = new Date(iso);
  if (Number.isNaN(dt.getTime())) return 'n/a';
  return new Intl.DateTimeFormat('es-AR', {
    timeZone: tz,
    weekday: 'short',
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  }).format(dt) + ' ART';
}

function renderList(id, items, opts = {}) {
  const ul = document.querySelector(`#${id} ul`);
  ul.innerHTML = '';
  const safeItems = Array.isArray(items) ? items : [];
  safeItems.forEach(item => {
    const li = document.createElement('li');
    li.textContent = item;
    if (opts.classFor) li.className = opts.classFor(item) || '';
    ul.appendChild(li);
  });
}

function getScopeStructure(d, scope) {
  if (d.structureByScope && Array.isArray(d.structureByScope[scope])) return d.structureByScope[scope];
  if (d.structureNav && Array.isArray(d.structureNav)) {
    if (scope === 'all') return d.structureNav;
    return d.structureNav.filter(x => x.toLowerCase().includes(`/${scope}/`) || x.toLowerCase().includes(`${scope}`));
  }
  if (d.structureTree && Array.isArray(d.structureTree)) {
    if (scope === 'all') return d.structureTree;
    return d.structureTree.filter(x => x.toLowerCase().includes(`${scope}/`) || x.toLowerCase().includes(` ${scope}/`));
  }
  return ['Sin estructura disponible para este scope'];
}

function getScopeChangelog(d, scope) {
  if (d.changelogByScope && Array.isArray(d.changelogByScope[scope])) return d.changelogByScope[scope];
  if (d.liveOps && Array.isArray(d.liveOps)) {
    const base = d.liveOps.slice(0, 5);
    return scope === 'all' ? base : base.map(x => `[${scope}] ${x}`);
  }
  return ['Sin changelog disponible'];
}

async function load() {
  const res = await fetch('./data.json', { cache: 'no-store' });
  const d = await res.json();

  const scopeSelect = document.getElementById('scopeSelect');
  const initialScope = parseScopeFromUrl();
  const valid = ['all', 'work', 'personal', 'general'];
  const scope = valid.includes(initialScope) ? initialScope : 'all';
  scopeSelect.value = scope;

  const nextIso = d.nextEstimatedUpdateAtIso || null;
  const updatedIso = d.updatedAtIso || null;

  const updatedHuman = updatedIso
    ? `${formatRelative(updatedIso)} (${formatAbsolute(updatedIso, d.timezone)})`
    : (d.updatedAt || 'n/a');

  const nextHuman = nextIso
    ? `${formatRelative(nextIso)} (${formatAbsolute(nextIso, d.timezone)})`
    : (d.nextEstimatedUpdateAt || 'n/a');

  const freq = d.refreshEveryMinutes ? ` · Frecuencia: ${d.refreshEveryMinutes} min` : '';
  document.getElementById('meta').textContent = `Actualizado: ${updatedHuman} · Próx update: ${nextHuman}${freq} · Zona: ${d.timezone || 'ART'}`;

  const ql = document.getElementById('quicklinks');
  ql.innerHTML = '';
  (d.quickLinks || []).forEach(l => {
    const a = document.createElement('a');
    a.href = l.url; a.target = '_blank'; a.rel = 'noreferrer'; a.textContent = l.label;
    ql.appendChild(a);
  });

  const na = d.nextAction || {};
  renderList('nextaction', [
    `${na.recommended || 'Sin recomendación'}`,
    `Prioridad: ${na.priority || 'P2'} · Fuente: ${na.source || 'FALLBACK'}`,
    `ETA: ${na.etaMinutes || 10} min · Confianza: ${na.confidence ?? 'n/a'}`,
    `Motivo: ${na.reason || 'n/a'}`
  ], {
    classFor: (txt) => txt.includes('Prioridad: P0') ? 'warn' : 'ok'
  });

  renderList('system', [
    `NEXT activos: ${d.system?.nextActive ?? 'n/a'} / 3`,
    `BLOCKED: ${d.system?.blocked ?? 'n/a'}`,
    `WAITING: ${d.system?.waiting ?? 'n/a'}`
  ]);

  renderList('scopeview', getScopeStructure(d, scope));
  renderList('scopechangelog', getScopeChangelog(d, scope));
  renderList('liveops', d.liveOps || []);

  scopeSelect.addEventListener('change', (e) => {
    const selected = e.target.value;
    setScopeInUrl(selected);
    renderList('scopeview', getScopeStructure(d, selected));
    renderList('scopechangelog', getScopeChangelog(d, selected));
  });
}

load().catch(err => {
  document.getElementById('meta').textContent = `Error cargando data.json: ${err.message}`;
});
