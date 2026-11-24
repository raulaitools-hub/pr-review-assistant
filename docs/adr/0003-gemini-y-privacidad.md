# ADR 0003: Gemini optativo para revisión especializada

- Estado: aceptada
- Fecha: 2026-11-18

## Contexto

El proyecto necesita una demo real de análisis semántico, pero también debe seguir siendo ejecutable sin coste ni credenciales. Para entrevistas resulta valioso enseñar tanto el análisis determinista como una ruta LLM.

## Decisión

Se integra Gemini mediante REST y biblioteca estándar de Python. `--llm` activa tres revisiones especializadas y requiere `GEMINI_API_KEY`. El modo determinista permanece disponible y es el valor predeterminado. El modelo se configura por CLI o variable de entorno.

## Privacidad y costes

La solicitud envía las líneas añadidas del diff a Google. El nivel gratuito ofrece cuotas limitadas y puede usar entradas para mejorar productos según la página de precios; por tanto, para demos se recomienda usar código sintético o público. No se incluye la clave en el repositorio.

## Consecuencias

La aplicación tiene una demo semántica funcional sin añadir dependencias. Se hacen tres llamadas por análisis y los límites del proveedor pueden afectar la demo. Las respuestas estructuradas se vuelven a validar localmente antes de incluirlas en el informe.
