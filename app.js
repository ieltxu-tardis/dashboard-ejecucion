async function load(){
  const res = await fetch('./data.json', {cache:'no-store'});
  const d = await res.json();

  document.getElementById('meta').textContent = `Actualizado: ${d.updatedAt} · Zona: ${d.timezone}`;

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
}

function renderList(id, items, opts={}){
  const ul = document.querySelector(`#${id} ul`);
  ul.innerHTML = '';
  items.forEach(item => {
    const li = document.createElement('li');
    li.textContent = item;
    if(opts.classFor) li.className = opts.classFor(item) || '';
    ul.appendChild(li);
  });
}

load().catch(err=>{
  document.getElementById('meta').textContent = `Error cargando data.json: ${err.message}`;
});