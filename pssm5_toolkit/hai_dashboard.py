"""HAI dashboard data for executive PFAC review.

The records are shaped with pandas when available so the site can grow into a
real analytics workflow. A small fallback keeps the demo runnable without extra
packages.
"""

from __future__ import annotations

from typing import Any, Dict, List


HAI_PROGRESS_ROWS: List[Dict[str, Any]] = [
    {"measure": "CLABSI", "setting": "Acute care hospitals", "change_vs_2023": -9, "change_vs_2015": -34, "pfac_question": "Are central-line risks explained in language patients and families can repeat back?"},
    {"measure": "CAUTI", "setting": "Acute care hospitals", "change_vs_2023": -10, "change_vs_2015": -44, "pfac_question": "Do patients know why a catheter is needed and when it should come out?"},
    {"measure": "VAE", "setting": "Acute care hospitals", "change_vs_2023": -2, "change_vs_2015": 11, "pfac_question": "Can families recognize respiratory decline and reach the team quickly?"},
    {"measure": "SSI colon", "setting": "Acute care hospitals", "change_vs_2023": -4, "change_vs_2015": -16, "pfac_question": "Are wound-care instructions specific enough for home recovery?"},
    {"measure": "SSI hysterectomy", "setting": "Acute care hospitals", "change_vs_2023": 8, "change_vs_2015": 11, "pfac_question": "Which surgical patients need clearer infection warning signs and escalation paths?"},
    {"measure": "MRSA bacteremia", "setting": "Acute care hospitals", "change_vs_2023": -7, "change_vs_2015": -30, "pfac_question": "Would a patient with a new infection concern be believed and escalated?"},
    {"measure": "C. difficile", "setting": "Acute care hospitals", "change_vs_2023": -11, "change_vs_2015": -63, "pfac_question": "Do discharge instructions explain diarrhea warning signs and when to call?"},
]

EXECUTIVE_ACTIONS = [
    {"lane": "Safety signal", "owner": "Chief Quality Officer", "decision": "Review local SIR and event counts for the two measures moving the wrong way nationally: SSI hysterectomy and VAE versus 2015 baseline."},
    {"lane": "Patient voice", "owner": "PFAC sponsor", "decision": "Ask patients and families to rewrite discharge warning signs for infection, fever, wound changes, diarrhea, and respiratory decline."},
    {"lane": "Equity check", "owner": "Patient experience lead", "decision": "Stratify follow-up calls, readmissions, and complaints by language, age, disability, geography, and care setting."},
    {"lane": "Closed loop", "owner": "Service-line executive", "decision": "Publish one you-said/we-did item showing how PFAC feedback changed infection-prevention practice."},
]


def _records_with_pandas(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    import pandas as pd

    frame = pd.DataFrame(rows)
    frame["direction"] = frame["change_vs_2023"].map(lambda value: "worse" if value > 0 else "better")
    frame["alert_weight"] = frame["change_vs_2023"].abs() + frame["change_vs_2015"].clip(lower=0)
    frame = frame.sort_values(["direction", "alert_weight", "measure"], ascending=[False, False, True])
    return frame.to_dict(orient="records")


def build_hai_dashboard() -> Dict[str, Any]:
    try:
        measures = _records_with_pandas(HAI_PROGRESS_ROWS)
        engine = "pandas"
    except Exception:
        measures = [
            {
                **row,
                "direction": "worse" if row["change_vs_2023"] > 0 else "better",
                "alert_weight": abs(row["change_vs_2023"]) + max(row["change_vs_2015"], 0),
            }
            for row in HAI_PROGRESS_ROWS
        ]
        measures.sort(key=lambda row: (row["direction"] != "worse", -row["alert_weight"], row["measure"]))
        engine = "standard-library-fallback"

    return {
        "status": "ok",
        "engine": engine,
        "source": "CDC 2024 National and State Healthcare-Associated Infections Progress Report",
        "source_url": "https://www.cdc.gov/healthcare-associated-infections/php/data/progress-report.html",
        "headline": "Most acute-care HAI SIRs improved in 2024 versus 2023, while abdominal hysterectomy SSI increased.",
        "measures": measures,
        "executive_actions": EXECUTIVE_ACTIONS,
        "chart_notes": [
            "Negative values indicate improvement versus the comparison period.",
            "Positive values indicate worsening and should trigger local data review.",
            "Use national data to frame the PFAC conversation, then request local SIR, event counts, complaints, and follow-up signals.",
        ],
    }
