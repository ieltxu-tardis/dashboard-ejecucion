# SYSTEM_MAP.md

Estado real del workspace (post-reset) — 2026-02-13 UTC.

## Qué existe y para qué

- `bridge/remote/` (repo git: `openclaw-bridge`)
  - Integración/puente activo.
  - Se mantiene como pieza operativa.

- `system-core/` (repo git: `tardis-system-core`)
  - Fuente de verdad operativa.
  - Reglas, estructura, roles, playbooks, backlog y scripts core.

- `memory/` + `MEMORY.md`
  - Memoria diaria + memoria de largo plazo activadas.

- `_trash/`
  - Respaldo recuperable de limpieza del dashboard legacy.

## Qué se desactivó

- Dashboard legacy en root (`app.js`, `index.html`, `styles.css`, `data.json`, `reports/`)
  - Removido de la raíz y movido a `_trash/`.

## Regla operativa actual

1. Core de decisiones y estructura: `system-core/`
2. Integración externa activa: `bridge/remote/`
3. Continuidad y contexto: `memory/` + `MEMORY.md`
4. Todo lo legacy se mantiene fuera de ruta en `_trash/`
