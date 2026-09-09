"""Web server for the APE PFAC PSSM 5 toolkit."""

from __future__ import annotations

import json
import mimetypes
import os
from pathlib import Path
from wsgiref.simple_server import make_server

from .hai_dashboard import build_hai_dashboard
from .supabase_backend import backend_status, build_demo_payload, submit_demo_intake

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
CWD_ROOT = Path.cwd()
WEB = CWD_ROOT / "web" if (CWD_ROOT / "web").is_dir() else PACKAGE_ROOT / "web"
REVIEW_FLOW_SCRIPT = b'  <script defer src="/review-flow.js"></script>\n'


def _release_sha() -> str:
    """Return the deployed source revision when the platform exposes it."""
    return (
        os.getenv("RENDER_GIT_COMMIT")
        or os.getenv("GIT_COMMIT")
        or os.getenv("SOURCE_VERSION")
        or "local"
    )


def _json(start_response, payload, status="200 OK"):
    body = json.dumps(payload, indent=2).encode("utf-8")
    start_response(
        status,
        [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(body))),
            ("Cache-Control", "no-store"),
            ("Access-Control-Allow-Origin", "*"),
            ("X-Content-Type-Options", "nosniff"),
            ("Referrer-Policy", "strict-origin-when-cross-origin"),
        ],
    )
    return [body]


def _asset(start_response, target: Path):
    if not target.is_file():
        return _json(start_response, {"error": "not_found"}, "404 Not Found")
    body = target.read_bytes()
    content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
    if content_type == "text/html" and REVIEW_FLOW_SCRIPT not in body:
        body = body.replace(b"</head>", REVIEW_FLOW_SCRIPT + b"</head>", 1)
    start_response(
        "200 OK",
        [
            ("Content-Type", content_type),
            ("Content-Length", str(len(body))),
            ("Cache-Control", "public, max-age=300"),
            ("X-Content-Type-Options", "nosniff"),
            ("Referrer-Policy", "strict-origin-when-cross-origin"),
        ],
    )
    return [body]


def application(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET").upper()
    if method == "OPTIONS":
        return _json(start_response, {"status": "ok"})
    if path == "/api/health":
        return _json(
            start_response,
            {
                "status": "ok",
                "service": "ape-pfac-pssm5-toolkit",
                "project_identity": "MPH Applied Practice Experience",
                "release": _release_sha(),
            },
        )
    if path == "/api/backend-status":
        return _json(start_response, backend_status())
    if path == "/api/demo-intake":
        if method != "POST":
            return _json(start_response, {"error": "method_not_allowed"}, "405 Method Not Allowed")
        try:
            size = int(environ.get("CONTENT_LENGTH") or "0")
            body = environ["wsgi.input"].read(min(size, 4096)).decode("utf-8")
            payload = json.loads(body or "{}")
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
            return _json(start_response, {"error": "invalid_json"}, "400 Bad Request")
        result = submit_demo_intake(payload)
        status = "201 Created" if result.get("status") == "received" else "202 Accepted"
        if result.get("status") == "error" or result.get("error") == "validation_failed":
            status = "422 Unprocessable Entity"
        return _json(start_response, result, status)
    if path == "/api/open-resources":
        return _json(start_response, {"open_resources": build_demo_payload()["open_resources"]})
    if path == "/api/hai-dashboard":
        return _json(start_response, build_hai_dashboard())
    if path == "/api/toolkit":
        return _json(start_response, build_demo_payload())
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
