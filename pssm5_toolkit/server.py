"""Standalone web server for the APE PFAC PSSM 5 toolkit."""

from __future__ import annotations

import json
import mimetypes
import os
from pathlib import Path
from wsgiref.simple_server import make_server

from .toolkit import build_toolkit

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"


def _json(start_response, payload, status="200 OK"):
    body = json.dumps(payload, indent=2).encode("utf-8")
    start_response(
        status,
        [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(body))),
            ("Cache-Control", "no-store"),
            ("Access-Control-Allow-Origin", "*"),
        ],
    )
    return [body]


def _asset(start_response, target: Path):
    if not target.is_file():
        return _json(start_response, {"error": "not_found"}, "404 Not Found")
    body = target.read_bytes()
    content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
    start_response(
        "200 OK",
        [
            ("Content-Type", content_type),
            ("Content-Length", str(len(body))),
            ("Cache-Control", "public, max-age=300"),
        ],
    )
    return [body]


def application(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    if path == "/api/health":
        return _json(
            start_response,
            {
                "status": "ok",
                "service": "ape-pfac-pssm5-toolkit",
                "project_identity": "MPH Applied Practice Experience",
                "scope": "PSSM 5 Patient and Family Engagement only",
                "boundary": "Standalone. Not connected to Hedge Desk or any finance project.",
            },
        )
    if path == "/api/toolkit":
        return _json(start_response, build_toolkit())
    relative = "index.html" if path in ("/", "") else path.lstrip("/")
    target = (WEB / relative).resolve()
    web_root = WEB.resolve()
    if target != web_root and web_root not in target.parents:
        return _json(start_response, {"error": "invalid_path"}, "400 Bad Request")
    if not target.is_file():
        target = WEB / "index.html"
    return _asset(start_response, target)


def main():
    port = int(os.getenv("PORT", "8765"))
    with make_server("0.0.0.0", port, application) as server:
        print(f"APE PFAC PSSM 5 toolkit listening on {port}", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()
