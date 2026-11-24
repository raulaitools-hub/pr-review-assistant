# ADR 0001: empezar con ejecución local

- Estado: aceptada
- Fecha: 2026-11-18

## Contexto

Una integración de GitHub añade permisos, webhooks, despliegue y manejo de PRs de forks antes de validar la calidad del análisis.

## Decisión

El primer entregable es un CLI local que analiza un diff de Git y escribe Markdown o JSON. No publica comentarios ni ejecuta el cambio.

## Consecuencias

El usuario puede probarlo sin credenciales y la superficie de riesgo es pequeña. Se posterga la demostración de webhooks y comentarios hasta tener métricas que justifiquen esa complejidad.
