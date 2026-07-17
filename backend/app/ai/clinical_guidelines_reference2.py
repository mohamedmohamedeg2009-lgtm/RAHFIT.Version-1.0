"""
Comprehensive Clinical and Biomechanical Reference Manual Part 2 for RAHFIT AI Decision Engine.
This module defines additional clinical standards, diagnostic criteria, exercise
rehabilitation steps, and translation matrices to drive safety gates and explainable logic.
"""

from collections.abc import Sequence
from typing import TypedDict


class ClinicalProtocolDetail2(TypedDict):
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


CLINICAL_REFERENCE_DATABASE_PART2: dict[str, ClinicalProtocolDetail2] = {
    "chronic_heart_failure": {
        "condition_code": "CHF_S1",
        "clinical_name_en": "Stable Chronic Heart Failure (NYHA Class I-II)",
        "clinical_name_ar": "فشل القلب المزمن المستقر (درجة NYHA الأولى والثانية)",
        "absolute_contraindications_en": [
            "Decompensated heart failure status",
            "Resting heart rate > 110 bpm",
            "Unstable angina pectoris",
        ],
        "absolute_contraindications_ar": [
            "حالة قصور القلب غير المعاوض",
            "معدل ضربات القلب أثناء الراحة > 110 نبضة في الدقيقة",
            "الذبحة الصدرية غير المستقرة",
        ],
        "relative_contraindications_en": [
            "Moderate valve disease",
            "Severe pulmonary hypertension",
        ],
        "relative_contraindications_ar": [
            "مرض صمامات القلب المعتدل",
            "ارتفاع ضغط الدم الرئوي الشديد",
        ],
        "safe_modalities_en": [
            "Low-intensity cycling",
            "Seated dynamic arm exercises",
            "Gentle stretching and breathing",
        ],
        "safe_modalities_ar": [
            "ركوب الدراجات منخفض الشدة",
            "تمارين الذراع الديناميكية جلوساً",
            "الإطالة اللطيفة والتنفس",
        ],
        "unilateral_restrictions_en": [
            "Extreme bilateral lower body loading",
        ],
        "unilateral_restrictions_ar": [
            "تحميل الجزء السفلي من الجسم بشكل ثنائي مفرط",
        ],
        "cardiac_limitations_en": "Keep target heart rate strictly below anaerobic threshold.",
        "cardiac_limitations_ar": "الحفاظ على معدل ضربات القلب المستهدف أقل من العتبة اللاهوائية بشكل صارم.",
        "pulmonary_limitations_en": "Monitor dyspnea scale carefully; keep score below 3 on 10-point scale.",
        "pulmonary_limitations_ar": "مراقبة مقياس ضيق التنفس بعناية؛ الحفاظ على درجة أقل من 3 على مقياس من 10 نقاط.",
        "blood_pressure_limits_systolic": 140,
        "blood_pressure_limits_diastolic": 90,
        "glucose_check_required": False,
        "glucose_range_min_mg_dl": 0,
        "glucose_range_max_mg_dl": 0,
        "co2_tolerance_focus": False,
        "warmup_extension_seconds": 600,
        "cooldown_extension_seconds": 600,
        "rpe_upper_bound": 5,
        "volume_reduction_multiplier": 0.6,
        "frequency_weekly_limit": 3,
    },
    "rheumatoid_arthritis_flare": {
        "condition_code": "RA_FLARE",
        "clinical_name_en": "Rheumatoid Arthritis Active Joint Flare-up",
        "clinical_name_ar": "نوبة نشطة لالتهاب المفاصل الروماتويدي",
        "absolute_contraindications_en": [
            "Acute joint inflammation with heat and redness",
            "Systemic fever or extreme fatigue crisis",
        ],
        "absolute_contraindications_ar": [
            "التهاب المفاصل الحاد مع حرارة واحمرار",
            "الحمى الجهازية أو أزمة التعب الشديد",
        ],
        "relative_contraindications_en": [
            "Mild joint swelling without pain",
        ],
        "relative_contraindications_ar": [
            "تورم خفيف في المفاصل دون ألم",
        ],
        "safe_modalities_en": [
            "Passive range of motion",
            "Isometric loading at pain-free angles",
            "Water-based gentle movement",
        ],
        "safe_modalities_ar": [
            "نطاق الحركة السلبي",
            "التحميل الثابت عند زوايا خالية من الألم",
            "الحركة اللطيفة في الماء",
        ],
        "unilateral_restrictions_en": [
            "High joint shearing dynamic loads",
        ],
        "unilateral_restrictions_ar": [
            "أحمال ديناميكية ذات قوى قص عالية للمفاصل",
        ],
        "cardiac_limitations_en": "Minimal cardiac impact.",
        "cardiac_limitations_ar": "تأثير ضئيل على القلب.",
        "pulmonary_limitations_en": "Normal respiration patterns.",
        "pulmonary_limitations_ar": "أنماط تنفس طبيعية.",
        "blood_pressure_limits_systolic": 150,
        "blood_pressure_limits_diastolic": 95,
        "glucose_check_required": False,
        "glucose_range_min_mg_dl": 0,
        "glucose_range_max_mg_dl": 0,
        "co2_tolerance_focus": False,
        "warmup_extension_seconds": 480,
        "cooldown_extension_seconds": 480,
        "rpe_upper_bound": 5,
        "volume_reduction_multiplier": 0.5,
        "frequency_weekly_limit": 2,
    },
}
