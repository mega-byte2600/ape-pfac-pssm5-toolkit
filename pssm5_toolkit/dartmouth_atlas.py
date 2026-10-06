"""Read-only Dartmouth Atlas public data adapter for the Resources explorer."""

from __future__ import annotations

import csv
import io
import re
import urllib.error
import urllib.request
import zipfile
from functools import lru_cache

DATASETS = {
    "primary-care": {
        "label": "Primary care access & quality",
        "download_url": "https://data.dartmouthatlas.org/downloads/research_files/hrr_hedis_6575ffs.csv.zip",
        "source_url": "https://data.dartmouthatlas.org/primary-care/",
        "years": "2008-2019",
        "keywords": ("primary", "ambul", "diab", "mamm", "amput", "prevent", "visit", "quality"),
    },
    "post-discharge": {
        "label": "Post-discharge events",
        "download_url": "https://data.dartmouthatlas.org/downloads/research_files/hrr_postdis_6599ffs.csv.zip",
        "source_url": "https://data.dartmouthatlas.org/post-discharge/",
        "years": "2009-2019",
        "keywords": ("readm", "emerg", "follow", "post", "disch"),
    },
}

SUPPRESSED = {
    "-77777": "Suppressed by source",
    "-88888": "Too small for statistical precision",
    "-99999": "Suppressed for privacy",
}

_AREA_CANDIDATES = (
    "hrrname", "hrr_name", "hrr name", "region_name", "region", "name", "hrr",
)
_YEAR_CANDIDATES = ("year", "yr")


def atlas_catalog():
    return {
        "status": "ok",
        "datasets": [
            {
                "id": key,
                "label": item["label"],
                "years": item["years"],
                "source_url": item["source_url"],
            }
            for key, item in DATASETS.items()
        ],
        "source": "Dartmouth Atlas Data",
        "terms_url": "https://data.dartmouthatlas.org/terms-of-use/",
    }


def _fetch_bytes(url: str, timeout: int = 15) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "APE-PFAC-PSSM5-Toolkit/1.0 (public-data adapter)"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


@lru_cache(maxsize=4)
def _load_dataset(dataset_id: str):
    meta = DATASETS.get(dataset_id)
    if not meta:
        raise ValueError("unknown_dataset")
    raw = _fetch_bytes(meta["download_url"])
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if not csv_names:
            raise ValueError("csv_missing")
        with archive.open(csv_names[0]) as handle:
            text = io.TextIOWrapper(handle, encoding="utf-8-sig", newline="")
            reader = csv.DictReader(text)
            rows = [dict(row) for row in reader]
            fields = list(reader.fieldnames or [])
    return fields, rows


def _field_lookup(fields):
    return {str(field).strip().lower(): field for field in fields}


def _pick_area_field(fields, rows):
    lookup = _field_lookup(fields)
    for candidate in _AREA_CANDIDATES:
        if candidate in lookup:
            return lookup[candidate]
    for field in fields:
        values = [str(row.get(field, "")).strip() for row in rows[:80] if str(row.get(field, "")).strip()]
        if values and any(re.search(r"[A-Za-z]", value) for value in values):
            return field
    return fields[0] if fields else ""


def _pick_year_field(fields):
    lookup = _field_lookup(fields)
    for candidate in _YEAR_CANDIDATES:
        if candidate in lookup:
            return lookup[candidate]
    for field in fields:
        if "year" in str(field).lower():
            return field
    return ""


