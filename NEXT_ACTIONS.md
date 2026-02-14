# NEXT_ACTIONS.md

## ACTIVE_NOW
- [ ] (ACTIVE) Operar snapshots de `#sistema` desde `runtime/RUNTIME_STATE.json`
  - Resultado: publicación determinística basada en runtime truth
  - Primer paso: ejecutar primer snapshot real con evidencia

## NEXT (Top 3)
- [ ] (NEXT) Conectar `#agent-feed` como fuente de eventos para actualizar runtime
  - Resultado: cambios de estado trazables
  - Primer paso: mapear evento -> bloque runtime

- [ ] (NEXT) Definir cadence de snapshot (trigger por cambio material)
  - Resultado: cero ruido y máxima señal
  - Primer paso: fijar criterio de “material change”

- [ ] (NEXT) Cerrar decisión de dashboard visual v2
  - Resultado: alcance visual confirmado sin romper Scope A
  - Primer paso: owner + deadline de decisión

## BLOCKED
- [ ] (BLOCKED) Decisión final sobre dashboard visual (sí/no y alcance)

## DONE
- [x] Bootstrap Scope A premium runtime foundation (2026-02-14)
- [x] `docs/DASHBOARD_A_PREMIUM_SPEC.md` creado con contrato de bloques y quality rules (2026-02-14)
- [x] `runtime/RUNTIME_STATE.json` creado con schema+sample operativo (2026-02-14)
- [x] `scripts/runtime_snapshot.md` creado con flujo de generación de snapshots (2026-02-14)
