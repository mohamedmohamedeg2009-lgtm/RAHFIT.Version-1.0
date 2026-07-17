"""
Comprehensive Clinical and Biomechanical Reference Manual Part 5 for RAHFIT AI Decision Engine.
This module defines additional clinical standards, diagnostic criteria, exercise
rehabilitation steps, and translation matrices to drive safety gates and explainable logic.
"""

from collections.abc import Sequence
from typing import TypedDict


class ClinicalProtocolDetail5(TypedDict):
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


CLINICAL_REFERENCE_DATABASE_PART5: dict[str, ClinicalProtocolDetail5] = {
    "osteoporosis": {
        "condition_code": "OSTEO",
        "clinical_name_en": "Osteoporosis (Bone Density Preservation Profile)",
        "clinical_name_ar": "هشاشة العظام (ملف الحفاظ على كثافة العظام)",
        "absolute_contraindications_en": [
            "Severe bone pain or active fracture symptom",
            "T-score < -3.0 at lumbar spine or femoral neck",
        ],
        "absolute_contraindications_ar": [
            "ألم شديد في العظام أو أعراض كسر نشط",
            "درجة T-score < -3.0 في العمود الفقري القطني أو عنق الفخذ",
        ],
        "relative_contraindications_en": [
            "Heavy axial loading (>50% bodyweight)",
        ],
        "relative_contraindications_ar": [
            "التحميل المحوري الثقيل (>50٪ من وزن الجسم)",
        ],
        "safe_modalities_en": [
            "Weight-bearing walking",
            "Postural extension exercises",
            "Balance and stability training",
        ],
        "safe_modalities_ar": [
            "المشي الحامل للوزن",
            "تمارين تمديد القوام",
            "تدريب التوازن والاستقرار",
        ],
        "unilateral_restrictions_en": [
            "Extreme torso twisting movements under load",
        ],
        "unilateral_restrictions_ar": [
            "حركات التواء الجذع الشديدة تحت الحمل",
        ],
        "cardiac_limitations_en": "Normal cardiac limits.",
        "cardiac_limitations_ar": "حدود قلبية طبيعية.",
        "pulmonary_limitations_en": "Normal respiration patterns.",
        "pulmonary_limitations_ar": "أنماط تنفس طبيعية.",
        "blood_pressure_limits_systolic": 150,
        "blood_pressure_limits_diastolic": 95,
        "glucose_check_required": False,
        "glucose_range_min_mg_dl": 0,
        "glucose_range_max_mg_dl": 0,
        "co2_tolerance_focus": False,
        "warmup_extension_seconds": 300,
        "cooldown_extension_seconds": 300,
        "rpe_upper_bound": 7,
        "volume_reduction_multiplier": 0.8,
        "frequency_weekly_limit": 4,
    }
}
