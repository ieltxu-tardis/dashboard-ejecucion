# REPORTING_SYSTEM.md

## Objetivo
Generar reportes diarios y deep-research configurables, con tuning dinámico.

## Source of truth
- `reports/config/topics.json`

## Output
- Brief diario: `reports/daily/YYYY-MM-DD.md`
- Deep research: `reports/deep/YYYY-MM-DD-<topic>.md`

## Cómo tunear (por chat)
Pedirle a Tardis comandos de intención:
- "report on <topic-id>"
- "report off <topic-id>"
- "report priority <topic-id> high|medium|low"
- "report deep <topic-id> daily|3x-week|weekly|off"
- "report add <name> con keywords ..."

Tardis actualiza `topics.json` y el siguiente cron usa la nueva configuración.
