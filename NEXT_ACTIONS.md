# NEXT_ACTIONS.md

## ACTIVE_NOW
- [ ] (ACTIVE) Ninguna tarea activa en Scope A v1 (última transición cerrada a DONE con evidencia)

## NEXT (Top 3)
- [ ] (NEXT) Conectar delivery automático real (servicio/cron) de `runtime/outbox/sistema_snapshot.txt` -> `#sistema`
  - Resultado: publicación automática end-to-end en cada runtime tick
  - Primer paso: registrar hook de ejecución que lea outbox y haga `message send` al canal destino

- [ ] (NEXT) Conectar delivery automático real (servicio/cron) de `runtime/outbox/agent_feed_event.txt` -> `#agent-feed`
  - Resultado: eventos event-driven llegan sin intervención manual
  - Primer paso: mapear outbox + guardas de no-duplicado al transporte de Discord

- [ ] (NEXT) Añadir prueba de regresión para diffs de `ACTIVE_NOW/BLOCKED/DONE`
  - Resultado: validación automática de reglas STARTED/HEARTBEAT/BLOCKED/COMPLETED
  - Primer paso: fixture previo/actual + asserts de evento esperado

## BLOCKED
- [ ] (BLOCKED) B-001: Falta dispatcher automatizado outbox -> Discord en host runtime (bloqueo concreto de integración operativa)

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
- [x] (DONE) Style polish + semantics unblock hardening (2026-02-14):
  - `docs/SCOPE_A_MESSAGE_STYLE.md` creado con plantillas de alta calidad para `#sistema` y `#agent-feed`
  - `scripts/publish_scope_a_snapshot.sh` actualizado a salida markdown compacta (sin `key=value`)
  - `scripts/emit_scope_a_runtime_event.sh` actualizado a eventos legibles multilinea (sin `key=value`)
  - `runtime/RUNTIME_STATE.json` actualizado: B-001 reescrito a bloqueo concreto real + D-003 agregado

## NEXT TRIGGER
- Trigger: cambio material en `runtime/RUNTIME_STATE.json`
- Acción: ejecutar `scripts/run_scope_a_runtime_cycle.sh` y despachar outbox a canales
