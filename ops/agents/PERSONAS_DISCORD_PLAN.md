# PERSONAS_DISCORD_PLAN.md

## Objetivo
Crear y escalar "personas" (agentes especializados) sin perder control operativo.

## Niveles posibles (de menor a mayor complejidad)

### Nivel 1 — Un bot, múltiples personas (recomendado ahora)
- Un único bot de Discord (el actual).
- Varias personas lógicas dentro de OpenClaw (`main`, `builder`, `scout`, etc.).
- Selección por reglas de orquestación (default Tardis) + override por tag/alias.

**Pros:** simple, seguro, barato.
**Contras:** visualmente sigue siendo el mismo usuario/bot en Discord.

### Nivel 2 — Un bot + múltiples canales por rol
- Mantener un bot y asignar canales dedicados por rol.
- Útil para separar contexto y auditar mejor.

**Pros:** orden y trazabilidad.
**Contras:** más fricción de navegación.

### Nivel 3 — Múltiples bots ("usuarios" distintos en Discord)
- Crear una app/bot de Discord por persona (ej: Tardis, Builder, Scout).
- Cada bot con token propio.
- OpenClaw multi-account o múltiples gateways para rutear cada bot a un agente.

**Pros:** identidad visual y operativa separada por completo.
**Contras:** más mantenimiento, seguridad de tokens, permisos por bot, complejidad de routing.

## Qué conviene para ustedes ahora
1. Quedarse en Nivel 1 (orquestador-first) + estructura de dominios.
2. Agregar aliases explícitos de invocación (`@builder`, `@scout`).
3. Cuando haya 2-3 personas estables con uso real, evaluar pasar a Nivel 3.

## Blueprint para crear nuevas personas
Al crear una persona nueva, definir siempre:
- `nombre`
- `misión`
- `qué sí / qué no`
- `inputs esperados`
- `output esperado`
- `tool policy` (allow/deny)
- `canal preferido`

Plantilla rápida:

```md
# Persona: <name>
Misión:
Inputs:
Outputs:
No hacer:
Tools permitidas:
Canal default:
```

## Riesgos (si vamos a múltiples bots)
- fuga de token por mala higiene
- permisos excesivos en Discord
- loops bot-to-bot si no hay mention gating
- pérdida de contexto si el routing no es explícito

## Guardrails obligatorios
- Menor privilegio por bot/canal
- Mention gating activo
- Registro de handoff entre personas
- Auditoría semanal de permisos/tokens
