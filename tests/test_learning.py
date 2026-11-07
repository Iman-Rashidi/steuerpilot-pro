"""Tests for the synthetic-only learning assistant prototype."""
import unittest

from steuerpilot.learning import (
    CaseStatus,
    GuidedCase,
    LearningWorkflowError,
    UnsafeDataModeError,
    get_lesson,
    list_lessons,
)


class LearningCatalogueTests(unittest.TestCase):
    def test_catalogue_contains_accounting_hr_tax_and_management(self):
        modules = {lesson.module for lesson in list_lessons()}
        self.assertTrue({"Buchhaltung", "Personal", "Steuern", "Geschäftsführung"} <= modules)

    def test_lesson_is_bilingual_and_has_required_fields(self):
        lesson = get_lesson("accounting.basics")
        self.assertTrue(lesson.title_fa)
        self.assertTrue(lesson.title_de)
        self.assertGreater(len(lesson.required_fields), 0)

    def test_module_filter_returns_only_matching_lessons(self):
        lessons = list_lessons("Personal")
        self.assertTrue(lessons)
        self.assertTrue(all(lesson.module == "Personal" for lesson in lessons))


class GuidedCaseTests(unittest.TestCase):
    def test_real_data_mode_is_rejected(self):
        with self.assertRaises(UnsafeDataModeError):
            GuidedCase("demo-1", "accounting.basics", synthetic_data=False)

    def test_unknown_lesson_is_rejected(self):
        with self.assertRaises(LearningWorkflowError):
            GuidedCase("demo-1", "unknown.lesson")

    def test_incomplete_case_cannot_advance(self):
        case = GuidedCase("demo-2", "accounting.basics")
        with self.assertRaisesRegex(LearningWorkflowError, "missing"):
            case.complete_information()
        self.assertEqual(case.status, CaseStatus.DRAFT)

    def test_basic_lesson_can_be_completed(self):
        case = GuidedCase("demo-3", "accounting.basics")
        for field_name in case.lesson.required_fields:
            case.answer(field_name, "SYNTHETIC-EXAMPLE")
        self.assertEqual(case.complete_information(), CaseStatus.INFORMATION_COMPLETE)
        self.assertEqual(case.complete_training(), CaseStatus.TRAINING_COMPLETED)

    def test_specialist_topic_is_never_auto_approved(self):
        case = GuidedCase("demo-4", "hr.offboarding")
        for field_name in case.lesson.required_fields:
            case.answer(field_name, "SYNTHETIC-EXAMPLE")
        self.assertEqual(
            case.complete_information(), CaseStatus.SPECIALIST_REVIEW_REQUIRED
        )
        with self.assertRaisesRegex(LearningWorkflowError, "qualified review"):
            case.complete_training()
        self.assertEqual(case.status, CaseStatus.SPECIALIST_REVIEW_REQUIRED)

    def test_answers_are_limited_to_declared_fields(self):
        case = GuidedCase("demo-5", "accounting.basics")
        with self.assertRaisesRegex(LearningWorkflowError, "not part of this lesson"):
            case.answer("iban", "SYNTHETIC-IBAN")

    def test_answers_cannot_be_changed_after_information_complete(self):
        case = GuidedCase("demo-6", "accounting.basics")
        for field_name in case.lesson.required_fields:
            case.answer(field_name, "SYNTHETIC-EXAMPLE")
        case.complete_information()
        with self.assertRaisesRegex(LearningWorkflowError, "draft"):
            case.answer("amount_eur", "200.00")


if __name__ == "__main__":
    unittest.main()
