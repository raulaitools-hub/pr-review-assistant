"""OpenRouter client restricted to explicitly free model variants."""
import json
import os
import urllib.error
import urllib.request
from collections.abc import Iterable

from .models import ChangedLine, Finding
from .provider_common import FINDINGS_JSON_SCHEMA, ROLES, ReviewProviderError, make_review_prompt, validate_findings

DEFAULT_MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"


class OpenRouterReviewer:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model or os.getenv("OPENROUTER_MODEL") or DEFAULT_MODEL
        if not self.api_key:
            raise ReviewProviderError("Falta OPENROUTER_API_KEY en el entorno o en .env.")
        if not self.model.endswith(":free") or not all(c.isascii() and (c.isalnum() or c in "/-._:") for c in self.model):
            raise ReviewProviderError("OpenRouter requiere un identificador de modelo terminado en :free.")

    def review(self, role: str, lines: Iterable[ChangedLine]) -> list[Finding]:
        if role not in ROLES:
            raise ValueError(f"Rol desconocido: {role}")
        changed = list(lines)
        if not changed:
            return []
        schema = json.dumps(FINDINGS_JSON_SCHEMA, ensure_ascii=False)
        prompt = make_review_prompt(role, changed) + f"\n\nDevuelve únicamente JSON válido con este esquema: {schema}"
        payload = {"model": self.model, "messages": [{"role": "system", "content": "Responde únicamente con un objeto JSON, sin markdown."}, {"role": "user", "content": prompt}], "temperature": 0, "max_tokens": 4096, "provider": {"allow_fallbacks": False}}
        request = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}", "User-Agent": "pr-review-assistant/0.1.0"}, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise ReviewProviderError(f"OpenRouter respondió HTTP {exc.code}. Comprueba la cuota y la disponibilidad del modelo gratuito.") from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise ReviewProviderError(f"No se pudo completar la solicitud a OpenRouter: {exc}") from exc
        try:
            choice = data["choices"][0]
            if choice.get("finish_reason") != "stop":
                raise ReviewProviderError(f"OpenRouter no completó la respuesta (motivo: {choice.get('finish_reason')}).")
            content = choice["message"]["content"]
            result = json.loads(content)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise ReviewProviderError("OpenRouter devolvió una respuesta vacía o JSON inválido.") from exc
        return validate_findings(role, result, changed, source="openrouter")
