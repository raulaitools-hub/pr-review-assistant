from collections import Counter

from .models import Finding

WEIGHTS = {"critical": 30, "high": 15, "medium": 7, "low": 3, "info": 0}


def score_findings(findings: list[Finding]) -> dict[str, object]:
    penalty = sum(WEIGHTS[f.severity] for f in findings)
    counts = dict(Counter(f.severity for f in findings))
    return {
        "score": max(0, 100 - penalty),
        "label": "heuristic review score",
        "penalty_by_severity": WEIGHTS,
        "counts": counts,
        "explanation": "100 menos penalizaciones por hallazgo; una puntuación menor indica más hallazgos de mayor severidad. Es una señal orientativa del diff, no una medida absoluta de calidad ni una certificación de seguridad.",
    }
