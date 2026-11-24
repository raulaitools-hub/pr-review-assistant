# Arquitectura

## Flujo

1. La CLI recibe una referencia base y una ruta local.
2. `git_diff` ejecuta `git diff --unified=0 BASE...HEAD` con argumentos separados, límite de tiempo y sin shell.
3. El parser conserva ruta, número de línea y contenido de cada línea añadida.
4. Las reglas inspeccionan solo los archivos Python modificados.
5. Si se selecciona un proveedor, tres revisores reciben las líneas añadidas con especialidades distintas.
6. La salida estructurada se valida localmente; se descartan hallazgos cuya ruta, línea o evidencia no pertenezcan al diff.
7. Los resultados se representan como `Finding`, un modelo independiente del formato de salida.
8. `report` emite Markdown o JSON y `scoring` calcula un indicador explicable.

## Límites entre componentes

- `cli`: argumentos, errores de usuario y destino del informe.
- `git_diff`: frontera con Git y extracción del diff.
- `rules`: reglas deterministas puras sobre líneas cambiadas.
- `models`: tipos de datos compartidos.
- `scoring`: cálculo transparente y determinista.
- `report`: presentación, sin lógica de detección.

## Evolución hacia LLM

Cada revisor recibe solo las líneas añadidas y devuelve JSON validado contra un esquema. Gemini, Groq y Ollama comparten la misma validación de ruta, línea y evidencia textual. Se descartan observaciones sin soporte exacto. La ejecución determinista sigue disponible como baseline reproducible.

Se introduciría LangGraph si la ejecución necesita bifurcación, reintentos, persistencia o pausas humanas. En el MVP el flujo lineal es más sencillo y auditable.

## Fallos y degradación

Un error de Git termina con código distinto de cero y un mensaje concreto. Gemini reintenta errores HTTP 503, fallos de conexión y timeouts con pausas breves; Groq reintenta errores HTTP transitorios. Si un proveedor sigue sin responder, el informe conserva los hallazgos deterministas e incluye un aviso. El modo sin LLM sigue funcionando independientemente de la red. Los hallazgos heurísticos nunca bloquean por sí solos un merge.
