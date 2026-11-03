"""Small localhost-only NOVA demo. No browser-side API secrets."""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files

from .catalog import OPERATORS, load_seeds
from .engine import NovaEngine, artifact
from .llm import ModelError


def make_handler(engine: NovaEngine):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, status: int, payload: bytes, content_type: str):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; object-src 'none'; base-uri 'none'")
            self.end_headers()
            self.wfile.write(payload)

        def _json(self, status: int, data: dict):
            self._send(status, json.dumps(data, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

        def do_GET(self):
            if self.path == "/":
                page = files("nova").joinpath("static/index.html").read_bytes()
                self._send(200, page, "text/html; charset=utf-8")
            elif self.path == "/api/health":
                self._json(200, {"status": "ok", "mode": "model-unverified" if engine.model else "template-demo", "operators": [
                    {"id": k, "label": v["label"]} for k, v in OPERATORS.items()],
                    "domains": sorted({seed["domain"] for seed in load_seeds()})})
            else:
                self._json(404, {"error": "not found"})

        def do_POST(self):
            if self.path != "/api/roll":
                return self._json(404, {"error": "not found"})
            origin = self.headers.get("Origin")
            if origin and origin not in {f"http://127.0.0.1:{self.server.server_port}",
                                         f"http://localhost:{self.server.server_port}"}:
                return self._json(403, {"error": "cross-origin request rejected"})
            if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
                return self._json(415, {"error": "application/json required"})
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 4096:
                    return self._json(413, {"error": "invalid request size"})
                request = json.loads(self.rfile.read(length))
                if not isinstance(request, dict):
                    raise ValueError("request must be a JSON object")
                count = request.get("count", 3)
                if isinstance(count, bool) or not isinstance(count, int) or count > 5:
                    raise ValueError("count must be an integer <= 5")
                seed = request.get("seed", None)
                if seed is not None and (isinstance(seed, bool) or not isinstance(seed, int)):
                    raise ValueError("seed must be an integer")
                domain = request.get("domain") or None
                op = request.get("operator") or None
                if domain is not None and not isinstance(domain, str):
                    raise ValueError("invalid domain")
                if op is not None and not isinstance(op, str):
                    raise ValueError("invalid operator")
                result = artifact(engine.roll(count=count, seed=seed, domain=domain, operator=op))
            except (ValueError, json.JSONDecodeError) as exc:
                return self._json(400, {"error": str(exc)[:180]})
            except ModelError:
                return self._json(502, {"error": "model call failed; check the local server configuration"})
            self._json(200, result)

        def log_message(self, format, *args):
            return  # no URL or confidential prompt logs

    return Handler


def serve_local(engine: NovaEngine, port: int = 8765):
    if not 1 <= port <= 65535:
        raise ValueError("port must be 1..65535")
    with ThreadingHTTPServer(("127.0.0.1", port), make_handler(engine)) as httpd:
        print(f"NOVA local UI: http://127.0.0.1:{httpd.server_port}/ (Ctrl+C to stop)")
        httpd.serve_forever(poll_interval=0.2)
