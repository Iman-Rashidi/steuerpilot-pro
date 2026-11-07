"""Smoke tests for the staging demo learning and payroll routes."""
import unittest
from io import BytesIO

from demo_app import application


class DemoRouteTests(unittest.TestCase):
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

    def test_home_links_to_academy_and_payroll(self):
        response, body = self.request("/")
        self.assertEqual(response["status"], "200 OK")
        self.assertIn('href="/academy"', body)
        self.assertIn('href="/payroll"', body)
        self.assertNotIn("STAGING · TEST ONLY", body)

    def test_academy_route_renders_training_content_without_badges(self):
        response, body = self.request("/academy")
        self.assertEqual(response["status"], "200 OK")
        self.assertIn("آکادمی مدیرعامل", body)
        self.assertIn("Buchhaltung Grundlagen", body)
        self.assertIn("Mitarbeiter-Onboarding", body)
        self.assertIn("Steuern und Finanzamt", body)
        self.assertNotIn("STAGING · TRAINING ONLY", body)

    def test_academy_route_discloses_synthetic_only_boundary(self):
        _, body = self.request("/academy/")
        self.assertIn("فقط برای یادگیری و آزمایش با اطلاعات ساختگی است", body)
        self.assertIn("هیچ اطلاعاتی ذخیره یا برای مرجع دولتی ارسال نمی‌شود", body)

    def test_academy_does_not_claim_official_submission(self):
        _, body = self.request("/academy")
        self.assertIn("ارسال رسمی در این صفحه انجام نمی‌شود", body)
        self.assertIn("Keine produktive Steuerberatung", body)

    def test_payroll_page_has_input_logo_and_pdf_export(self):
        response, body = self.request("/payroll")
        self.assertEqual(response["status"], "200 OK")
        self.assertIn('id="logo_file"', body)
        self.assertIn('id="company"', body)
        self.assertIn('id="employee"', body)
        self.assertIn('id="p_net"', body)
        self.assertIn("window.print()", body)
        self.assertIn("Auszahlungsbetrag", body)
        self.assertIn("Arbeitgeberanteile", body)

    def test_payroll_page_has_automatic_social_insurance_and_shift_inputs(self):
        response, body = self.request("/payroll")
        self.assertEqual(response["status"], "200 OK")
        for field in ("monthly_gross", "weekly_hours", "gkv_additional", "night_rate",
                      "sunday_rate", "holiday_rate", "special_holiday_rate", "state",
                      "children_under25", "shifts", "krankenkasse"):
            self.assertIn('id="' + field + '"', body)
        for output in ("p_health", "p_care", "p_pension", "p_unemployment",
                       "p_employer_health", "p_employer_care", "p_night",
                       "p_sunday", "p_holiday", "p_net"):
            self.assertIn('id="' + output + '"', body)
        self.assertIn("calculatePayroll", body)
        self.assertIn("calculateShiftPremiums", body)

    def test_payroll_page_uses_2026_caps_and_state_holiday_calendar(self):
        _, body = self.request("/payroll")
        self.assertIn("gkvAssessmentCeilingMonthly: 5812.50", body)
        self.assertIn("pensionAssessmentCeilingMonthly: 8450", body)
        self.assertIn("function easterSunday", body)
        self.assertIn("function holidayName", body)
        self.assertIn("Fronleichnam", body)
        self.assertIn("Buß- und Bettag", body)
        self.assertIn("Math.min(hourly, 25)", body)
        self.assertIn("Math.min(hourly, 50)", body)

    def test_payroll_page_uses_browser_only_and_discloses_limitations(self):
        _, body = self.request("/payroll/")
        self.assertIn("اطلاعات فقط در مرورگر پردازش می‌شود", body)
        self.assertIn("Minijob، Midijob", body)
        self.assertIn("Lohnsteuer", body)
        self.assertIn("Keine vollständige gesetzliche Entgeltbescheinigung", body)
        self.assertNotIn('id="steuer_id"', body)
        self.assertNotIn('id="iban"', body)


if __name__ == "__main__":
    unittest.main()
