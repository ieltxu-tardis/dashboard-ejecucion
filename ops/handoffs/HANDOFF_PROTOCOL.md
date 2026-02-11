# HANDOFF_PROTOCOL.md

## Objetivo
Delegar entre personas sin perder contexto ni calidad.

## Formato obligatorio
```md
HANDOFF
from: <persona>
to: <persona>
why: <por qué delega>
context:
- <3-5 bullets>
expected_output: <qué se espera exactamente>
done_definition:
- <criterios de terminado>
timebox: <ej. 30m / 2h>
priority: <P1|P2|P3>
```

## Regla de cierre
La persona receptora devuelve:
- resultado
- evidencia (archivo/commit/link)
- next step sugerido

## Regla anti-caos
Sin `done_definition`, no se acepta handoff.
