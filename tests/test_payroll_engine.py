import unittest
from decimal import Decimal

from steuerpilot.payroll import (
    PayrollInput, TaxResult, UnsupportedPayrollCase, PayrollInputError,
    calculate_payroll,
)


class PayrollEngineFoundationTests(unittest.TestCase):
    def base_input(self, **changes):
        values = dict(
            gross_pay=Decimal("4000.00"),
            taxable_gross=Decimal("4000.00"),
            social_insurance_gross=Decimal("4000.00"),
            state="NW",
            children_under_25=0,
            age=30,
        )
        values.update(changes)
        return PayrollInput(**values)

    def tax(self):
        return TaxResult(
            wage_tax=Decimal("500.00"),
            solidarity_surcharge=Decimal("0.00"),
            church_tax=Decimal("0.00"),
            source_id="TEST-BMF-PAP-2026-FIXTURE",
        )

    def test_ordinary_employee_contributions_and_net_are_cent_rounded(self):
        result = calculate_payroll(self.base_input(), self.tax())
        self.assertEqual(result.employee_health, Decimal("350.00"))
        self.assertEqual(result.employer_health, Decimal("350.00"))
        self.assertEqual(result.employee_care, Decimal("96.00"))
        self.assertEqual(result.employer_care, Decimal("72.00"))
        self.assertEqual(result.employee_pension, Decimal("372.00"))
        self.assertEqual(result.employee_unemployment, Decimal("52.00"))
        self.assertEqual(result.employee_social_total, Decimal("870.00"))
        self.assertEqual(result.net_pay, Decimal("2630.00"))

    def test_saxony_care_split_and_childless_surcharge(self):
        result = calculate_payroll(
            self.base_input(state="SN"),
            self.tax(),
        )
        self.assertEqual(result.employee_care, Decimal("116.00"))
        self.assertEqual(result.employer_care, Decimal("52.00"))

    def test_child_reduction_applies_from_second_child(self):
        one = calculate_payroll(self.base_input(children_under_25=1), self.tax())
        two = calculate_payroll(self.base_input(children_under_25=2), self.tax())
        self.assertEqual(one.employee_care, Decimal("72.00"))
        self.assertEqual(two.employee_care, Decimal("62.00"))

    def test_contribution_caps_are_applied_separately(self):
        result = calculate_payroll(
            self.base_input(gross_pay=Decimal("10000"), taxable_gross=Decimal("10000"), social_insurance_gross=Decimal("10000")),
            self.tax(),
        )
        self.assertEqual(result.employee_health, Decimal("508.59"))
        self.assertEqual(result.employee_pension, Decimal("785.85"))

    def test_midijob_and_private_insurance_are_rejected_not_guessed(self):
        with self.assertRaises(UnsupportedPayrollCase):
            calculate_payroll(self.base_input(employment_type="midijob"), self.tax())
        with self.assertRaises(UnsupportedPayrollCase):
            calculate_payroll(self.base_input(health_insurance_type="pkv"), self.tax())

    def test_partial_month_and_multiple_employers_are_rejected(self):
        with self.assertRaises(UnsupportedPayrollCase):
            calculate_payroll(self.base_input(full_month=False), self.tax())
        with self.assertRaises(UnsupportedPayrollCase):
            calculate_payroll(self.base_input(one_employer=False), self.tax())

    def test_missing_traceable_tax_result_is_rejected(self):
        tax = TaxResult(Decimal("0"), Decimal("0"), source_id="")
        with self.assertRaises(PayrollInputError):
            calculate_payroll(self.base_input(), tax)

    def test_invalid_state_is_rejected(self):
        with self.assertRaises(PayrollInputError):
            calculate_payroll(self.base_input(state="XX"), self.tax())


    def test_childless_surcharge_does_not_apply_before_age_23(self):
        result = calculate_payroll(self.base_input(age=22), self.tax())
        self.assertEqual(result.employee_care, Decimal("72.00"))

    def test_non_member_cannot_be_charged_church_tax(self):
        tax = TaxResult(
            wage_tax=Decimal("500.00"),
            solidarity_surcharge=Decimal("0.00"),
            church_tax=Decimal("36.00"),
            source_id="TEST-BMF-PAP-2026-FIXTURE",
        )
        with self.assertRaises(PayrollInputError):
            calculate_payroll(self.base_input(), tax)

    def test_member_requires_tax_adapter_church_tax_amount(self):
        tax = TaxResult(
            wage_tax=Decimal("500.00"),
            solidarity_surcharge=Decimal("0.00"),
            church_tax=Decimal("0.00"),
            source_id="TEST-BMF-PAP-2026-FIXTURE",
        )
        with self.assertRaises(PayrollInputError):
            calculate_payroll(self.base_input(church_tax_member=True), tax)

    def test_negative_deductions_are_rejected(self):
        with self.assertRaises(PayrollInputError):
            calculate_payroll(self.base_input(other_deductions=Decimal("-1")), self.tax())


if __name__ == "__main__":
    unittest.main()
