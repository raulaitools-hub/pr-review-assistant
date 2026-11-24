import json

from .models import Finding
from .scoring import score_findings


def render_json(base: str, findings: list[Finding], warnings: list[str] | None = None) -> str:
    result: dict[str, object] = {
        "schema_version": "1.0",
        "base": base,
        "score": score_findings(findings),
        "findings": [item.to_dict() for item in findings],
    }
    if warnings:
        result["warnings"] = warnings
    return json.dumps(result, ensure_ascii=False, indent=2)


def render_markdown(base: str, findings: list[Finding], warnings: list[str] | None = None) -> str:
    score = score_findings(findings)
    parts = [
        "# Informe de revisión", "",
        f"- Base: `{base}`", "- Alcance: líneas añadidas del diff", "- Ejecución de código: no", "",
        f"## Puntuación orientativa: {score['score']}/100", "",
        str(score["explanation"]), "", "## Hallazgos", "",
    ]
    if not findings:
        parts.append("No se detectaron hallazgos por las reglas habilitadas. Esto no demuestra que el cambio esté libre de defectos.")
    if warnings:
        parts.extend(["", "## Avisos", ""])
        parts.extend(f"- {warning}" for warning in warnings)
    for finding in findings:
        evidence = finding.evidence.replace("`", "\\`")
        parts.extend([
            f"### [{finding.severity.upper()}] {finding.title} (`{finding.rule_id}`)",
            f"`{finding.path}:{finding.line}` · {finding.category}", "",
            f"Evidencia: `{evidence}`", "",
            f"Recomendación: {finding.recommendation}", "",
        ])
    return "\n".join(parts).rstrip() + "\n"
