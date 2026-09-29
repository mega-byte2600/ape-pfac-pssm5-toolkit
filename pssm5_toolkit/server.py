"""Web server for the APE PFAC PSSM 5 toolkit."""

from __future__ import annotations

import json
import mimetypes
import os
import urllib.parse
from pathlib import Path
from wsgiref.simple_server import make_server

from .cdc_data import (
    cdc_data_status,
    fetch_cdc_candidemia,
    fetch_cdc_hai_isa,
    fetch_cdc_places_county,
    fetch_cdc_svi_county,
)
from .cdc_geography import fetch_cdc_counties
from .evidence_search import fetch_evidence_search
from .hai_dashboard import build_hai_dashboard
from .live_data import (
    fetch_census_demographics,
    fetch_census_upper_valley,
    fetch_evidence_watch,
    fetch_hcahps,
    fetch_trials,
    live_data_status,
    search_facilities,
)
from .supabase_backend import backend_status, build_demo_payload, submit_demo_intake

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
CWD_ROOT = Path.cwd()
WEB = CWD_ROOT / "web" if (CWD_ROOT / "web").is_dir() else PACKAGE_ROOT / "web"
RETIRED_PUBLIC_ROUTES = {"/mvp-one.html", "/review-flow.js"}


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


def _int_query(query, name: str, default: int) -> int:
    try:
        return int(query.get(name, [str(default)])[0] or str(default))
    except ValueError:
        return default


def application(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET").upper()
    if method == "OPTIONS":
        return _json(start_response, {"status": "ok"})
    if path in RETIRED_PUBLIC_ROUTES:
        return _json(start_response, {"error": "not_found"}, "404 Not Found")
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
    if path == "/api/live/status":
        status = live_data_status()
        status["sources"].extend(cdc_data_status()["sources"])
        return _json(start_response, status)
    if path == "/api/live/facility-search":
        query = urllib.parse.parse_qs(environ.get("QUERY_STRING", ""))
        return _json(
            start_response,
            search_facilities(
                name=query.get("name", [""])[0],
                state=query.get("state", [""])[0],
            ),
        )
    if path == "/api/live/hcahps":
        query = urllib.parse.parse_qs(environ.get("QUERY_STRING", ""))
        facility_id = query.get("facility_id", ["300003"])[0] or "300003"
        return _json(start_response, fetch_hcahps(facility_id))
    if path == "/api/live/evidence-watch":
        return _json(start_response, fetch_evidence_watch())
    if path == "/api/live/evidence-search":
        query = urllib.parse.parse_qs(environ.get("QUERY_STRING", ""))
        return _json(
            start_response,
            fetch_evidence_search(
                query.get("q", [""])[0], limit=_int_query(query, "limit", 10)
            ),
        )
    if path == "/api/live/trials":
        query = urllib.parse.parse_qs(environ.get("QUERY_STRING", ""))
        return _json(
            start_response,
            fetch_trials(
                facility_name=query.get("facility_name", [""])[0],
                state=query.get("state", [""])[0],
            ),
        )
    if path == "/api/live/census-demographics":
        query = urllib.parse.parse_qs(environ.get("QUERY_STRING", ""))
        return _json(
            start_response,
            fetch_census_demographics(
                state_fips=query.get("state_fips", [""])[0],
                county_fips=query.get("county_fips", [""])[0],
            ),
        )
    if path == "/api/live/census-upper-valley":
        return _json(start_response, fetch_census_upper_valley())
    if path == "/api/live/cdc/status":
        return _json(start_response, cdc_data_status())
    if path == "/api/live/cdc/counties":
        query = urllib.parse.parse_qs(environ.get("QUERY_STRING", ""))
        return _json(start_response, fetch_cdc_counties(query.get("state", [""])[0]))
    if path == "/api/live/cdc/hai-isa":
        query = urllib.parse.parse_qs(environ.get("QUERY_STRING", ""))
        return _json(
            start_response,
            fetch_cdc_hai_isa(
                topic=query.get("topic", [""])[0],
                view_by=query.get("view_by", [""])[0],
                series=query.get("series", [""])[0],
                limit=_int_query(query, "limit", 100),
            ),
        )
    if path == "/api/live/cdc/candidemia":
        query = urllib.parse.parse_qs(environ.get("QUERY_STRING", ""))
        return _json(
            start_response,
            fetch_cdc_candidemia(
                topic=query.get("topic", [""])[0],
                view_by=query.get("view_by", [""])[0],
                series=query.get("series", [""])[0],
                limit=_int_query(query, "limit", 100),
            ),
        )
    if path == "/api/live/cdc/places":
        query = urllib.parse.parse_qs(environ.get("QUERY_STRING", ""))
        return _json(
            start_response,
            fetch_cdc_places_county(
                location_id=query.get("location_id", [""])[0],
                limit=_int_query(query, "limit", 100),
            ),
        )
    if path == "/api/live/cdc/svi":
        query = urllib.parse.parse_qs(environ.get("QUERY_STRING", ""))
        return _json(
            start_response,
            fetch_cdc_svi_county(fips=query.get("fips", [""])[0]),
        )
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
