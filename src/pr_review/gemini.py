import json
import os
import time
import urllib.error
import urllib.request
from collections.abc import Iterable

from .models import ChangedLine, Finding
from .provider_common import ROLES, ReviewProviderError, make_review_prompt, validate_findings

DEFAULT_MODEL = "gemini-3.5-flash"
RESPONSE_SCHEMA: dict[str, object] = {
    "type": "OBJECT",
    "properties": {
        "findings": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "title": {"type": "STRING"},
                    "category": {"type": "STRING"},
                    "severity": {"type": "STRING", "enum": ["critical", "high", "medium", "low", "info"]},
                    "path": {"type": "STRING"},
                    "line": {"type": "INTEGER"},
                    "evidence": {"type": "STRING"},
                    "recommendation": {"type": "STRING"},
                    "confidence": {"type": "NUMBER"},
                },
                "required": ["title", "category", "severity", "path", "line", "evidence", "recommendation", "confidence"],
            },
        }
    },
    "required": ["findings"],
}


class GeminiError(ReviewProviderError):
    """Raised for configuration, transport, or response errors from Gemini."""


class GeminiReviewer:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
        if not self.api_key:
            raise GeminiError("Falta GEMINI_API_KEY. Crea una clave en Google AI Studio y configúrala como variable de entorno.")

    def review(self, role: str, lines: Iterable[ChangedLine]) -> list[Finding]:
        if role not in ROLES:
            raise ValueError(f"Rol desconocido: {role}")
        changed = list(lines)
        if not changed:
            return []
        prompt = make_review_prompt(role, changed)
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json", "responseSchema": RESPONSE_SCHEMA},
        }
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "x-goog-api-key": self.api_key},
            method="POST",
        )
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    response_data = json.loads(response.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")[:1000]
                if exc.code == 503 and attempt < 2:
                    time.sleep(1 + 2 * attempt)
                    continue
                raise GeminiError(f"Gemini respondió HTTP {exc.code}: {detail}") from exc
            except (urllib.error.URLError, TimeoutError) as exc:
                if attempt < 2:
                    time.sleep(1 + 2 * attempt)
                    continue
                raise GeminiError(f"No se pudo completar la solicitud a Gemini: {exc}") from exc
            except json.JSONDecodeError as exc:
                raise GeminiError(f"Gemini devolvió una respuesta JSON inválida: {exc}") from exc
        try:
            text = response_data["candidates"][0]["content"]["parts"][0]["text"]
            result = json.loads(text)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise GeminiError("Gemini devolvió una respuesta vacía o con formato inesperado.") from exc
        return validate_findings(role, result, changed, source="gemini")
