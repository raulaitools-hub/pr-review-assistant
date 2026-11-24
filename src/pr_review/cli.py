import argparse
import sys
from pathlib import Path

from .config import load_env
from .git_diff import DiffError, read_added_lines
from .gemini import GeminiReviewer
from .groq import GroqReviewer
from .ollama import OllamaReviewer
from .openrouter import OpenRouterReviewer
from .provider_common import ReviewProviderError
from .report import render_json, render_markdown
from .rules import inspect_changed_lines


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Revisa líneas añadidas de un diff Git sin ejecutar el código.")
    parser.add_argument("--base", required=True, help="Referencia Git base, por ejemplo origin/main")
    parser.add_argument("--repo", default=".", help="Ruta del repositorio (por defecto: directorio actual)")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", help="Escribe el informe en esta ruta; por defecto usa stdout")
    parser.add_argument("--llm", action="store_true", help="Alias de --provider gemini")
    parser.add_argument("--provider", choices=("openrouter", "gemini", "groq", "ollama"), help="Proveedor LLM; envía el diff al proveedor o servidor local")
    parser.add_argument("--model", help="Sobrescribe el modelo configurado para el proveedor seleccionado")
    return parser


def review_lines(changed, provider, model=None):
    findings = inspect_changed_lines(changed)
    warnings: list[str] = []
    if provider:
        try:
            if provider == "openrouter":
                reviewer = OpenRouterReviewer(model=model)
            elif provider == "gemini":
                reviewer = GeminiReviewer(model=model)
            elif provider == "groq":
                reviewer = GroqReviewer(model=model)
            else:
                reviewer = OllamaReviewer(model=model)
            for role in ("correctness", "security", "tests"):
                try:
                    findings.extend(reviewer.review(role, changed))
                except ReviewProviderError as exc:
                    warnings.append(f"Revisor {role} ({provider}): {exc}")
                    break
        except ReviewProviderError as exc:
            warnings.append(f"Proveedor {provider} no disponible: {exc}")
    return findings, warnings


def main(argv: list[str] | None = None) -> int:
    load_env()
    args = build_parser().parse_args(argv)
    try:
        changed = read_added_lines(args.base, args.repo)
    except DiffError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    provider = args.provider or ("gemini" if args.llm else None)
    findings, warnings = review_lines(changed, provider, args.model)
    if warnings:
        print("Aviso: se generará el informe con los resultados disponibles.", file=sys.stderr)
    report = render_json(args.base, findings, warnings) if args.format == "json" else render_markdown(args.base, findings, warnings)
    if args.output:
        try:
            Path(args.output).write_text(report, encoding="utf-8")
        except OSError as exc:
            print(f"No se pudo escribir el informe: {exc}", file=sys.stderr)
            return 2
    else:
        print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
