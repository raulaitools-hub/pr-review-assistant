import json
import urllib.error
import urllib.request
from collections.abc import Iterable

from .models import ChangedLine, Finding
from .provider_common import FINDINGS_JSON_SCHEMA, ROLES, ReviewProviderError, make_review_prompt, validate_findings

DEFAULT_MODEL = "qwen2.5-coder:7b"


class OllamaReviewer:
    """Optional local reviewer using an Ollama server on localhost."""

    def __init__(self, model: str | None = None, endpoint: str = "http://127.0.0.1:11434/api/chat") -> None:
        self.model = model or DEFAULT_MODEL
        self.endpoint = endpoint

    def review(self, role: str, lines: Iterable[ChangedLine]) -> list[Finding]:
        if role not in ROLES:
            raise ValueError(f"Rol desconocido: {role}")
        changed = list(lines)
        if not changed:
            return []
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "Eres un revisor de código. Responde solo con el objeto JSON requerido."},
                {"role": "user", "content": make_review_prompt(role, changed)},
            ],
            "format": FINDINGS_JSON_SCHEMA,
            "stream": False,
        }
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                response_data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:1000]
            raise ReviewProviderError(f"Ollama respondió HTTP {exc.code}: {detail}") from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise ReviewProviderError(f"No se pudo conectar con Ollama en {self.endpoint}: {exc}") from exc
        try:
            result = json.loads(response_data["message"]["content"])
        except (KeyError, TypeError, json.JSONDecodeError) as exc:
            raise ReviewProviderError("Ollama devolvió una respuesta vacía o con formato inesperado.") from exc
        return validate_findings(role, result, changed, source="ollama")
