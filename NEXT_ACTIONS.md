# NEXT_ACTIONS.md

## ACTIVE_NOW
- [ ] (ACTIVE) Integrar `#agent-feed` como eventos de ejecución reales para actualizar `runtime/RUNTIME_STATE.json`
  - Resultado: pipeline STARTED/HEARTBEAT/BLOCKED/COMPLETED con cambios trazables
  - Primer paso: cablear emisor de eventos al contrato `docs/SCOPE_A_RUNTIME_EVENTS.md`

## NEXT (Top 3)
- [ ] (NEXT) Implementar emisor runtime -> `#agent-feed` según `docs/SCOPE_A_RUNTIME_EVENTS.md`
  - Resultado: eventos STARTED/HEARTBEAT/BLOCKED/COMPLETED salen sólo por cambios reales
  - Primer paso: mapear transición de `runtime/RUNTIME_STATE.json` a payload de evento

- [ ] (NEXT) Activar marker de cambio material en runtime publisher
  - Resultado: `scripts/publish_scope_a_snapshot.sh` publica snapshot sólo cuando hay marker válido
  - Primer paso: escribir `material_change_marker` desde la actualización de runtime

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
- [x] (ACTIVE->DONE) Publicador `scripts/publish_scope_a_snapshot.sh` creado con salida de 4 bloques + `NO_REPLY` sin `material_change_marker` (2026-02-14)
- [x] `docs/SCOPE_A_RUNTIME_EVENTS.md` creado con contrato STARTED/HEARTBEAT/BLOCKED/COMPLETED para `#agent-feed` (2026-02-14)
