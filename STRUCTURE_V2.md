# STRUCTURE_V2.md

Estructura mínima propuesta (sin ruido):

```text
/workspace
├─ system-core/      # decisiones, reglas, backlog, playbooks
├─ bridge/           # integración activa
├─ memory/           # logs diarios
├─ MEMORY.md         # memoria larga
├─ SYSTEM_MAP.md     # mapa real del sistema
└─ _trash/           # histórico recuperable
```

## Criterios
- No crear carpetas por anticipado.
- Solo se agrega una carpeta nueva cuando existe uso real repetido.
- Cada pieza nueva debe tener propósito explícito en `SYSTEM_MAP.md`.
