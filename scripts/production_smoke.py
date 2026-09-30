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
    "/": ["Evidence-Based Approach to Improve Outcomes for Patient-Care Experience", "APE deliverables"],
    "/story.html": ["Rosie Bartel", "lived experience"],
    "/about.html": ["Michael Bolton", "Project Lead"],
    "/hai-alert.html": ["hai-trend-chart", "hai-baseline-chart", "plotly-2.35.2.min.js"],
    "/applied-analysis.html": ["analysis-chart", "Original local analysis", "72,736"],
    "/evidence-summary.html": ["CMS Patient Safety Structural Measure", "Domain 5: Patient and Family Engagement"],
    "/evidence-matrix.html": ["Evidence Matrix"],
    "/bibliography.html": ["Bibliography"],
    "/dh-benchmark.html": ["Benchmark assessment framework"],
    "/toolkit-tools.html": ["Leadership Tools", "Leadership workspace", "leadership-tool-select", "Inspect full working table"],
    "/surveillance-method.html": [
        "Build a literature surveillance system you can actually run every week.",
        "APE_MASTER_PFAC_Inpatient_Experience_Safety",
        "APE_ALERTS_MASTER",
        "APE_HIGH_VALUE",
        "Bolton TDI APE 27",
        "Keep the architecture. Change the topic.",
    ],
    "/resources.html": ["cdc-state", "cdc-county-fips", "No ZIP code or FIPS lookup needed.", "cms-hcahps-explorer"],
    "/deliverables.html": ["APE deliverables"],
}

ASSET_CHECKS = {
    "/app.js": ["Plotly", "applyHomepageRationale", "serves as a bridge between leadership and PFACs"],
    "/applied-analysis.js": ["Plotly.react"],
    "/leadership-tools.js": ["leadership-tool-select", "data-leadership-tool", "history.replaceState"],
    "/leadership-tools.css": [".tool-workspace", ".tool-summary-grid", ".audit-table-details"],
    "/cdc-county-selector.js": ["/api/live/cdc/counties", "Choose state first"],
    "/hcahps-explorer.js": ["/api/live/hcahps-compare", "context signals, not evidence that PFAC activity caused a score"],
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


def check_json_route(base_url: str, path: str) -> tuple[dict, int]:
    try:
        status, content_type, body = fetch(base_url, path)
        payload = json.loads(body)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        fail(f"{path} request error: {exc}")
        return {}, 1
    failures = 0
    if status != 200 or "application/json" not in content_type:
        fail(f"{path} did not return JSON 200")
        failures += 1
    if payload.get("status") not in {"ok", "unavailable"}:
        fail(f"{path} returned unexpected status {payload.get('status')!r}")
        failures += 1
    return payload, failures


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

    counties, county_failures = check_json_route(args.base_url, "/api/live/cdc/counties?state=CA")
    failures += county_failures
    if counties.get("status") == "ok":
        county_map = {str(c.get("fips")): c.get("name") for c in counties.get("counties", [])}
        if county_map.get("06079") != "San Luis Obispo":
            fail("CDC county selector did not return San Luis Obispo County FIPS 06079")
            failures += 1
        else:
            print("CDC county selector live: CA -> San Luis Obispo (06079)")

    places, places_failures = check_json_route(args.base_url, "/api/live/cdc/places?location_id=06079&limit=200")
    failures += places_failures
    if places.get("status") == "ok":
        if not places.get("measures"):
            fail("CDC PLACES returned no measures for San Luis Obispo County")
            failures += 1
        else:
            print(f"CDC PLACES live: {len(places.get('measures', []))} county measure rows")

    svi, svi_failures = check_json_route(args.base_url, "/api/live/cdc/svi?fips=06079")
    failures += svi_failures
    if svi.get("status") == "ok":
        if svi.get("overall_percentile") is None:
            fail("CDC SVI returned no overall percentile for San Luis Obispo County")
            failures += 1
        else:
            print("CDC SVI live: San Luis Obispo County percentile returned")

    hcahps, hcahps_failures = check_json_route(args.base_url, "/api/live/hcahps-compare?facility_id=300003")
    failures += hcahps_failures
    if hcahps.get("status") == "ok":
        if str(hcahps.get("facility_id")) != "300003":
            fail("CMS HCAHPS comparison returned the wrong facility")
            failures += 1
        elif not hcahps.get("measures"):
            fail("CMS HCAHPS comparison returned no benchmark measures")
            failures += 1
        else:
            print(f"CMS HCAHPS live: {len(hcahps.get('measures', []))} benchmark measure rows")

    if failures:
        print(f"Production smoke FAILED with {failures} issue(s).")
        return 1

    print("Production smoke PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
