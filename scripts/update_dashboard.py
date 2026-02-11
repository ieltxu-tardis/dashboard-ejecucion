#!/usr/bin/env python3
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path('/root/.openclaw/workspace')
NEXT = ROOT / 'NEXT_ACTIONS.md'
DATA = ROOT / 'dashboard' / 'data.json'
PERSONA_METRICS = ROOT / 'dashboards' / 'personas' / 'persona-metrics.json'

text = NEXT.read_text(encoding='utf-8')


def section(name):
    m = re.search(rf"## {re.escape(name)}\n(.*?)(?=\n## |\Z)", text, re.S)
    return m.group(1).strip() if m else ''

next_sec = section('NEXT (Top 3)')
blocked_sec = section('BLOCKED')
waiting_sec = section('WAITING')
done_sec = section('DONE')

# top3 titles from lines like: - [ ] (NEXT) Name
raw_top = re.findall(r"^- \[.\] \(NEXT\) (.+)$", next_sec, re.M)
if not raw_top:
    raw_top = [re.sub(r"^- \[.\]\s*", "", l).strip() for l in re.findall(r"^- \[.\].+$", next_sec, re.M)][:3]

def count_open(sec):
    return len(re.findall(r"^- \[ \]", sec, re.M))

next_active = min(3, len(raw_top))
blocked = count_open(blocked_sec)
waiting = count_open(waiting_sec)

# basic momentum heuristic from DONE section count + assume recent activity
done_count = len(re.findall(r"^- \[x\]", done_sec, re.M | re.I))
last_done_hours = 0 if done_count > 0 else 48

# Argentina time
art = timezone(timedelta(hours=-3))
now = datetime.now(art)
updated = now.strftime('%Y-%m-%d %H:%M ART')

def sh(cmd):
    import subprocess
    return subprocess.check_output(cmd, shell=True, text=True).strip()

if DATA.exists():
    data = json.loads(DATA.read_text(encoding='utf-8'))
else:
    data = {}

persona_runtime = []
if PERSONA_METRICS.exists():
    pm = json.loads(PERSONA_METRICS.read_text(encoding='utf-8'))
    for p in pm.get('personas', []):
        status = '🟢' if p.get('active') else '⚪'
        persona_runtime.append(f"{status} {p.get('id')} · runs:{p.get('runsToday',0)} · blocked:{p.get('blocked',0)} · thr:{p.get('throughput','n/a')}")

# live ops status (detailed monitor)
try:
    last_commit = sh("git -C /root/.openclaw/workspace log -1 --pretty=format:'%h %s'")
except Exception:
    last_commit = 'n/a'

try:
    changed = sh("git -C /root/.openclaw/workspace status --short | wc -l")
except Exception:
    changed = '0'

try:
    tardis_next = (ROOT / 'TARDIS_NEXT.md').read_text(encoding='utf-8')
    pending_tardis = len(re.findall(r'^- \[ \]', tardis_next, re.M))
except Exception:
    pending_tardis = 0

try:
    deploy_commit = sh("git -C /root/.openclaw/workspace/.tmp-dashboard-pages log -1 --pretty=format:'%h %s'")
except Exception:
    deploy_commit = 'n/a'

try:
    mins = int((now - datetime.strptime(updated, '%Y-%m-%d %H:%M ART').replace(tzinfo=art)).total_seconds() / 60)
except Exception:
    mins = 0

live_ops = [
    f"Heartbeat: cada 10 min",
    f"Último commit local: {last_commit}",
    f"Último deploy pages: {deploy_commit}",
    f"Cambios sin commit (workspace): {changed}",
    f"Tareas Tardis pendientes: {pending_tardis}",
    f"Freshness target: <=10m",
    f"Última actualización: {updated}",
]

data.update({
    'updatedAt': updated,
    'timezone': 'America/Argentina/Buenos_Aires',
    'top3': raw_top[:3],
    'system': {
        'nextActive': next_active,
        'blocked': blocked,
        'waiting': waiting,
    },
    'momentum': {
        'streakDays': max(1, done_count),
        'lastDoneHoursAgo': last_done_hours,
    },
    'personaRuntime': persona_runtime,
    'liveOps': live_ops,
})

DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'updated: {DATA}')
