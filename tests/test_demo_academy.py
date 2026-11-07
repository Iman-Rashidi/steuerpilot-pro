"""Smoke tests for the staging demo academy route."""
import unittest
from io import BytesIO

from demo_app import application


class AcademyRouteTests(unittest.TestCase):
    def request(self, path: str):
        captured = {}

        def start_response(status, headers):
            captured["status"] = status
            captured["headers"] = dict(headers)

        environ = {
            "REQUEST_METHOD": "GET",
            "PATH_INFO": path,
            "CONTENT_LENGTH": "0",
            "wsgi.input": BytesIO(b""),
        }
        body = b"".join(application(environ, start_response)).decode("utf-8")
        return captured, body

    def test_home_links_to_academy(self):
        response, body = self.request("/")
        self.assertEqual(response["status"], "200 OK")
        self.assertIn('href="/academy"', body)

    def test_academy_route_renders_training_content(self):
        response, body = self.request("/academy")
        self.assertEqual(response["status"], "200 OK")
        self.assertIn("آکادمی مدیرعامل", body)
        self.assertIn("Buchhaltung Grundlagen", body)
        self.assertIn("Mitarbeiter-Onboarding", body)
        self.assertIn("Steuern und Finanzamt", body)

    def test_academy_route_discloses_synthetic_only_boundary(self):
        _, body = self.request("/academy/")
        self.assertIn("فقط برای یادگیری و آزمایش با اطلاعات ساختگی است", body)
        self.assertIn("هیچ اطلاعاتی ذخیره یا برای مرجع دولتی ارسال نمی‌شود", body)

    def test_academy_does_not_claim_official_submission(self):
        _, body = self.request("/academy")
        self.assertIn("ارسال رسمی در این صفحه انجام نمی‌شود", body)
        self.assertIn("Keine produktive Steuerberatung", body)


if __name__ == "__main__":
    unittest.main()
