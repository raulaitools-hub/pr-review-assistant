# Proveedores de prueba

Las cuotas y los modelos disponibles cambian; comprueba siempre el panel del proveedor antes de una demo. Para una ejecución LLM, el programa envía las líneas añadidas del diff. Usa código sintético o público mientras evalúas servicios gratuitos.

## Integración disponible

| Proveedor | Cómo elegirlo | Credencial | Valor por defecto | Nota |
|---|---|---|---|---|
| OpenRouter | `--provider openrouter` | `OPENROUTER_API_KEY` | `nvidia/nemotron-3-ultra-550b-a55b:free` | Se aceptan solo IDs terminados en `:free`; disponibilidad y cuota variables. |
| Gemini API | `--provider gemini` o `--llm` | `GEMINI_API_KEY` | `gemini-3.5-flash` | Respondió a la prueba manual del usuario; la revisión estructurada del proyecto aún requiere una ejecución real. El modelo puede cambiarse con `--model` o `GEMINI_MODEL`. |
| GroqCloud | `--provider groq` | `GROQ_API_KEY` | `GROQ_MODEL` o `openai/gpt-oss-120b` | API compatible con OpenAI y tier gratuito con límites por modelo/cuenta. Revisa qué modelos tiene habilitados tu proyecto. |
| Ollama local | `--provider ollama` | Ninguna | `qwen2.5-coder:7b` | Requiere que Ollama esté instalado, el modelo descargado y su servicio local activo. No envía el diff a un proveedor externo. |

Ejemplos:

```powershell
pr-review --base origin/main --provider groq --format markdown
pr-review --base origin/main --provider ollama --format json
```

`--model` permite elegir otro modelo. Para Groq también se puede establecer `GROQ_MODEL`; para Gemini, `GEMINI_MODEL`.

## Servicios gratuitos adicionales

| Servicio | Situación de prueba observada | Consideraciones |
|---|---|---|
| OpenRouter | Modelos `:free` y router `openrouter/free`; el plan gratuito indica hasta 50 solicitudes/día. | Límites y disponibilidad por modelo pueden cambiar; las solicitudes se encaminan a proveedores participantes. La integración exige IDs terminados en `:free`. |
| Cerebras | La página oficial ofrece actualmente $5 en créditos iniciales al crear cuenta. | Prueba de bienvenida, no una cuota gratuita permanente. No está integrado. |
| Hugging Face Inference Providers | Las páginas de precios actuales muestran que cuentas gratuitas no reciben créditos mensuales incluidos. | Puede servir con créditos comprados o planes de pago; no lo elegiría como API gratuita estable. |
| Mistral | Su modo Free cubre productos como Vibe/Studio, no la API. | La API requiere activar facturación. |

## Recomendación para este portfolio

1. Probar OpenRouter con Nemotron, el modelo utilizado en el otro proyecto multiagente.
2. Mantener Groq y Gemini como alternativas, sujetos a disponibilidad y cuota.
3. Cambiar `OPENROUTER_MODEL` a otro modelo `:free` si el predeterminado deja de estar disponible.
4. Usar Ollama para una demo sin depender de internet, aceptando menor capacidad por el tamaño del GPU local.

La ruta LLM consume tres solicitudes por revisión, una por especialidad. Si una falla tras reintentos, el informe conserva lo que produjo el análisis determinista y registra el aviso.

## Privacidad

- Google señala que en el nivel gratuito puede usar las entradas para mejorar sus productos.
- Groq indica que las entradas y salidas de inferencia no se conservan por defecto, aunque puede registrar temporalmente contenido para fiabilidad o abuso; esos registros pueden durar hasta 30 días salvo controles como Zero Data Retention.
- OpenRouter reenvía solicitudes a los proveedores del modelo seleccionado; revisa las políticas del modelo y del proveedor concreto.
- Ollama procesa solicitudes en el servidor local si se configura con `127.0.0.1`.

Fuentes oficiales: [precios Gemini](https://ai.google.dev/gemini-api/docs/pricing), [límites Groq](https://console.groq.com/docs/rate-limits), [JSON estructurado de Groq](https://console.groq.com/docs/structured-outputs), [modelos Groq](https://console.groq.com/docs/models), [datos Groq](https://console.groq.com/docs/your-data), [modelos gratis OpenRouter](https://openrouter.ai/collections/free-models), [precios y límites OpenRouter](https://openrouter.ai/pricing), [precios Cerebras](https://www.cerebras.ai/pricing), [precios Hugging Face](https://huggingface.co/docs/inference-providers/main/pricing) y [planes Mistral](https://docs.mistral.ai/admin/billing-usage/usage-limits).
