# Desarrollo

## Requisitos

- Python 3.11 o superior.
- Git disponible en PATH.
- Ninguna API key ni paquete de terceros para el modo determinista.

## Instalación editable

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

## Flujo recomendado

1. Crear una rama y preparar un cambio pequeño en un repositorio de ejemplo.
2. Ejecutar `pr-review --base <referencia>` desde ese repositorio.
3. Revisar cada ubicación y comparar el JSON con el Markdown.
4. Añadir un caso sintético positivo y uno negativo al corpus antes de modificar reglas.

No se instala ni se invoca el código del repositorio objetivo. La validación automatizada y el corpus ejecutable quedan como siguiente tarea de ingeniería.

## Privacidad

La interfaz se inicia con `python -m pr_review.web` y escucha únicamente en `127.0.0.1:8765`. El selector de archivos analiza el contenido completo (texto UTF-8, hasta 256 KB); también se pueden analizar cambios de repositorios locales. Presenta informes con una gráfica de severidad. La clave se lee desde el entorno o el `.env` de la raíz, nunca desde el navegador. OpenRouter es el proveedor seleccionado inicialmente; solo se aceptan modelos terminados en `:free` y se desactiva el cambio automático de proveedor. La cuota y disponibilidad pueden variar.

El modo determinista solo consulta Git local. OpenRouter, Gemini y Groq son opcionales y transmiten las líneas añadidas del diff al proveedor elegido. Ollama puede procesar la solicitud localmente.

## Gemini opcional

1. Crea una clave en [Google AI Studio](https://aistudio.google.com/app/apikey).
2. En PowerShell, cárgala para la sesión actual con entrada oculta:

   ```powershell
   $secureKey = Read-Host "Mi Api de Gemini" -AsSecureString
   $keyPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
   try { $env:GEMINI_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($keyPointer) }
   finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($keyPointer) }
   ```

   No la subas al repositorio ni la pegues en archivos versionados. Esta variable dura solo mientras siga abierta esa sesión de PowerShell.
3. Ejecuta la CLI con `--llm` o `--provider gemini`; se hacen tres solicitudes, una por especialidad.
4. El modelo predeterminado es `gemini-3.5-flash`, que respondió a una prueba básica desde PowerShell el 18/11/2026. Para probar otro modelo sin editar el proyecto, usa `--model gemini-4-hydrogen` en el comando o establece `$env:GEMINI_MODEL = "gemini-4-hydrogen"` en la sesión actual. Solo funcionará si Google lo habilita para tu clave. La prueba básica no sustituye a la comprobación de la salida estructurada de esta aplicación.

Google ofrece acceso gratuito con cuotas limitadas para determinados modelos; las cuotas pueden cambiar. En el nivel gratuito, Google indica que puede utilizar las entradas para mejorar productos. Para demos, usa cambios sintéticos o código público y revisa la [tarifa y condiciones vigentes](https://ai.google.dev/gemini-api/docs/pricing).

## Groq opcional

1. Crea una clave en [Groq Console](https://console.groq.com/keys).
2. En la misma ventana de PowerShell donde ejecutarás el programa, cárgala sin mostrarla ni guardarla en el repositorio:

   ```powershell
   $secureKey = Read-Host "Clave de Groq" -AsSecureString
   $keyPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
   try { $env:GROQ_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($keyPointer) }
   finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($keyPointer) }
   ```

   La variable dura solo mientras siga abierta esa sesión de PowerShell. No pegues la clave en el chat ni la añadas a archivos.
3. Ejecuta `pr-review --base <referencia> --provider groq`. El modelo usa `GROQ_MODEL` o `openai/gpt-oss-120b`; si ese ID no está habilitado en tu cuenta, selecciona un modelo compatible del panel de Groq.

El tier gratuito tiene límites por organización/modelo. Consulta los [límites actuales](https://console.groq.com/docs/rate-limits). Las llamadas hacen reintentos acotados ante errores transitorios y respetan `retry-after` en HTTP 429. GPT-OSS 20B y 120B admiten la salida JSON Schema estricta que exige el cliente; otros modelos pueden rechazar ese formato.

## Ollama local opcional

Con Ollama instalado y el servidor local activo, ejecuta `pr-review --base <referencia> --provider ollama`. Por defecto usa `qwen2.5-coder:7b`; puedes elegir otro con `--model`. Consulta el análisis de memoria y GPU en [modelo local](local-model.md).
