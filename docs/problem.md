# Problema, usuarios y alcance

## Problema

Las revisiones de cambios consumen tiempo y algunos riesgos pasan inadvertidos. Los asistentes basados únicamente en un LLM pueden producir comentarios convincentes pero incorrectos, sin señalar evidencia verificable.

## Usuario objetivo

Desarrolladores que quieren una primera revisión repetible de un cambio antes de pedir revisión humana. El producto es una ayuda a la revisión, no un aprobador automático.

## Objetivo del MVP

Leer el diff local de Git y producir observaciones acotadas a líneas modificadas, explicando qué regla se activó y cómo se puede corregir.

## No objetivos

- Aprobar, fusionar o publicar cambios.
- Ejecutar código del repositorio automáticamente.
- Certificar que el cambio sea seguro o correcto.
- Cubrir múltiples lenguajes en la primera entrega.
- Reemplazar CodeQL, un análisis SAST especializado ni la revisión humana.

## Criterio de producto

Un comentario solo es útil si se puede ubicar y verificar. La evidencia y los límites del análisis forman parte del resultado.
