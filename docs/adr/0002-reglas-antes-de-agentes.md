# ADR 0002: reglas deterministas antes de agentes

- Estado: aceptada
- Fecha: 2026-11-18

## Contexto

El valor de varios agentes no puede medirse si no existe una línea base que produzca resultados repetibles.

## Decisión

Se empieza con reglas deterministas sobre líneas añadidas y un modelo `Finding` común. Los revisores LLM se incorporarán detrás de interfaces, con evaluación comparativa y validación de salida.

## Consecuencias

El MVP es reproducible, rápido y no requiere API. Su cobertura semántica es limitada y no debe anunciarse como revisión completa de bugs. Se podrá medir cuánto aporta el LLM frente a la base determinista.

La ruta Gemini optativa se añadió después según ADR 0003; el modo solo reglas mantiene la ejecución sin API.
