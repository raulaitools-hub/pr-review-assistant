# Modelo local para este equipo

La inspección local del entorno informa de una NVIDIA GeForce RTX 3070 Laptop con 8 GB de VRAM, 16 procesadores lógicos y alrededor de 16 GB de memoria de sistema. No se instaló ni descargó software.

## Recomendación de prueba

El primer candidato es `qwen2.5-coder:7b` en Ollama: es un modelo orientado a código y la variante publicada ocupa aproximadamente 4.7 GB con contexto listado de 32K. Cabe mejor que modelos de 14B/30B en el GPU de 8 GB, dejando margen para el runtime y otros procesos.

También se puede comparar `qwen3.5:4b`, que aparece con un tamaño de 3.3–4.0 GB y ventana publicada de 256K. Es más reciente, pero más general y un contexto máximo enorme consume memoria adicional; para comparar en esta máquina conviene mantener el contexto de la aplicación pequeño.

Los tamaños descargables no son equivalentes al total de VRAM necesario durante inferencia. Si el escritorio o el runtime agotan la VRAM, Ollama puede repartir trabajo entre GPU y RAM, con menor velocidad.

## Preparar más adelante

Con Ollama instalado y un modelo descargado, la CLI ya puede usar su API local:

```powershell
ollama run qwen2.5-coder:7b
pr-review --base origin/main --provider ollama
```

El primer comando descarga el modelo si todavía no está en el equipo. No se ejecutó desde Codex.

Fuentes: [Qwen2.5-Coder en Ollama](https://ollama.com/library/qwen2.5-coder), [Qwen3.5 en Ollama](https://ollama.com/library/qwen3.5).
