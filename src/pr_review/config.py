"""Load project-local credentials without overriding the process environment."""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_env() -> None:
    path = PROJECT_ROOT / ".env"
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name, value = name.strip(), value.strip()
        if name not in {"GEMINI_API_KEY", "GROQ_API_KEY", "OPENROUTER_API_KEY", "GEMINI_MODEL", "GROQ_MODEL", "OPENROUTER_MODEL"}:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        os.environ.setdefault(name, value)
