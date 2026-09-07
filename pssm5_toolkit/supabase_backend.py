"""Supabase-backed demo data access for the PFAC/PSSM 5 toolkit."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from .open_resources import build_open_resources
from .toolkit import build_toolkit

PROJECT_REF = "vgquagonefygzgebgzyx"
FUNCTION_BASE_URL = f"https://{PROJECT_REF}.supabase.co/functions/v1"
TOOLKIT_DATA_URL = os.getenv("SUPABASE_TOOLKIT_DATA_URL", f"{FUNCTION_BASE_URL}/toolkit-data")
DEMO_INTAKE_URL = os.getenv("SUPABASE_DEMO_INTAKE_URL", f"{FUNCTION_BASE_URL}/demo-intake")
TIMEOUT_SECONDS = float(os.getenv("SUPABASE_TIMEOUT_SECONDS", "8"))


def _fetch_json(url: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    method = "GET" if payload is None else "POST"
    request = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={"content-type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def build_demo_payload() -> dict[str, Any]:
    payload = build_toolkit()
    payload["open_resources"] = build_open_resources()
    try:
        live = _fetch_json(TOOLKIT_DATA_URL)
    except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError) as error:
        payload["backend_status"] = {
            "source": "bundled-fallback",
            "supabase_online": False,
            "detail": str(error),
        }
        return payload

    for key in ("competencies", "metric_drivers", "playbook_steps", "evidence", "open_resources"):
        if live.get(key):
            payload[key] = live[key]
    payload["backend_status"] = {
        "source": live.get("backend", "supabase"),
        "supabase_online": live.get("status") == "ok",
        "project": live.get("project", "ape-pfac-pssm5-toolkit"),
        "counts": live.get("counts", {}),
        "generated_at": live.get("generated_at"),
    }
    return payload


def backend_status() -> dict[str, Any]:
    payload = build_demo_payload()
    status = payload.get("backend_status", {})
    return {
        "status": "ok" if status.get("supabase_online") else "fallback",
        "service": "ape-pfac-pssm5-toolkit",
        "backend": status,
        "demo_ready": True,
        "privacy_note": "Demo intake must not include PHI or private patient identifiers.",
    }


def submit_demo_intake(payload: dict[str, Any]) -> dict[str, Any]:
    allowed = {"role", "organization", "priority", "message"}
    cleaned = {key: str(payload.get(key, "")).strip() for key in allowed}
    try:
        return _fetch_json(DEMO_INTAKE_URL, cleaned)
    except urllib.error.HTTPError as error:
        try:
            detail = json.loads(error.read().decode("utf-8"))
        except (OSError, json.JSONDecodeError):
            detail = {"error": "intake_unavailable"}
        detail.setdefault("status", "error")
        return detail
    except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError) as error:
        return {
            "status": "queued-locally",
            "error": "supabase_intake_unavailable",
            "detail": str(error),
            "privacy_note": "Demo fallback. Do not submit PHI or private patient identifiers.",
        }
