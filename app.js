async function load(){
  const res = await fetch('./data.json', {cache:'no-store'});
  const d = await res.json();

  const updated = formatDateSmart(d.updatedAtIso, d.updatedAt);
  const nextEta = d.nextEstimatedUpdateAt ? ` · Próxima actualización: ${d.nextEstimatedUpdateAt}` : '';
  const freq = d.refreshEveryMinutes ? ` · Frecuencia: cada ${d.refreshEveryMinutes} min` : '';
  document.getElementById('meta').textContent = `Última actualización: ${updated}${nextEta}${freq} · Zona: ${d.timezone}`;

  const ql = document.getElementById('quicklinks');
  ql.innerHTML = '';
  (d.quickLinks || []).forEach(l => {
    const a = document.createElement('a');
    a.href = l.url; a.target = '_blank'; a.rel = 'noreferrer'; a.textContent = l.label;
    ql.appendChild(a);
  });

  renderList('top3', d.top3);
  renderList('system', [
    `NEXT activos: ${d.system.nextActive} / 3`,
    `BLOCKED: ${d.system.blocked}`,
    `WAITING: ${d.system.waiting}`
  ]);

  renderList('momentum', [
    `Racha DONE: ${d.momentum.streakDays} días`,
    `Último DONE: ${d.momentum.lastDoneHoursAgo}h`
  ], {
    classFor: (txt)=> txt.includes('Último DONE') && d.momentum.lastDoneHoursAgo > 24 ? 'warn' : 'ok'
  });

  renderList('finance', d.finance);
  renderList('relationships', d.relationships);
  renderList('ai', d.aiSignal.map(i => `${i.title} — ${i.note}`));
  renderList('health', d.health);
  renderList('architecture', d.architecture || []);
  renderList('personas', d.personaRuntime || []);
  renderList('agentlive', d.agentLive || []);
  renderList('tokencontrol', d.tokenControl || []);
  renderList('bridgecontrol', d.bridgeControl || []);
  renderList('statusboard', d.statusBoard || []);
  renderList('liveops', d.liveOps || []);
  renderList('structurenav', d.structureNav || []);
  renderList('roadmap', d.personaRoadmap || []);

  const tree = document.querySelector('#structure .tree');
  tree.textContent = (d.structureTree || []).join('\n');
}

function renderList(id, items, opts={}){
  const ul = document.querySelector(`#${id} ul`);
  if(!ul) return;
  ul.innerHTML = '';
  items.forEach(item => {
    const li = document.createElement('li');
    li.textContent = item;
    if(opts.classFor) li.className = opts.classFor(item) || '';
    ul.appendChild(li);
  });
}

function formatDateSmart(iso, fallback){
  if(!iso) return fallback || 'n/a';
  const dt = new Date(iso);
  if(Number.isNaN(dt.getTime())) return fallback || iso;
  const now = new Date();
  const diffMs = now - dt;
  const diffMin = Math.round(diffMs / 60000);
  if(diffMin < 1) return 'justo ahora';
  if(diffMin < 60) return `hace ${diffMin} min`;
  const diffH = Math.round(diffMin / 60);
  if(diffH < 24) return `hace ${diffH} h`;
  return fallback || dt.toLocaleString();
}

load().catch(err=>{
  document.getElementById('meta').textContent = `Error cargando data.json: ${err.message}`;
});