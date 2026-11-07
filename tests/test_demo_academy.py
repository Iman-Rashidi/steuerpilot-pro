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
        self.assertIn("<span>Auszahlungsbetrag</span>", body)
        self.assertIn('<html lang="de" dir="ltr">', body)
        self.assertNotIn('lang="fa"', body)
        self.assertNotIn("dir=\"rtl\"", body)
        self.assertNotRegex(body, r"[\u0600-\u06FF]")
        preview = body.split('<section class="preview" id="payroll_preview"', 1)[1].split("</section>", 1)[0]
        self.assertNotRegex(body, r"[\u0600-\u06FF]")
        self.assertIn("Firmenname", preview)
        self.assertIn("Unternehmensanschrift", preview)
        self.assertNotRegex(body, r"[\u0600-\u06FF]")
        self.assertIn("Arbeitgeberanteile", body)
        self.assertIn('id="print_button"', body)
        self.assertIn('id="pdf_button"', body)
        self.assertIn("doc.save(", body)
        self.assertIn("ENTGELTABRECHNUNG", body)
        self.assertIn("@page{size:A4;margin:9mm}", body)
        self.assertIn("output-actions{display:grid;grid-template-columns:1fr;gap:9px", body)
        self.assertIn("window.print()", body)

    def test_payroll_page_has_automatic_social_insurance_and_shift_inputs(self):
        response, body = self.request("/payroll")
        self.assertEqual(response["status"], "200 OK")
        for field in ("monthly_hours", "kv_extra", "night_rate", "sunday_rate",
                      "holiday_rate", "shift_rows", "state", "children"):
            self.assertIn('id="' + field + '"', body)
        for output in ("p_health", "p_care", "p_pension", "p_unemployment",
                       "p_employer_health", "p_employer_care", "p_night_pay",
                       "p_sunday_pay", "p_holiday_pay", "p_net"):
            self.assertIn('id="' + output + '"', body)

    def test_payroll_page_uses_2026_caps_and_state_holiday_calendar(self):
        _, body = self.request("/payroll")
        self.assertIn("581250", body)
        self.assertIn("845000", body)
        self.assertIn("function holidaysFor", body)
        self.assertIn("Bundesland auswählen", body)
        self.assertIn("Bitte wählen Sie das Bundesland", body)
        self.assertIn("function easterSunday", body)
        self.assertIn("mins>=1200||mins<360", body)
        self.assertIn("afterMidnightCarry=startedBeforeMidnight&&mins<240", body)
        self.assertIn("startedBeforeMidnight=finish>Date.UTC(y,m-1,d,24,0)", body)
        self.assertIn("holidays.has(previousIso)", body)
        self.assertIn("previousDay===0", body)
        self.assertIn("plusDays(easter,0)", body)
        self.assertIn("plusDays(easter,49)", body)
        self.assertIn("Math.floor(start/60),start%60", body)
        self.assertIn("0.093", body)
        self.assertIn("0.013", body)

    def test_payroll_page_has_datev_inspired_payroll_fields_and_summaries(self):
        _, body = self.request("/payroll")
        required_fields = (
            "employee_address", "birth_date", "steuer_id_test", "sv_number_test",
            "tax_class", "tax_factor", "child_allowance", "religion",
            "annual_allowance", "monthly_allowance", "dba_country", "midijob",
            "pgrs", "bgrs", "sv_days", "uv_code_test", "uv_days",
            "scheduled_hours", "actual_hours", "attendance_days",
            "vacation_entitlement", "vacation_carryover", "vacation_taken",
            "sick_days", "absence_days", "holiday_days",
            "earnings_rows", "net_benefit_rows", "net_deduction_rows",
            "kug_payout", "vwl_deduction", "garnishment", "loan_repayment",
            "rest_garnishment", "rest_loan", "payment_method", "bank_name_test",
            "ytd_gross", "ytd_tax_gross", "ytd_kv_gross", "ytd_rv_gross",
            "ytd_av_gross", "ytd_pv_gross", "ytd_tax", "ytd_church",
            "ytd_soli", "ytd_kv", "ytd_rv", "ytd_av", "ytd_pv", "ytd_vwl",
            "u1_cost", "u2_cost", "insolvency_cost", "accident_cost",
        )
        for field in required_fields:
            self.assertIn('id="' + field + '"', body, field)

        for label in (
            "Abrechnung der Brutto/Netto-Bezüge", "Geburtsdatum", "Steuerklasse",
            "Faktor (Steuerklasse IV)", "Kinderfreibetrag", "Konfession",
            "Freibetrag jährlich", "Freibetrag monatlich", "DBA-Staat",
            "Midijob", "Krankenkasse", "Personengruppenschlüssel (PGRS)",
            "Beitragsgruppenschlüssel (BGRS)", "Anwesenheitstage",
            "Urlaubsanspruch", "Krankheitstage", "Feiertage",
            "Lohnart", "Einheit", "Menge", "Faktor (EUR)", "Prozentsatz",
            "Netto-Bezüge", "Netto-Abzüge", "Verdienstbescheinigung",
            "Pfändung", "Darlehensrückzahlung", "Auszahlungsweg",
            "Gesamtkosten Arbeitgeber", "Auszahlungsbetrag",
        ):
            self.assertIn(label, body)

        self.assertIn('["taxable","sv","gb"]', body)
        self.assertIn("input.dataset.wage=field", body)
        self.assertIn("function addWageRow", body)
        self.assertIn("function readWageRows", body)
        self.assertIn("taxGross", body)
        self.assertIn("doc.addPage()", body)
        self.assertIn("Keine echten Steuer- oder Sozialversicherungsnummern", body)
        self.assertNotRegex(body, r"[\\u0600-\\u06FF]")

    def test_payroll_page_uses_browser_only_and_discloses_limitations(self):
        _, body = self.request("/payroll/")
        self.assertIn("Angaben und Logo werden nicht an den Server übertragen", body)
        self.assertIn("Dieses Formular wird ausschließlich im Browser ausgeführt", body)
        self.assertIn("Lohnsteuer wird nicht berechnet", body)
        self.assertNotIn('id="steuer_id"', body)
        self.assertNotIn('id="iban"', body)


if __name__ == "__main__":
    unittest.main()
