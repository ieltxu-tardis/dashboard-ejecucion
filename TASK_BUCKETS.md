# TASK_BUCKETS.md

Checkpoint: 2026-02-14

## 1) Sistema de Agentes (Operación)
Objetivo: visibilidad y coordinación real entre agentes.

- [ ] Definir contrato de evento único para `#agent-feed` (START/HANDOFF/BLOCKED/DELIVERED/RESUMED/DONE)
- [ ] Publicar status heartbeat operativo cada 15 min en `#sistema`
- [ ] Definir regla de escalamiento (bloqueo >20 min)

## 2) Gestión de Proyectos (Multi-frente)
Objetivo: siempre conocer next step por proyecto.

- [ ] Plantilla canónica Project Card (owner, estado, next, bloqueo, evidencia)
- [ ] Inventario inicial de proyectos activos por canal (`#trabajo`, `#finanzas`, `#personal`, `#ideas`)
- [ ] Límite WIP global (máx proyectos running simultáneos)

## 3) Observabilidad
Objetivo: tablero útil, no decorativo.

- [ ] Especificar `state.json` canónico (agents/projects/todos/alerts/freshness)
- [ ] Definir fuentes de verdad (Discord + repos + memoria)
- [ ] Crear primera vista textual en `#sistema`

## 4) Memoria & Continuidad
Objetivo: no perder contexto entre sesiones.

- [ ] Rutina diaria en `memory/YYYY-MM-DD.md`
- [ ] Curar semanalmente a `MEMORY.md`
- [ ] Registrar decisiones estructurales en `SYSTEM_MAP.md`

## 5) Arquitectura & Repos
Objetivo: límites claros entre repos.

- [ ] Mantener root solo para mapa/operación general
- [ ] Mantener `system-core` como fuente de verdad operativa
- [ ] Mantener `bridge/remote` como integración activa
