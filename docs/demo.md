# Demo local sin API

La demo crea un repositorio temporal con dos commits: una base y un cambio sintético que llama a `eval`. El analizador detecta la línea con la regla `PY001` y muestra un informe Markdown. No se ejecuta el código sintético ni se modifica el workspace.

## Requisitos

- Python 3.11 o superior.
- Git.
- Instalación editable del proyecto (`python -m pip install -e .`).

## Ejecutar

Desde la raíz del proyecto:

```powershell
python examples/demo.py
```

Para probar la integración LLM contra el cambio sintético, configura la clave del proveedor en el entorno y ejecuta:

```powershell
python examples/demo.py --provider gemini
```

Esto realiza tres solicitudes (corrección, seguridad y tests) con `gemini-3.5-flash` por defecto. Para probar un modelo distinto, añade `--model <id>`. El diff solo contiene el ejemplo sintético y el repositorio temporal se elimina al terminar; el informe queda en pantalla.

El repositorio temporal se elimina automáticamente al terminar. La demo es independiente de proveedores LLM y sirve para presentar el flujo aunque ninguno esté disponible.

## Qué explicar en entrevista

1. El CLI obtiene solo líneas añadidas con `git diff`.
2. La regla determinista activa `PY001` sobre el patrón sintético.
3. El informe indica evidencia, ubicación y mitigación.
4. `--provider gemini`, `--provider groq` o `--provider ollama` puede enriquecer el análisis, manteniendo el modo reproducible local como baseline.
