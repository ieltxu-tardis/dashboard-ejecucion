# SYSTEM_STRUCTURE.md

## Objetivo
Escalar este sistema sin caos: separar dominios, mantener trazabilidad y facilitar delegación entre agentes.

## Estructura base
- `domains/work/` → cosas de trabajo (proyectos, dashboards, notas, assets)
- `domains/personal/` → vida personal/sistema personal
- `domains/general/` → experimentos y utilidades compartidas
- `ops/agents/` → definición de roles y reglas de colaboración
- `ops/routing/` → decisiones de enrutamiento por canal/contexto
- `ops/playbooks/` → procedimientos operativos (deploy, backup, incidentes)
- `ops/templates/` → plantillas reutilizables
- `repos/` → mapeo de repos remotos y estado local

## Reglas de orden
1. Todo artefacto nuevo debe caer en un dominio (`work|personal|general`).
2. Si algo cruza dominios, va primero a `general` y luego se duplica/enlaza.
3. Cada proyecto tiene `README.md` corto con: objetivo, estado, próximo paso.
4. Nada crítico vive solo en chat: registrar en archivos.

## Convención de proyectos
`domains/<domain>/projects/<yyyy>-<slug>/`

Contenido mínimo:
- `README.md`
- `NEXT.md`
- `DECISIONS.md`

## Gobernanza de agentes
- Tardis (orquestador): default en todos los canales.
- Builder: ejecución técnica cuando se delega.
- Scout: research/radar cuando se delega.

## Próximo paso sugerido
Mover dashboard actual a `domains/personal/dashboards/dashboard-ejecucion/` (sin romper URL pública), y dejar sync automatizado desde ahí.
