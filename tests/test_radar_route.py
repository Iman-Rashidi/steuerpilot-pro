import os
import unittest
from io import BytesIO
from unittest.mock import patch

from demo_app import application


SECRET = "test-only-secret-material-with-at-least-32-characters"


def request(path, method="GET"):
    captured = {}

    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = dict(headers)

    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "QUERY_STRING": "",
        "CONTENT_LENGTH": "0",
        "wsgi.input": BytesIO(b""),
        "HTTP_COOKIE": "",
    }
    body = b"".join(application(environ, start_response)).decode("utf-8")
    return captured["status"], captured["headers"], body


class RadarRouteTests(unittest.TestCase):
    def test_radar_route_embeds_without_a_separate_trial_password(self):
        with patch.dict(os.environ, {"STEUERPILOT_RADAR_SSO_SECRET": SECRET}, clear=True):
            status, headers, body = request("/reinigungsradar")

        self.assertEqual(status, "200 OK")
        self.assertIn("text/html", headers.get("Content-Type", ""))
        self.assertIn("<iframe", body)
        self.assertIn("embed=true", body)
        self.assertIn("sso=", body)
        self.assertIn("نیازی به رمز عبور آزمایشی جداگانه نیست", body)
        self.assertNotIn("type=\"password\"", body)
        self.assertNotIn("/radar-login", body)

    def test_existing_misspelled_render_secret_remains_compatible(self):
        with patch.dict(os.environ, {"STEUEERPILOT_RADAR_SSO_SECRET": SECRET}, clear=True):
            status, _, body = request("/reinigungsradar")

        self.assertEqual(status, "200 OK")
        self.assertIn("<iframe", body)

    def test_missing_secret_returns_a_controlled_configuration_error(self):
        with patch.dict(os.environ, {}, clear=True):
            status, _, body = request("/reinigungsradar")

        self.assertEqual(status, "503 Service Unavailable")
        self.assertIn("ورود یکپارچه هنوز آماده نیست", body)

    def test_legacy_password_route_is_removed(self):
        with patch.dict(os.environ, {"STEUERPILOT_RADAR_SSO_SECRET": SECRET}, clear=True):
            status, _, _ = request("/radar-login")

        self.assertEqual(status, "404 Not Found")


if __name__ == "__main__":
    unittest.main()
