# Modelo de amenazas

## Activos

- Código fuente, credenciales locales y token de GitHub (solo en una fase futura).
- Integridad de los comentarios de revisión y confianza en el informe.

## Límites de confianza

- Todo archivo, diff, nombre de rama, comentario y documentación del repositorio analizado se considera entrada no confiable.
- La salida del modelo se considera no confiable hasta validarla.
- El analizador no ejecuta archivos del repositorio. En modo determinista no envía el diff a un servicio externo; al seleccionar OpenRouter, Gemini o Groq, transmite las líneas añadidas del diff al proveedor configurado.

## Riesgos y mitigaciones

| Riesgo | Mitigación actual o futura |
|---|---|
| Comandos maliciosos del repositorio | No ejecutar tests, hooks, scripts ni dependencias del proyecto en el MVP. |
| Prompt injection en comentarios o código | En fase LLM, separar instrucciones de datos; no conceder herramientas de escritura/ejecución; validar salida. |
| Filtrado de código a un proveedor | Proveedores externos son opt-in mediante `--provider`; se envían solo líneas añadidas. Ollama apunta a localhost. No usar APIs externas con código privado sin autorización. |
| Salida inventada o ubicación falsa | Exigir evidencia y validar que ruta/línea pertenezcan al diff. |
| Fuga de credenciales | No leer `.env`; no registrar secretos; permisos mínimos para futura GitHub App. |
| PR de fork ejecutado con secretos | En CI futuro, separar análisis de datos de ejecución de código; no usar `pull_request_target` para ejecutar código no confiable; token de solo lectura. |
| Reglas regex incompletas | Presentar detecciones como señales, probar casos positivos y negativos, y no afirmar cobertura total. |

## Supuestos

El usuario invoca el CLI en un repositorio bajo su control. Las referencias de Git son argumentos de proceso, no shell. La extensión GitHub debe diseñarse de nuevo alrededor de permisos y aislamiento antes de habilitarla.
