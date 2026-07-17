"""
Comprehensive Clinical and Biomechanical Reference Manual Part 3 for RAHFIT AI Decision Engine.
This module defines additional clinical standards, diagnostic criteria, exercise
rehabilitation steps, and translation matrices to drive safety gates and explainable logic.
"""

from collections.abc import Sequence
from typing import TypedDict


class ClinicalProtocolDetail3(TypedDict):
    condition_code: str
    clinical_name_en: str
    clinical_name_ar: str
    absolute_contraindications_en: Sequence[str]
    absolute_contraindications_ar: Sequence[str]
    relative_contraindications_en: Sequence[str]
    relative_contraindications_ar: Sequence[str]
    safe_modalities_en: Sequence[str]
    safe_modalities_ar: Sequence[str]
    unilateral_restrictions_en: Sequence[str]
    unilateral_restrictions_ar: Sequence[str]
    cardiac_limitations_en: str
    cardiac_limitations_ar: str
    pulmonary_limitations_en: str
    pulmonary_limitations_ar: str
    blood_pressure_limits_systolic: int
    blood_pressure_limits_diastolic: int
    glucose_check_required: bool
    glucose_range_min_mg_dl: int
    glucose_range_max_mg_dl: int
    co2_tolerance_focus: bool
    warmup_extension_seconds: int
    cooldown_extension_seconds: int
    rpe_upper_bound: int
    volume_reduction_multiplier: float
    frequency_weekly_limit: int


CLINICAL_REFERENCE_DATABASE_PART3: dict[str, ClinicalProtocolDetail3] = {
    "copd_stable": {
        "condition_code": "COPD_STABLE",
        "clinical_name_en": "Stable Chronic Obstructive Pulmonary Disease",
        "clinical_name_ar": "مرض الانسداد الرئوي المزمن المستقر",
        "absolute_contraindications_en": [
            "Oxygen saturation < 88% at rest",
            "Acute respiratory tract infection",
            "Severe dyspnea at rest",
        ],
        "absolute_contraindications_ar": [
            "درجة تشبع الأكسجين < 88٪ أثناء الراحة",
            "عدوى الجهاز التنفسي الحادة",
            "ضيق التنفس الشديد أثناء الراحة",
        ],
        "relative_contraindications_en": [
            "Exercise-induced hypoxemia",
        ],
        "relative_contraindications_ar": [
            "نقص أكسجة الدم الناجم عن التمرين",
        ],
        "safe_modalities_en": [
            "Low-intensity walking",
            "Upper body light resistance training",
            "Pursed-lip breathing exercises",
        ],
        "safe_modalities_ar": [
            "المشي منخفض الشدة",
            "تدريب المقاومة الخفيف للجزء العلوي من الجسم",
            "تمارين التنفس بضم الشفتين",
        ],
        "unilateral_restrictions_en": [
            "High intensity lower body dynamic training",
        ],
        "unilateral_restrictions_ar": [
            "التدريب الديناميكي عالي الشدة للجزء السفلي من الجسم",
        ],
        "cardiac_limitations_en": "Avoid excessive heart rate elevation to minimize ventilatory demand.",
        "cardiac_limitations_ar": "تجنب الارتفاع المفرط في معدل ضربات القلب لتقليل الطلب على التهوية.",
        "pulmonary_limitations_en": "Stop exercise immediately if oxygen saturation drops below 88%.",
        "pulmonary_limitations_ar": "أوقف التمرين فوراً إذا انخفض تشبع الأكسجين عن 88٪.",
        "blood_pressure_limits_systolic": 150,
        "blood_pressure_limits_diastolic": 95,
        "glucose_check_required": False,
        "glucose_range_min_mg_dl": 0,
        "glucose_range_max_mg_dl": 0,
        "co2_tolerance_focus": True,
        "warmup_extension_seconds": 600,
        "cooldown_extension_seconds": 600,
        "rpe_upper_bound": 5,
        "volume_reduction_multiplier": 0.6,
        "frequency_weekly_limit": 3,
    }
}
