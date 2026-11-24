# Plan de evaluación

## Hipótesis

El sistema puede detectar patrones conocidos en líneas cambiadas y producir observaciones localizables con una tasa de falsos positivos suficientemente baja para ahorrar tiempo de revisión.

## Corpus

Preparar ejemplos pequeños, sintéticos y versionados con etiqueta por hallazgo: categoría, archivo/línea, severidad esperada y justificación. Incluir negativos similares para medir sobrealerta. No usar código privado.

Casos iniciales sugeridos: `eval`, `exec`, `pickle.loads`, `subprocess` con `shell=True`, secreto aparente; negativos con nombres de variables coincidentes en comentarios o documentación; un bug de límite que requiere razonamiento contextual para la futura evaluación LLM.

## Métricas

- Precisión = verdaderos positivos / todos los hallazgos emitidos.
- Cobertura/recall = casos sembrados detectados / casos positivos del corpus.
- Falsos positivos por cambio y por categoría.
- Validez de ubicación: porcentaje de hallazgos cuya ruta y línea existen en el diff.
- En fase LLM: aceptación humana, coste medio, latencia p50/p95 y tasa de salida inválida.
- En fase de parches: porcentaje de parches aplicables y que pasan los checks aislados.

## Criterios de aceptación propuestos

- 100% de hallazgos con ruta, línea, regla, evidencia y recomendación.
- 100% de los hallazgos apuntan a líneas añadidas del diff.
- Las respuestas del modelo con ubicación o evidencia no verificable se descartan.
- Ningún cambio al repositorio analizado y ninguna ejecución de su código.
- Publicar resultados por regla, incluidos fallos conocidos; no presentar un score aislado como garantía.

## Reproducibilidad

Registrar versión del analizador, commit revisado, base, reglas habilitadas, proveedor/modelo si aplica, configuración, fecha y formato de salida. Fijar el corpus con su licencia y mantenerlo sintético.
