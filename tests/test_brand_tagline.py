from __future__ import annotations

import unittest
from pathlib import Path

from pssm5_toolkit.server import application


NEW_TAGLINE = "Patients. Leaders. Experience."
OLD_TAGLINE = "Evidence. Local analysis. Decisions. Accountability."


def request(path: str) -> tuple[str, dict[str, str], str]:
    captured: dict[str, object] = {}

    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = dict(headers)

    body = b"".join(
        application({"PATH_INFO": path, "REQUEST_METHOD": "GET"}, start_response)
    ).decode("utf-8")
    return str(captured["status"]), captured["headers"], body


class BrandTaglineContractTests(unittest.TestCase):
    def test_every_public_html_route_uses_approved_tagline(self):
        web_dir = Path("web")
        routes = ["/"]
        routes.extend(
            f"/{item.name}"
            for item in sorted(web_dir.glob("*.html"))
            if item.name != "index.html"
        )

        for route in routes:
            with self.subTest(route=route):
                status, headers, body = request(route)
                self.assertEqual(status, "200 OK")
                self.assertIn("text/html", headers["Content-Type"])
                self.assertIn(NEW_TAGLINE, body)
                self.assertNotIn(OLD_TAGLINE, body)


if __name__ == "__main__":
    unittest.main()
