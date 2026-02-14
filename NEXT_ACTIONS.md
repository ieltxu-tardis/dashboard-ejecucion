# NEXT_ACTIONS.md

## ACTIVE_NOW
- [ ] (ACTIVE) Ninguna tarea activa en Scope A v1 (última transición cerrada a DONE con evidencia)

## NEXT (Top 3)
- [ ] (NEXT) Integrar dispatcher externo para enviar `runtime/outbox/sistema_snapshot.txt` a `#sistema`
  - Resultado: publicación automática end-to-end conectada al runtime tick
  - Primer paso: conectar outbox a transporte del canal

- [ ] (NEXT) Integrar dispatcher externo para enviar `runtime/outbox/agent_feed_event.txt` a `#agent-feed`
  - Resultado: eventos de ejecución llegan al canal sin romper anti-noise
  - Primer paso: mapear archivo outbox a envío por canal

- [ ] (NEXT) Añadir prueba de regresión para diffs de `ACTIVE_NOW/BLOCKED/DONE`
  - Resultado: validación automática de reglas STARTED/HEARTBEAT/BLOCKED/COMPLETED
  - Primer paso: fixture previo/actual + asserts de evento esperado

## BLOCKED
- [ ] (BLOCKED) Dependencia externa: falta conectar transporte de canal (outbox -> Discord) en runtime host

## DONE
- [x] Bootstrap Scope A premium runtime foundation (2026-02-14)
- [x] `docs/DASHBOARD_A_PREMIUM_SPEC.md` creado con contrato de bloques y quality rules (2026-02-14)
- [x] `runtime/RUNTIME_STATE.json` creado con schema+sample operativo (2026-02-14)
- [x] `scripts/runtime_snapshot.md` creado con flujo de generación de snapshots (2026-02-14)
- [x] (ACTIVE->DONE) Publicador `scripts/publish_scope_a_snapshot.sh` creado con salida de 4 bloques + `NO_REPLY` sin `material_change_marker` (2026-02-14)
- [x] `docs/SCOPE_A_RUNTIME_EVENTS.md` creado con contrato STARTED/HEARTBEAT/BLOCKED/COMPLETED para `#agent-feed` (2026-02-14)
- [x] (ACTIVE->DONE) Scope A v1 runtime wiring completado con evidencia:
  - `scripts/run_scope_a_runtime_cycle.sh` (cron/runtime entrypoint)
  - `scripts/emit_scope_a_runtime_event.sh` (emite STARTED/HEARTBEAT/BLOCKED/COMPLETED sólo por cambios materiales)
  - `scripts/runtime_snapshot.md` (pipeline de `#sistema` cableado al output de `publish_scope_a_snapshot.sh`)
  - `docs/SCOPE_A_RUNTIME_EVENTS.md` (wiring de eventos y outbox)
