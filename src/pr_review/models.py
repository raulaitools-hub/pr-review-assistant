from dataclasses import asdict, dataclass
from typing import Literal

Severity = Literal["critical", "high", "medium", "low", "info"]


@dataclass(frozen=True)
class ChangedLine:
    path: str
    line: int
    content: str


@dataclass(frozen=True)
class Finding:
    rule_id: str
    title: str
    category: str
    severity: Severity
    path: str
    line: int
    evidence: str
    recommendation: str
    confidence: float = 1.0
    source: str = "deterministic"

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
