import subprocess

from .models import ChangedLine


class DiffError(RuntimeError):
    """Raised when Git cannot provide the requested diff."""


def read_added_lines(base: str, cwd: str = ".") -> list[ChangedLine]:
    """Return added diff lines with their new-file line numbers."""
    try:
        result = subprocess.run(
            ["git", "diff", "--no-ext-diff", "--unified=0", f"{base}...HEAD", "--"],
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise DiffError(f"No se pudo ejecutar git diff: {exc}") from exc
    if result.returncode:
        detail = result.stderr.strip() or "Git devolvió un error sin detalle."
        raise DiffError(detail)

    changed: list[ChangedLine] = []
    path: str | None = None
    new_line = 0
    for raw in result.stdout.splitlines():
        if raw.startswith("+++ b/"):
            path = raw[6:]
        elif raw.startswith("+++ /dev/null"):
            path = None
        elif raw.startswith("@@"):
            try:
                new_range = raw.split("+")[1].split(" ")[0]
                start, _, _count = new_range.partition(",")
                new_line = int(start)
            except (IndexError, ValueError):
                path = None
        elif raw.startswith("+") and not raw.startswith("+++"):
            if path is not None:
                changed.append(ChangedLine(path, new_line, raw[1:]))
            new_line += 1
        elif raw.startswith("-") and not raw.startswith("---"):
            continue
        elif not raw.startswith("\\") and path is not None and raw.startswith(" "):
            new_line += 1
    return changed
