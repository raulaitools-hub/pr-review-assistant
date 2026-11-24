"""Local-only interface for reviewing a Git diff."""
import json
import os
import secrets
import subprocess
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from .config import PROJECT_ROOT, load_env
from .cli import review_lines
from .models import ChangedLine
from .report import render_json

TOKEN = secrets.token_urlsafe(32)
ASSETS = PROJECT_ROOT / "web"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass

    def respond(self, status: int, content: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self) -> None:
        if self.headers.get("Host") != f"127.0.0.1:{self.server.server_port}":
            return self.respond(403, b"Forbidden", "text/plain")
        path = urlsplit(self.path).path
        if path == "/api/session":
            return self.respond(200, json.dumps({"token": TOKEN}).encode(), "application/json")
        names = {"/": ("index.html", "text/html; charset=utf-8"), "/app.js": ("app.js", "text/javascript; charset=utf-8"), "/style.css": ("style.css", "text/css; charset=utf-8")}
        if path not in names:
            return self.respond(404, b"Not found", "text/plain")
        name, mime = names[path]
        self.respond(200, (ASSETS / name).read_bytes(), mime)

    def do_POST(self) -> None:
        expected = f"http://127.0.0.1:{self.server.server_port}"
        if self.path != "/api/review" or self.headers.get("Host") != f"127.0.0.1:{self.server.server_port}" or self.headers.get("Origin") != expected or self.headers.get("X-Review-Token") != TOKEN:
            return self.respond(403, b"Forbidden", "text/plain")
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 1600000:
                raise ValueError("Solicitud inválida")
            data = json.loads(self.rfile.read(size))
            if data.get("mode") == "file":
                name, content, provider = data["name"], data["content"], data["provider"]
                if (not isinstance(name, str) or not name.strip() or len(name) > 255
                    or any(c in name for c in "/\\\x00\r\n")
                    or not isinstance(content, str) or not content or "\x00" in content
                    or len(content.encode("utf-8")) > 262144
                    or provider not in {"local", "openrouter", "groq", "gemini", "ollama"}):
                    raise ValueError("Selecciona un archivo de texto UTF-8 no vacío de hasta 256 KB.")
                load_env()
                lines = [ChangedLine(name, number, line) for number, line in enumerate(content.splitlines(), 1)]
                findings, warnings = review_lines(lines, None if provider == "local" else provider)
                report = json.loads(render_json(name, findings, warnings))
                report["scope"] = "file"
                return self.respond(200, json.dumps(report, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")
            repo, base, provider = data["repo"], data["base"], data["provider"]
            if not all(isinstance(x, str) and x.strip() for x in (repo, base, provider)) or provider not in {"local", "openrouter", "groq", "gemini", "ollama"} or base.startswith("-"):
                raise ValueError("Comprueba la ruta, la base y el proveedor.")
            args = [sys.executable, "-m", "pr_review", "--repo", repo, "--base", base, "--format", "json"]
            if provider != "local":
                args += ["--provider", provider]
            child_env = os.environ.copy()
            child_env["PYTHONIOENCODING"] = "utf-8"
            result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=650, env=child_env)
            if result.returncode:
                raise ValueError(result.stderr.strip() or "No se pudo realizar la revisión.")
            report = json.loads(result.stdout)
            report["scope"] = "diff"
            self.respond(200, json.dumps(report, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")
        except (ValueError, KeyError, TypeError, json.JSONDecodeError, subprocess.TimeoutExpired, OSError) as exc:
            self.respond(400, json.dumps({"error": str(exc)}, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")


def main() -> None:
    load_env()
    server = ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
    url = "http://127.0.0.1:8765/"
    print(f"Interfaz disponible en {url} (Ctrl+C para cerrar)")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
