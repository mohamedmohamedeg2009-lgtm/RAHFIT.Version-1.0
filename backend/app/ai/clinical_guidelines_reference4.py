"""
Comprehensive Clinical and Biomechanical Reference Manual Part 4 for RAHFIT AI Decision Engine.
This module defines additional clinical standards, diagnostic criteria, exercise
rehabilitation steps, and translation matrices to drive safety gates and explainable logic.
"""

from collections.abc import Sequence
from typing import TypedDict


class ClinicalProtocolDetail4(TypedDict):
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


CLINICAL_REFERENCE_DATABASE_PART4: dict[str, ClinicalProtocolDetail4] = {
    "metabolic_syndrome": {
        "condition_code": "METS",
        "clinical_name_en": "Metabolic Syndrome (Insulin Resistance Profile)",
        "clinical_name_ar": "متلازمة التمثيل الغذائي (ملف مقاومة الأنسولين)",
        "absolute_contraindications_en": [
            "Resting BP > 180/110 mmHg",
            "Severe chest discomfort during dynamic exertion",
        ],
        "absolute_contraindications_ar": [
            "ضغط الدم أثناء الراحة > 180/110 ملم زئبق",
            "انزعاج شديد في الصدر أثناء المجهود الديناميكي",
        ],
        "relative_contraindications_en": [
            "Triglycerides > 150 mg/dL",
            "Waist circumference > 102 cm (male) or 88 cm (female)",
        ],
        "relative_contraindications_ar": [
            "دهون ثلاثية > 150 ملغ/ديسيلتر",
            "محيط الخصر > 102 سم (ذكور) أو 88 سم (إناث)",
        ],
        "safe_modalities_en": [
            "Moderate intensity interval training (MIIT)",
            "Resistance circuit training",
            "Outdoor walking",
        ],
        "safe_modalities_ar": [
            "التدريب الفتري متوسط الشدة (MIIT)",
            "تدريب الدوائر بالمقاومة",
            "المشي في الهواء الطلق",
        ],
        "unilateral_restrictions_en": [
            "High impact jumping or depth drops",
        ],
        "unilateral_restrictions_ar": [
            "القفز عالي التأثير أو الهبوط من العمق",
        ],
        "cardiac_limitations_en": "Monitor heart rate to stay within 55-75% of maximum predicted HR.",
        "cardiac_limitations_ar": "مراقبة ضربات القلب للبقاء في حدود 55-75٪ من أقصى ضربات قلب متوقعة.",
        "pulmonary_limitations_en": "Normal respiration patterns.",
        "pulmonary_limitations_ar": "أنماط تنفس طبيعية.",
        "blood_pressure_limits_systolic": 160,
        "blood_pressure_limits_diastolic": 100,
        "glucose_check_required": False,
        "glucose_range_min_mg_dl": 0,
        "glucose_range_max_mg_dl": 0,
        "co2_tolerance_focus": False,
        "warmup_extension_seconds": 300,
        "cooldown_extension_seconds": 300,
        "rpe_upper_bound": 8,
        "volume_reduction_multiplier": 0.9,
        "frequency_weekly_limit": 5,
    }
}
