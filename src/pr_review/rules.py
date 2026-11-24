import re
from collections.abc import Iterable

from .models import ChangedLine, Finding

RULES: tuple[tuple[str, re.Pattern[str], str, str, str, str], ...] = (
    (
        "PY001", re.compile(r"\beval\s*\("), "Seguridad", "high",
        "Uso de eval()", "Evita evaluar texto como código; valida los datos y usa un parser o una tabla de operaciones permitidas.",
    ),
    (
        "PY002", re.compile(r"\bexec\s*\("), "Seguridad", "high",
        "Uso de exec()", "Evita ejecutar texto dinámico. Sustitúyelo por funciones explícitas y entradas validadas.",
    ),
    (
        "PY003", re.compile(r"\bpickle\.loads?\s*\("), "Seguridad", "high",
        "Deserialización pickle", "No deserialices pickle de fuentes no confiables; considera JSON u otro formato con esquema.",
    ),
    (
        "PY004", re.compile(r"\bsubprocess\.[A-Za-z_]+\s*\([^\n]*\bshell\s*=\s*True"), "Seguridad", "high",
        "Subproceso con shell=True", "Evita shell=True cuando los argumentos incluyan datos variables; pasa una lista de argumentos y valida entradas.",
    ),
    (
        "PY005", re.compile(r"(?i)\b(password|secret|api[_-]?key)\s*=\s*(['\"])[^'\"]{4,}\2"), "Seguridad", "medium",
        "Posible secreto codificado", "Carga el secreto desde un gestor seguro o variable de entorno y rota el valor si era real.",
    ),
)


def inspect_changed_lines(lines: Iterable[ChangedLine]) -> list[Finding]:
    findings: list[Finding] = []
    for item in lines:
        if not item.path.endswith(".py"):
            continue
        for rule_id, pattern, category, severity, title, recommendation in RULES:
            if pattern.search(item.content):
                evidence = item.content.strip()[:240]
                if rule_id == "PY005":
                    evidence = pattern.sub(lambda match: f"{match.group(1)}=<redacted>", evidence)
                findings.append(Finding(
                    rule_id=rule_id,
                    title=title,
                    category=category,
                    severity=severity,  # type: ignore[arg-type]
                    path=item.path,
                    line=item.line,
                    evidence=evidence,
                    recommendation=recommendation,
                ))
    return findings
