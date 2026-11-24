import json
import os
import time
import urllib.error
import urllib.request
from collections.abc import Iterable

from .models import ChangedLine, Finding
from .provider_common import FINDINGS_JSON_SCHEMA, ROLES, ReviewProviderError, make_review_prompt, validate_findings

DEFAULT_MODEL = "openai/gpt-oss-120b"


class GroqReviewer:
    """OpenAI-compatible review client for GroqCloud."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model or os.getenv("GROQ_MODEL", DEFAULT_MODEL)
        if not self.api_key:
            raise ReviewProviderError("Falta GROQ_API_KEY. Configúrala como variable de entorno para usar Groq.")

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
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": "code_review_findings", "strict": True, "schema": FINDINGS_JSON_SCHEMA},
            },
        }
        request = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "pr-review-assistant/0.1.0",
            },
            method="POST",
        )
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    response_data = json.loads(response.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")[:1000]
                if exc.code == 403 and "1010" in detail:
                    raise ReviewProviderError(
                        "Groq/Cloudflare bloqueó la firma del cliente (HTTP 403, código 1010). "
                        "No parece un error de cuota ni de modelo; la petición identifica la aplicación "
                        "con User-Agent. Si persiste, comparte el mensaje y cualquier Ray ID de la respuesta, nunca la clave."
                    ) from exc
                if exc.code in {429, 500, 502, 503, 504} and attempt < 2:
                    retry_after = exc.headers.get("retry-after") if exc.code == 429 else None
                    try:
                        wait = min(float(retry_after), 20) if retry_after else 1 + 2 * attempt
                    except ValueError:
                        wait = 1 + 2 * attempt
                    time.sleep(wait)
                    continue
                raise ReviewProviderError(f"Groq respondió HTTP {exc.code}: {detail}") from exc
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                raise ReviewProviderError(f"No se pudo completar la solicitud a Groq: {exc}") from exc
        try:
            text = response_data["choices"][0]["message"]["content"]
            result = json.loads(text)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise ReviewProviderError("Groq devolvió una respuesta vacía o con formato inesperado.") from exc
        return validate_findings(role, result, changed, source="groq")