def _numeric_fields(fields, rows, excluded):
    out = []
    for field in fields:
        if field in excluded:
            continue
        values = [str(row.get(field, "")).strip() for row in rows[:120]]
        samples = [v for v in values if v and v not in SUPPRESSED]
        if not samples:
            continue
        numeric = 0
        for value in samples:
            try:
                float(value.replace(",", ""))
                numeric += 1
            except ValueError:
                pass
        if numeric >= max(1, len(samples) // 2):
            out.append(field)
    return out


def _humanize(field: str) -> str:
    text = re.sub(r"[_\-]+", " ", str(field)).strip()
    text = re.sub(r"\s+", " ", text)
    return text[:1].upper() + text[1:] if text else field


def _measure_fields(dataset_id, fields, rows, area_field, year_field):
    excluded = {area_field, year_field}
    for field in fields:
        low = str(field).lower()
        if low in {"hrrnum", "hrr_num", "hrrid", "hrr_id", "id", "code"} or low.endswith("_id"):
            excluded.add(field)
    numeric = _numeric_fields(fields, rows, excluded)
    keywords = DATASETS[dataset_id]["keywords"]
    curated = [f for f in numeric if any(k in str(f).lower() for k in keywords)]
    selected = curated or numeric
    return selected[:24]


def atlas_options(dataset_id: str):
    try:
        fields, rows = _load_dataset(dataset_id)
        area_field = _pick_area_field(fields, rows)
        year_field = _pick_year_field(fields)
        measures = _measure_fields(dataset_id, fields, rows, area_field, year_field)
        areas = sorted(
            {str(row.get(area_field, "")).strip() for row in rows if str(row.get(area_field, "")).strip()},
            key=str.casefold,
        )
        return {
            "status": "ok",
            "dataset": dataset_id,
            "areas": areas,
            "measures": [{"id": field, "label": _humanize(field)} for field in measures],
            "source": "Dartmouth Atlas Data",
            "source_url": DATASETS[dataset_id]["source_url"],
        }
    except ValueError as exc:
        return {"status": "error", "reason_code": str(exc)}
    except (urllib.error.URLError, TimeoutError, zipfile.BadZipFile, OSError) as exc:
        return {
            "status": "unavailable",
            "reason_code": "atlas_source_unavailable",
            "detail": str(exc)[:180],
        }


def _year_key(value):
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return -1


def atlas_value(dataset_id: str, area: str, measure: str):
    if dataset_id not in DATASETS:
        return {"status": "error", "reason_code": "unknown_dataset"}
    try:
        fields, rows = _load_dataset(dataset_id)
        area_field = _pick_area_field(fields, rows)
        year_field = _pick_year_field(fields)
        allowed = {item["id"] for item in atlas_options(dataset_id).get("measures", [])}
        if measure not in fields or measure not in allowed:
            return {"status": "error", "reason_code": "unknown_measure"}
        matches = [
            row for row in rows
            if str(row.get(area_field, "")).strip().casefold() == str(area).strip().casefold()
        ]
        if not matches:
            return {"status": "not_found", "reason_code": "area_not_found"}
        if year_field:
            matches.sort(key=lambda row: _year_key(row.get(year_field)), reverse=True)
        row = matches[0]
        raw = str(row.get(measure, "")).strip()
        year = str(row.get(year_field, "")).strip() if year_field else ""
        payload = {
            "status": "ok",
            "dataset": dataset_id,
            "dataset_label": DATASETS[dataset_id]["label"],
            "area": str(row.get(area_field, "")).strip() or area,
            "measure": measure,
            "measure_label": _humanize(measure),
            "year": year,
            "source": "Dartmouth Atlas Data",
            "source_url": DATASETS[dataset_id]["source_url"],
            "terms_url": "https://data.dartmouthatlas.org/terms-of-use/",
        }
        if raw in SUPPRESSED:
            payload.update({"value": None, "suppressed": True, "note": SUPPRESSED[raw]})
            return payload
        try:
            value = float(raw.replace(",", ""))
            if value.is_integer():
                value = int(value)
            payload.update({"value": value, "suppressed": False})
        except ValueError:
            payload.update({"value": raw or None, "suppressed": False})
        return payload
    except (urllib.error.URLError, TimeoutError, zipfile.BadZipFile, OSError) as exc:
        return {
            "status": "unavailable",
            "reason_code": "atlas_source_unavailable",
            "detail": str(exc)[:180],
        }
