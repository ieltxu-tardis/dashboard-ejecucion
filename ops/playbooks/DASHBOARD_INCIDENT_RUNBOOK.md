# DASHBOARD_INCIDENT_RUNBOOK.md

## Trigger
Usar este playbook cuando el dashboard no refleja cambios esperados.

## Checks (en orden)
1. `cron runs` del job `Auto-refresh dashboard-ejecucion (10m)`
2. `scripts/dashboard_healthcheck.sh`
3. Verificar que `.tmp-dashboard-repo` tenga `index.html` y `data.json` en el root
4. Verificar URL pública (HTTP 200)

## Fix rápido
```bash
cd /root/.openclaw/workspace
./scripts/update_dashboard.py
cd .tmp-dashboard-repo
cp -r /root/.openclaw/workspace/dashboard/* .
git add .
git -c user.name='tardis-bot' -c user.email='bot@local' commit -m 'Manual dashboard recovery' || true
git push
```

## Falla crítica (alertar)
Enviar alerta a `#sistema-de-ejecucion` con:
- síntoma
- último run cron
- último commit deployado
- acción aplicada

## Postmortem mínimo
Registrar en `memory/YYYY-MM-DD.md`:
- causa raíz
- guardrail agregado
- cómo detectarlo antes
