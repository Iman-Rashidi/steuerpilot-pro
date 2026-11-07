"""Bilingual learning catalogue and synthetic training workflow.

This module is an educational prototype only. It does not process real customer,
employee, payroll, banking, or tax data and it cannot submit official filings.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping


class LearningWorkflowError(ValueError):
    """Raised when a training workflow is used outside its permitted path."""


class UnsafeDataModeError(LearningWorkflowError):
    """Raised when a caller tries to use real data in the training prototype."""


class CaseStatus(str, Enum):
    DRAFT = "draft"
    INFORMATION_COMPLETE = "information_complete"
    SPECIALIST_REVIEW_REQUIRED = "specialist_review_required"
    TRAINING_COMPLETED = "training_completed"


@dataclass(frozen=True, slots=True)
class Lesson:
    """A short bilingual lesson with a safe, explicit workflow boundary."""

    lesson_id: str
    module: str
    title_fa: str
    title_de: str
    objective_fa: str
    steps_fa: tuple[str, ...]
    required_fields: tuple[str, ...]
    requires_specialist_review: bool = False


LESSONS: tuple[Lesson, ...] = (
    Lesson(
        lesson_id="accounting.basics",
        module="Buchhaltung",
        title_fa="مبانی حسابداری شرکت",
        title_de="Grundlagen der Buchhaltung",
        objective_fa="تفاوت درآمد، هزینه، دریافت وجه، بدهی، طلب، سود و نقدینگی را بشناسید.",
        steps_fa=(
            "رویداد مالی را با زبان ساده توصیف کنید.",
            "تاریخ و مبلغ نمونه را مشخص کنید.",
            "مدرک پشتیبان ساختگی را به رویداد وصل کنید.",
            "تفاوت ثبت مالی با دریافت یا پرداخت پول را توضیح دهید.",
        ),
        required_fields=("event_description", "event_date", "amount_eur", "proof_reference"),
    ),
    Lesson(
        lesson_id="accounting.sales_invoice",
        module="Rechnungen",
        title_fa="آماده‌سازی فاکتور فروش",
        title_de="Ausgangsrechnung vorbereiten",
        objective_fa="اطلاعات پایه فاکتور فروش را آماده و موارد ناقص را شناسایی کنید.",
        steps_fa=(
            "طرف معامله و شرح کالا یا خدمت را مشخص کنید.",
            "تاریخ و مبلغ نمونه را ثبت کنید.",
            "نرخ مالیات را فقط به‌عنوان ورودی آزمایشی علامت بزنید.",
            "پیش‌نویس را کنترل کنید؛ محاسبه ریاضی به‌تنهایی اعتبار قانونی نرخ را ثابت نمی‌کند.",
        ),
        required_fields=("invoice_date", "counterparty_label", "description", "gross_or_net_amount", "proof_reference"),
        requires_specialist_review=True,
    ),
    Lesson(
        lesson_id="accounting.purchase_invoice",
        module="Rechnungen",
        title_fa="ثبت فاکتور خرید و هزینه",
        title_de="Eingangsrechnung und Ausgabe erfassen",
        objective_fa="مدرک هزینه را ثبت کنید و موارد مبهم را برای بررسی علامت بزنید.",
        steps_fa=(
            "فروشنده، تاریخ و شرح خرید را مشخص کنید.",
            "هدف تجاری خرید را توضیح دهید.",
            "مبلغ نمونه و مرجع رسید را ثبت کنید.",
            "در مورد استفاده شخصی یا قابلیت کسر نامشخص، تصمیم قطعی نگیرید.",
        ),
        required_fields=("expense_date", "vendor_label", "description", "business_purpose", "amount_eur", "proof_reference"),
        requires_specialist_review=True,
    ),
    Lesson(
        lesson_id="accounting.bank_reconciliation",
        module="Bankabgleich",
        title_fa="تطبیق تراکنش بانکی",
        title_de="Banktransaktion abgleichen",
        objective_fa="تراکنش بانکی را به مدرک یا فاکتور ساختگی متصل کنید.",
        steps_fa=(
            "تاریخ و مبلغ تراکنش نمونه را بخوانید.",
            "طرف معامله و مرجع پرداخت را بررسی کنید.",
            "مدرک متناظر را پیدا کنید.",
            "تراکنش بدون مدرک را در وضعیت بررسی نگه دارید.",
        ),
        required_fields=("booking_date", "amount_eur", "counterparty_label", "match_reference"),
    ),
    Lesson(
        lesson_id="hr.onboarding",
        module="Personal",
        title_fa="چک‌لیست شروع همکاری کارمند",
        title_de="Mitarbeiter-Onboarding",
        objective_fa="مراحل اداری شروع همکاری را بشناسید و پیش‌نویس چک‌لیست بسازید.",
        steps_fa=(
            "نوع اشتغال و تاریخ شروع را با داده ساختگی مشخص کنید.",
            "چک‌لیست قرارداد و پرونده پرسنلی را مرور کنید.",
            "ثبت‌های بیمه اجتماعی و مالیاتی مربوط را برای بررسی علامت بزنید.",
            "هیچ ثبت رسمی را بدون رسید واقعی انجام‌شده تلقی نکنید.",
        ),
        required_fields=("employment_type", "start_date", "weekly_hours", "contract_check_reference"),
        requires_specialist_review=True,
    ),
    Lesson(
        lesson_id="hr.offboarding",
        module="Personal",
        title_fa="چک‌لیست پایان همکاری",
        title_de="Mitarbeiter-Offboarding",
        objective_fa="مدارک و پرسش‌های لازم برای بررسی پایان همکاری را فهرست کنید.",
        steps_fa=(
            "نوع پایان همکاری را مشخص کنید.",
            "قرارداد و مهلت‌های احتمالی را برای بررسی آماده کنید.",
            "وجود وضعیت‌های دارای حمایت ویژه را به متخصص ارجاع دهید.",
            "دسترسی‌ها، تسویه و اسناد را در چک‌لیست ثبت کنید.",
        ),
        required_fields=("end_type", "proposed_end_date", "contract_check_reference", "open_items"),
        requires_specialist_review=True,
    ),
    Lesson(
        lesson_id="tax.return_preparation",
        module="Steuern",
        title_fa="آماده‌سازی پیش‌نویس گزارش مالیاتی",
        title_de="Steuererklärung vorbereiten",
        objective_fa="اطلاعات دوره و نوع شرکت را برای پیش‌نویس فهرست کنید؛ ارسال رسمی در این ماژول انجام نمی‌شود.",
        steps_fa=(
            "دوره گزارش و نوع حقوقی شرکت آزمایشی را مشخص کنید.",
            "درآمدها، هزینه‌ها و اسناد ناقص را فهرست کنید.",
            "نوع مالیات احتمالی را با منبع رسمی تطبیق دهید.",
            "پیش‌نویس را برای بررسی متخصص آماده کنید؛ ادعای ارسال رسمی نکنید.",
        ),
        required_fields=("reporting_period", "legal_form", "data_completeness", "source_reference"),
        requires_specialist_review=True,
    ),
    Lesson(
        lesson_id="management.monthly_review",
        module="Geschäftsführung",
        title_fa="بازبینی ماهانه مدیرعامل",
        title_de="Monatlicher Geschäftsführungs-Check",
        objective_fa="گزارش ساده درآمد، هزینه، نقدینگی و کارهای باز را مرور کنید.",
        steps_fa=(
            "دوره ماهانه نمونه را انتخاب کنید.",
            "جمع درآمد و هزینه ساختگی را مرور کنید.",
            "مانده نقدی و موارد پرداخت‌نشده را بررسی کنید.",
            "کارهای باز را به مسئول مشخص ارجاع دهید.",
        ),
        required_fields=("reporting_period", "revenue_total_eur", "expense_total_eur", "cash_balance_eur", "open_items"),
    ),
)

_LESSON_INDEX: Mapping[str, Lesson] = {lesson.lesson_id: lesson for lesson in LESSONS}


@dataclass(slots=True)
class GuidedCase:
    """In-memory practice case. It deliberately accepts synthetic data only."""

    case_id: str
    lesson_id: str
    synthetic_data: bool = True
    status: CaseStatus = CaseStatus.DRAFT
    answers: dict[str, str] = field(default_factory=dict)
    history: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.case_id.strip():
            raise LearningWorkflowError("A case ID is required")
        get_lesson(self.lesson_id)
        if self.synthetic_data is not True:
            raise UnsafeDataModeError(
                "This learning prototype accepts synthetic training data only"
            )
        self.history.append("case_created")

    @property
    def lesson(self) -> Lesson:
        return get_lesson(self.lesson_id)

    @property
    def missing_fields(self) -> tuple[str, ...]:
        return tuple(
            field_name
            for field_name in self.lesson.required_fields
            if not self.answers.get(field_name, "").strip()
        )

    def answer(self, field_name: str, value: str) -> None:
        """Record a short synthetic answer for a declared training field."""
        if self.status is not CaseStatus.DRAFT:
            raise LearningWorkflowError("Answers can only be changed while the case is a draft")
        if field_name not in self.lesson.required_fields:
            raise LearningWorkflowError(f"Field is not part of this lesson: {field_name}")
        if not isinstance(value, str) or not value.strip():
            raise LearningWorkflowError("Answer must be a non-empty text value")
        if len(value) > 300:
            raise LearningWorkflowError("Training answers must be 300 characters or fewer")
        self.answers[field_name] = value.strip()
        self.history.append(f"answer_recorded:{field_name}")

    def complete_information(self) -> CaseStatus:
        """Validate training fields and route sensitive topics to specialist review."""
        if self.status is not CaseStatus.DRAFT:
            raise LearningWorkflowError("Only draft cases can complete information")
        if self.missing_fields:
            missing = ", ".join(self.missing_fields)
            raise LearningWorkflowError(f"Required training fields are missing: {missing}")
        if self.lesson.requires_specialist_review:
            self.status = CaseStatus.SPECIALIST_REVIEW_REQUIRED
            self.history.append("specialist_review_required")
        else:
            self.status = CaseStatus.INFORMATION_COMPLETE
            self.history.append("information_complete")
        return self.status

    def complete_training(self) -> CaseStatus:
        """Complete a lesson only when it does not require specialist review."""
        if self.status is CaseStatus.SPECIALIST_REVIEW_REQUIRED:
            raise LearningWorkflowError(
                "This lesson requires qualified review; the prototype cannot approve it"
            )
        if self.status is not CaseStatus.INFORMATION_COMPLETE:
            raise LearningWorkflowError("Complete all required information before finishing")
        self.status = CaseStatus.TRAINING_COMPLETED
        self.history.append("training_completed")
        return self.status


def get_lesson(lesson_id: str) -> Lesson:
    """Return a lesson by ID or raise a clear error."""
    try:
        return _LESSON_INDEX[lesson_id]
    except KeyError as exc:
        raise LearningWorkflowError(f"Unknown lesson: {lesson_id}") from exc


def list_lessons(module: str | None = None) -> tuple[Lesson, ...]:
    """Return the full catalogue or lessons for one module."""
    if module is None:
        return LESSONS
    return tuple(lesson for lesson in LESSONS if lesson.module == module)
