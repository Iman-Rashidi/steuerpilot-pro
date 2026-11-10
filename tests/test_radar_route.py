import unittest
from io import BytesIO

from demo_app import application


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
    def test_radar_route_embeds_passwordless_staging_app_without_sso(self):
        status, headers, body = request("/reinigungsradar")

        self.assertEqual(status, "200 OK")
        self.assertIn("text/html", headers.get("Content-Type", ""))
        self.assertIn("<iframe", body)
        self.assertIn('src="https://reinigungsai-pr7-staging.onrender.com/"', body)
        self.assertNotIn("sso=", body)
        self.assertNotIn("embed=true", body)
        self.assertNotIn("type=\"password\"", body)
        self.assertNotIn("/radar-login", body)

    def test_radar_route_does_not_depend_on_sso_environment_variables(self):
        status, _, body = request("/reinigungsradar")
        self.assertEqual(status, "200 OK")
        self.assertIn("ReinigungsRadar NRW", body)
        self.assertNotIn("ورود یکپارچه هنوز آماده نیست", body)

    def test_legacy_password_route_is_removed(self):
        status, _, _ = request("/radar-login")
        self.assertEqual(status, "404 Not Found")


if __name__ == "__main__":
    unittest.main()
