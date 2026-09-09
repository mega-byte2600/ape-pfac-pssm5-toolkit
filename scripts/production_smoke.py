#!/usr/bin/env python3
"""Run lightweight smoke tests against the deployed public APE site."""

from __future__ import annotations

import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_BASE_URL = "https://ape-pfac-pssm5-toolkit.onrender.com"

HTML_CHECKS = {
    "/": ["Turn patient voice into accountable action.", "APE deliverables"],
    "/story.html": ["Rosie Bartel", "lived experience"],
    "/about.html": ["Michael Bolton", "Project Lead"],
    "/hai-alert.html": ["hai-trend-chart", "hai-baseline-chart", "plotly-2.35.2.min.js"],
    "/applied-analysis.html": ["analysis-chart", "Original local analysis", "72,736"],
    "/evidence-summary.html": ["CMS Patient Safety Structural Measure", "Domain 5: Patient and Family Engagement"],
    "/evidence-matrix.html": ["Evidence Matrix"],
    "/bibliography.html": ["Bibliography"],
    "/dh-benchmark.html": ["Benchmark assessment framework"],
    "/toolkit-tools.html": ["Leadership Tools", "Leadership workspace", "leadership-tool-select", "Inspect full working table"],
    "/deliverables.html": ["APE deliverables"],
}

ASSET_CHECKS = {
    "/app.js": ["Plotly"],
    "/applied-analysis.js": ["Plotly.react"],
    "/leadership-tools.js": ["leadership-tool-select", "data-leadership-tool", "history.replaceState"],
    "/leadership-tools.css": [".tool-workspace", ".tool-summary-grid", ".audit-table-details"],
    "/upper-valley-local-analysis.csv": ["Municipality"],
}

FORBIDDEN_PUBLIC_COPY = ("Reviewer Guide", "/mvp-one.html", "review-flow.js", "Reviewer flow")
RETIRED_ROUTES = ("/mvp-one.html", "/review-flow.js")


def fetch(base_url: str, path: str) -> tuple[int, str, str]:
    request = Request(base_url.rstrip("/") + path, headers={"User-Agent": "ape-production-smoke/1.0"})
    with urlopen(request, timeout=20) as response:
        content_type = response.headers.get("Content-Type", "")
        body = response.read().decode("utf-8", errors="replace")
        return response.status, content_type, body


def fetch_status(base_url: str, path: str) -> tuple[int, str, str]:
    try:
        return fetch(base_url, path)
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return exc.code, exc.headers.get("Content-Type", ""), body


def fail(message: str) -> None:
    print(f"FAIL: {message}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--expected-sha", default=None)
    args = parser.parse_args()

    failures = 0

    for path, sentinels in HTML_CHECKS.items():
        try:
            status, content_type, body = fetch(args.base_url, path)
        except (HTTPError, URLError, TimeoutError) as exc:
            fail(f"{path} request error: {exc}")
            failures += 1
            continue
        if status != 200:
            fail(f"{path} returned {status}")
            failures += 1
        if "text/html" not in content_type:
            fail(f"{path} content type was {content_type!r}")
            failures += 1
        for sentinel in sentinels:
            if sentinel.casefold() not in body.casefold():
                fail(f"{path} missing sentinel {sentinel!r}")
                failures += 1
        for forbidden in FORBIDDEN_PUBLIC_COPY:
            if forbidden.casefold() in body.casefold():
                fail(f"{path} reintroduces retired reviewer-guide content {forbidden!r}")
                failures += 1

    for path, sentinels in ASSET_CHECKS.items():
        try:
            status, _, body = fetch(args.base_url, path)
        except (HTTPError, URLError, TimeoutError) as exc:
            fail(f"{path} request error: {exc}")
            failures += 1
            continue
        if status != 200:
            fail(f"{path} returned {status}")
            failures += 1
        for sentinel in sentinels:
            if sentinel.casefold() not in body.casefold():
                fail(f"{path} missing sentinel {sentinel!r}")
                failures += 1

    for path in RETIRED_ROUTES:
        try:
            status, _, _ = fetch_status(args.base_url, path)
        except (URLError, TimeoutError) as exc:
            fail(f"{path} request error: {exc}")
            failures += 1
            continue
        if status != 404:
            fail(f"retired route {path} returned {status}, expected 404")
            failures += 1

    try:
        status, content_type, body = fetch(args.base_url, "/api/health")
        health = json.loads(body)
        if status != 200 or "application/json" not in content_type:
            fail("/api/health did not return JSON 200")
            failures += 1
        if health.get("status") != "ok":
            fail("/api/health status is not ok")
            failures += 1
        if args.expected_sha:
            release = str(health.get("release", ""))
            if not release.startswith(args.expected_sha):
                fail(f"deployed release {release!r} does not match expected {args.expected_sha!r}")
                failures += 1
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        fail(f"/api/health request error: {exc}")
        failures += 1

    if failures:
        print(f"Production smoke FAILED with {failures} issue(s).")
        return 1

    print("Production smoke PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
