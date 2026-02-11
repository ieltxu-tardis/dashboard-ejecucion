# Deep Research — agent-engineering
Date: 2026-02-11
Topic: Agent engineering patterns
Priority: high

## Tesis principal
En 2026, los equipos que mejor rinden no ganan por “más magia multi-agent”, sino por **disciplina de sistema**: comenzar simple, instrumentar fuerte (tracing/evals), y recién escalar autonomía cuando la evidencia lo justifica.

## Evidencia (fuentes y señales)
1) **Patrones simples > frameworks complejos al inicio**
- Anthropic señala que los despliegues más exitosos usan patrones composables simples; diferencian claramente workflows predefinidos vs agentes con control dinámico.
- Recomiendan empezar por llamadas directas al modelo antes de sumar capas de abstracción.
- Fuente: https://www.anthropic.com/engineering/building-effective-agents (fetch 2026-02-11)

2) **Complejidad debe comprarse con performance, no con hype**
- Misma fuente: sistemas agentic intercambian costo/latencia por mejor performance; no siempre conviene.
- Patrón sugerido: prompting + retrieval + ejemplos in-context primero; escalar a routing/paralelización/orchestrator-workers solo si hay gap medible.
- Fuente: https://www.anthropic.com/engineering/building-effective-agents

3) **Adopción real ya existe, pero el cuello está en calidad y controles**
- Survey de LangChain (1300+ profesionales): adopción en producción relevante, pero principal barrera reportada es performance quality; también destacan tracing/guardrails/human oversight.
- Señal útil: el problema dejó de ser “si usar agentes” y pasó a ser “cómo gobernarlos sin romper calidad”.
- Fuente: https://www.langchain.com/stateofaiagents (fetch 2026-02-11)

4) **Routing/evals como patrón económico de producción**
- OpenAI cookbook de selección de modelos enfatiza combinar modelos por capa (routing, synthesis, verification) en vez de un único modelo para todo.
- Para casos críticos, sugiere verificación explícita (LLM-as-judge) y arquitectura por etapas.
- Fuente: https://developers.openai.com/cookbook/examples/partners/model_selection_guide/model_selection_guide

## Implicancias para nuestros proyectos
- **Regla de diseño**: “mínima autonomía viable”. Workflows deterministas para lo repetible; agente libre solo donde aporta.
- **Gobernanza**: observabilidad obligatoria por tarea (traza de decisiones + inputs/outputs de herramientas + evaluación automática).
- **Economía**: routing por dificultad (modelos baratos para lo simple, potentes para edge cases) para bajar costo sin sacrificar outcomes.
- **Producto**: introducir checkpoints de aprobación humana solo en acciones irreversibles (write/delete/public).

## Riesgos y anti-patrones
- Lanzar multi-agent sin contratos claros entre agentes (duplica errores y costo).
- Evaluar solo “respuesta linda” y no task completion end-to-end.
- Medir costo por request en vez de costo por resultado útil.

## Experimento recomendado (esta semana)
**Pilot de arquitectura escalonada con eval automática**
- Pipeline:
  1) router (simple vs complejo),
  2) ejecución (workflow determinista o agente),
  3) verificador (rubrica de calidad + policy checks).
- Dataset inicial: 30 tareas reales del canal de ejecución (mezcla simple/medio/complejo).
- Métricas:
  - task completion real,
  - intervención humana por tarea,
  - costo por tarea útil,
  - tasa de incidentes (acciones incorrectas o fuera de scope).
- Umbral para escalar: +10% completion o -20% costo manteniendo calidad.

## Nivel de confianza
Medio (evidencia fuerte de patrones y operación; falta benchmark propio con nuestros flujos y constraints).