"""Run an offline review against a temporary, synthetic Git repository."""

import argparse
import subprocess
import tempfile
from pathlib import Path

from pr_review.cli import main


def run_git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def main_demo(provider: str | None = None, model: str | None = None) -> int:
    with tempfile.TemporaryDirectory(prefix="pr-review-demo-") as temporary:
        repo = Path(temporary)
        run_git(repo, "init", "--quiet", "--initial-branch=main")
        (repo / "calculator.py").write_text(
            "def calculate(expression: str) -> object:\n    return expression\n",
            encoding="utf-8",
        )
        run_git(repo, "add", "calculator.py")
        run_git(repo, "-c", "user.name=Demo", "-c", "user.email=demo@example.invalid", "commit", "--quiet", "-m", "safe baseline")
        run_git(repo, "tag", "demo-base")

        (repo / "calculator.py").write_text(
            "def calculate(expression: str) -> object:\n    return eval(expression)\n",
            encoding="utf-8",
        )
        run_git(repo, "add", "calculator.py")
        run_git(repo, "-c", "user.name=Demo", "-c", "user.email=demo@example.invalid", "commit", "--quiet", "-m", "synthetic unsafe change")
        arguments = ["--repo", str(repo), "--base", "demo-base", "--format", "markdown"]
        if provider:
            arguments.extend(["--provider", provider])
        if model:
            arguments.extend(["--model", model])
        return main(arguments)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ejecuta una revisión contra un repositorio Git sintético.")
    parser.add_argument("--provider", choices=("openrouter", "gemini", "groq", "ollama"), help="Proveedor opcional para probar la revisión LLM")
    parser.add_argument("--model", help="Modelo opcional para el proveedor seleccionado")
    args = parser.parse_args()
    raise SystemExit(main_demo(provider=args.provider, model=args.model))
