from __future__ import annotations

import unittest
from pathlib import Path

from pssm5_toolkit.server import application


BRAND_STYLESHEET = "/brand-refresh.css"


def request(path: str) -> tuple[str, dict[str, str], str]:
    captured: dict[str, object] = {}

    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = dict(headers)

    body = b"".join(
        application({"PATH_INFO": path, "REQUEST_METHOD": "GET"}, start_response)
    ).decode("utf-8")
    return str(captured["status"]), captured["headers"], body


class BrandRefreshContractTests(unittest.TestCase):
    def test_every_public_html_route_loads_brand_refresh_stylesheet_once(self):
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
                self.assertEqual(body.count(BRAND_STYLESHEET), 1)

    def test_brand_refresh_stylesheet_is_served_as_css(self):
        status, headers, body = request(BRAND_STYLESHEET)
        self.assertEqual(status, "200 OK")
        self.assertIn("text/css", headers["Content-Type"])
        self.assertIn("--ape-serif", body)
        self.assertIn("Cambria", body)


if __name__ == "__main__":
    unittest.main()
