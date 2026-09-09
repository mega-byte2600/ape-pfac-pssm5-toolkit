from __future__ import annotations

import unittest
from pathlib import Path


class QAPlaybookContractTests(unittest.TestCase):
    def test_best_fit_qa_playbook_covers_demo_risks(self):
        body = Path("docs/QA_REGRESSION_PLAYBOOK.md").read_text(encoding="utf-8")
        required = [
            "best-fit QA ladder",
            "Architecture Guardrails",
            "Pull Request Gate",
            "White-Box Regression",
            "Black-Box Smoke",
            "Browser And Mobile Smoke",
            "Production Smoke",
            "extended_public_smoke.py",
            "browser_smoke.py",
            "production_smoke.py",
            "prompt spillover prevention",
            "Supabase integration stays behind the backend interface",
            "Navigation improvements should add orientation without flattening contextual page navigation.",
            "internal administration language",
            "Dartmouth Health benchmark language remains a framework",
            "CSV-backed calculations reconcile",
            "Plotly containers remain present",
            "Do not merge a demo-facing change when extended public smoke fails.",
        ]
        folded = body.casefold()
        for fragment in required:
            self.assertIn(fragment.casefold(), folded)


if __name__ == "__main__":
    unittest.main()
