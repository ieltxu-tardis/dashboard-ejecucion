const TZ_FALLBACK = 'America/Argentina/Buenos_Aires';

function asDate(input) {
  if (!input) return null;
  const direct = new Date(input);
  if (!Number.isNaN(direct.getTime())) return direct;

  const art = String(input).match(/(\d{4}-\d{2}-\d{2})\s(\d{2}:\d{2})(?::\d{2})?\s*ART/i);
  if (art) {
    const iso = `${art[1]}T${art[2]}:00-03:00`;
    const parsed = new Date(iso);
    if (!Number.isNaN(parsed.getTime())) return parsed;
  }

  return null;
}

function fmtDate(input, tz = TZ_FALLBACK) {
  const d = asDate(input);
  if (!d) return 'n/a';
  return new Intl.DateTimeFormat('es-AR', {
    timeZone: tz,
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  }).format(d).replace(',', '') + ' ART';
}

function minTo(input) {
  const d = asDate(input);
  if (!d) return null;
  return Math.round((d.getTime() - Date.now()) / 60000);
}

function pickNow(data) {
  const top = data.top3?.[0] || 'Sin foco definido';
  const blocked = Number(data.system?.blocked ?? 0);
  const waiting = Number(data.system?.waiting ?? 0);

  const light = blocked > 0 ? 'yellow' : 'green';
  const label = blocked > 0 ? 'AMARILLO' : 'VERDE';

  return {
    light,
    label,
    headline: top,
    items: [
      `Actualizado: ${fmtDate(data.updatedAtIso || data.updatedAt, data.timezone || TZ_FALLBACK)}`,
      `Capacidad operativa: next=${data.system?.nextActive ?? 'n/a'} · blocked=${blocked} · waiting=${waiting}`,
      `${(data.personaRoadmap || []).find(x => x.includes('In progress')) || 'Sin bloque activo declarado'}`
    ]
  };
}

function pickNext15(data) {
  const nextUpdate = data.nextEstimatedUpdateAtIso || data.nextEstimatedUpdateAt;
  const mins = minTo(nextUpdate);

  let light = 'green';
  let label = 'VERDE';
  if (mins !== null && mins < 0) {
    light = 'red';
    label = 'ROJO';
  } else if (mins !== null && mins > 15) {
    light = 'yellow';
    label = 'AMARILLO';
  }

  const roadmapNext = (data.personaRoadmap || []).filter(x => x.includes('Next')).slice(0, 2);

  return {
    light,
    label,
    headline: mins === null ? 'Sin ETA confiable' : `Ventana operativa: ${mins} min`,
    items: [
      `Próxima actualización: ${fmtDate(nextUpdate, data.timezone || TZ_FALLBACK)}`,
      ...roadmapNext,
      `Refresh objetivo: cada ${data.refreshEveryMinutes || 'n/a'} min`
    ].slice(0, 4)
  };
}

function pickRisks(data) {
  const blocked = Number(data.system?.blocked ?? 0);
  const waiting = Number(data.system?.waiting ?? 0);
  const staleBuilder = (data.agentLive || []).find(x => /stale\s+builder/i.test(x));

  let light = 'green';
  let label = 'VERDE';
  if (blocked > 0) {
    light = 'red';
    label = 'ROJO';
  } else if (waiting > 0 || staleBuilder) {
    light = 'yellow';
    label = 'AMARILLO';
  }

  const riskItems = [
    blocked > 0 ? `Bloqueos activos: ${blocked}` : 'Bloqueos activos: 0',
    waiting > 0 ? `Elementos en espera: ${waiting}` : 'Elementos en espera: 0',
    staleBuilder || 'Señal de agentes sin stale crítico',
    (data.bridgeControl || []).find(x => x.toLowerCase().includes('estado:')) || 'Bridge status: n/a'
  ];

  return {
    light,
    label,
    headline: blocked > 0 ? 'Atacar bloqueos primero' : 'Riesgo bajo control',
    items: riskItems
  };
}

function paint(blockId, lightId, headlineId, listId, payload) {
  const light = document.getElementById(lightId);
  const headline = document.getElementById(headlineId);
  const list = document.getElementById(listId);
  const block = document.getElementById(blockId);

  if (light) {
    light.className = `light ${payload.light}`;
    light.textContent = payload.label;
  }

  if (headline) headline.textContent = payload.headline;

  if (list) {
    list.innerHTML = '';
    payload.items.forEach((item, idx) => {
      const li = document.createElement('li');
      li.textContent = item;
      if (idx > 1) li.classList.add('dim');
      list.appendChild(li);
    });
  }

  if (block) block.dataset.state = payload.light;
}

async function init() {
  const meta = document.getElementById('meta');

  try {
    const res = await fetch('./data.json', { cache: 'no-store' });
    const data = await res.json();

    const now = pickNow(data);
    const next = pickNext15(data);
    const risks = pickRisks(data);

    paint('block-now', 'light-now', 'now-headline', 'now-list', now);
    paint('block-next', 'light-next', 'next-headline', 'next-list', next);
    paint('block-risks', 'light-risks', 'risks-headline', 'risks-list', risks);

    if (meta) {
      const ts = fmtDate(data.updatedAtIso || data.updatedAt, data.timezone || TZ_FALLBACK);
      meta.textContent = `Una pantalla · 3 bloques · última señal ${ts}`;
    }
  } catch (err) {
    if (meta) meta.textContent = `Error cargando data.json: ${err.message}`;
  }
}

init();
