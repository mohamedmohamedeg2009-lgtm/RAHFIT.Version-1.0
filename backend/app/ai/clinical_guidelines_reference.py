"""
Comprehensive Clinical and Biomechanical Reference Manual for RAHFIT AI Decision Engine.
This module defines the primary clinical standards, diagnostic criteria, exercise
rehabilitation steps, and translation matrices to drive safety gates and explainable logic.
"""

from collections.abc import Sequence
from typing import TypedDict


class ClinicalProtocolDetail(TypedDict):
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


CLINICAL_REFERENCE_DATABASE: dict[str, ClinicalProtocolDetail] = {
    "hypertension_stage_1": {
        "condition_code": "HTN_S1",
        "clinical_name_en": "Stage 1 Essential Hypertension",
        "clinical_name_ar": "ارتفاع ضغط الدم الأساسي من الدرجة الأولى",
        "absolute_contraindications_en": [
            "Systolic BP > 160 mmHg",
            "Diastolic BP > 100 mmHg",
            "Symptomatic chest pain during exertion",
            "Active orthostatic hypotension",
        ],
        "absolute_contraindications_ar": [
            "ضغط الدم الانقباضي > 160 ملم زئبق",
            "ضغط الدم الانبساطي > 100 ملم زئبق",
            "ألم في الصدر مع المجهود البدني",
            "انخفاض ضغط الدم الانتصابي النشط",
        ],
        "relative_contraindications_en": [
            "Resting BP > 140/90 mmHg",
            "Controlled arrhythmias with pacemaker",
            "Unmanaged diabetes mellitus",
        ],
        "relative_contraindications_ar": [
            "ضغط الدم أثناء الراحة > 140/90 ملم زئبق",
            "عدم انتظام ضربات القلب الخاضع للسيطرة بجهاز تنظيم ضربات القلب",
            "داء السكري غير المنضبط",
        ],
        "safe_modalities_en": [
            "Dynamic aerobic training",
            "Low-resistance circuit training",
            "Bodyweight mobility drills",
        ],
        "safe_modalities_ar": [
            "التدريب الهوائي الديناميكي",
            "تدريب الدوائر منخفض المقاومة",
            "تمارين الحركية بوزن الجسم",
        ],
        "unilateral_restrictions_en": [
            "Heavy single-arm overhead pressing",
            "Heavy unilateral barbell lifting",
        ],
        "unilateral_restrictions_ar": [
            "دفع الدمبل الثقيل فوق الرأس بذراع واحدة",
            "رفع البار الثقيل أحادي الجانب",
        ],
        "cardiac_limitations_en": "Limit maximum heart rate to 75% of age-predicted maximum to prevent excessive myocardial oxygen demand.",
        "cardiac_limitations_ar": "تحديد الحد الأقصى لمعدل ضربات القلب عند 75٪ من الحد الأقصى المتوقع للمحافظة على عضلة القلب.",
        "pulmonary_limitations_en": "Ensure steady, uncontrolled respiratory pattern. Do not hold breath.",
        "pulmonary_limitations_ar": "ضمان نمط تنفس مستقر وغير مقيد. لا تحبس النفس.",
        "blood_pressure_limits_systolic": 160,
        "blood_pressure_limits_diastolic": 100,
        "glucose_check_required": False,
        "glucose_range_min_mg_dl": 0,
        "glucose_range_max_mg_dl": 0,
        "co2_tolerance_focus": False,
        "warmup_extension_seconds": 300,
        "cooldown_extension_seconds": 300,
        "rpe_upper_bound": 7,
        "volume_reduction_multiplier": 0.8,
        "frequency_weekly_limit": 4,
    },
    "type_1_diabetes_mellitus": {
        "condition_code": "T1DM",
        "clinical_name_en": "Type 1 Insulin-Dependent Diabetes",
        "clinical_name_ar": "داء السكري من النوع الأول المعتمد على الأنسولين",
        "absolute_contraindications_en": [
            "Blood glucose < 70 mg/dL (Hypoglycemia risk)",
            "Blood glucose > 300 mg/dL with ketones (Ketoacidosis risk)",
            "Active diabetic retinopathy symptoms",
        ],
        "absolute_contraindications_ar": [
            "سكر الدم < 70 ملغ/ديسيلتر (خطر انخفاض السكر)",
            "سكر الدم > 300 ملغ/ديسيلتر مع وجود الكيتونات (خطر حموضة الدم الكيتونية)",
            "أعراض اعتلال الشبكية السكري النشط",
        ],
        "relative_contraindications_en": [
            "Blood glucose 250-300 mg/dL without ketones",
            "Severe autonomic neuropathy",
        ],
        "relative_contraindications_ar": [
            "سكر الدم 250-300 ملغ/ديسيلتر بدون كيتونات",
            "الاعتلال العصبي المستقل الشديد",
        ],
        "safe_modalities_en": [
            "Moderate walking",
            "Static resistance bands",
            "Non-weight-bearing cycling",
        ],
        "safe_modalities_ar": [
            "المشي المعتدل",
            "أحزمة المقاومة الثابتة",
            "ركوب الدراجات دون تحميل الوزن",
        ],
        "unilateral_restrictions_en": [
            "High impact jumping and bounding",
        ],
        "unilateral_restrictions_ar": [
            "القفز والوثب عالي التأثير",
        ],
        "cardiac_limitations_en": "Monitor heart rate carefully to identify autonomic neuropathy complications.",
        "cardiac_limitations_ar": "مراقبة معدل ضربات القلب بعناية لتحديد مضاعفات الاعتلال العصبي المستقل.",
        "pulmonary_limitations_en": "Ensure proper respiration during recovery cycles.",
        "pulmonary_limitations_ar": "ضمان التنفس السليم خلال دورات الاستشفاء.",
        "blood_pressure_limits_systolic": 140,
        "blood_pressure_limits_diastolic": 90,
        "glucose_check_required": True,
        "glucose_range_min_mg_dl": 100,
        "glucose_range_max_mg_dl": 250,
        "co2_tolerance_focus": True,
        "warmup_extension_seconds": 180,
        "cooldown_extension_seconds": 180,
        "rpe_upper_bound": 8,
        "volume_reduction_multiplier": 0.9,
        "frequency_weekly_limit": 5,
    },
    "asthma_severe_persistent": {
        "condition_code": "ASTHMA_SP",
        "clinical_name_en": "Severe Persistent Bronchial Asthma",
        "clinical_name_ar": "ربو شعبي مستمر شديد",
        "absolute_contraindications_en": [
            "Forced expiratory volume in 1 second (FEV1) < 60% of predicted",
            "Active wheezing or chest tightness at rest",
            "Recent acute hospitalization for respiratory crisis within 30 days",
        ],
        "absolute_contraindications_ar": [
            "حجم الزفير القسري في الثانية الأولى < 60٪ من المتوقع",
            "أزيز الصدر النشط أو ضيق الصدر أثناء الراحة",
            "دخول المستشفى مؤخراً بسبب أزمة تنفسية حادة في غضون 30 يوماً",
        ],
        "relative_contraindications_en": [
            "Cold dry outdoor environments",
            "High environmental allergen counts (pollen, dust)",
        ],
        "relative_contraindications_ar": [
            "البيئات الخارجية الباردة والجافة",
            "ارتفاع مسببات الحساسية البيئية (حبوب اللقاح والغبار)",
        ],
        "safe_modalities_en": [
            "Indoor swimming in warm humid pools",
            "Controlled walking on treadmill",
            "Gentle dynamic stretching",
        ],
        "safe_modalities_ar": [
            "السباحة الداخلية في حمامات دافئة ورطبة",
            "المشي المنظم على جهاز المشي",
            "الإطالة الديناميكية اللطيفة",
        ],
        "unilateral_restrictions_en": [
            "High ventilation conditioning intervals",
        ],
        "unilateral_restrictions_ar": [
            "فترات التكييف البدني ذات التهوية العالية للرئتين",
        ],
        "cardiac_limitations_en": "Avoid exceeding aerobic threshold limit.",
        "cardiac_limitations_ar": "تجنب تجاوز حد العتبة الهوائية.",
        "pulmonary_limitations_en": "Require bronchodilator inhalation 15 minutes prior to session.",
        "pulmonary_limitations_ar": "طلب استنشاق موسع الشعب الهوائية قبل 15 دقيقة من الجلسة.",
        "blood_pressure_limits_systolic": 150,
        "blood_pressure_limits_diastolic": 95,
        "glucose_check_required": False,
        "glucose_range_min_mg_dl": 0,
        "glucose_range_max_mg_dl": 0,
        "co2_tolerance_focus": True,
        "warmup_extension_seconds": 900,
        "cooldown_extension_seconds": 600,
        "rpe_upper_bound": 6,
        "volume_reduction_multiplier": 0.7,
        "frequency_weekly_limit": 3,
    },
}

CLINICAL_EXPLANATORY_BUNLDES: dict[str, dict[str, str]] = {
    "myocardial_infarction_recovery": {
        "en": "Cardiac tissue healing requires low metabolic stress. Keep cardiac demand low. High intensity is completely restricted.",
        "ar": "يتطلب شفاء أنسجة القلب إجهاداً أيضياً منخفضاً. حافظ على انخفاض طلب القلب. الشدة العالية مقيدة تماماً.",
    },
    "osteoporosis_safety": {
        "en": "Skeletal structures are vulnerable to compression. Axial loading on spine must be strictly avoided. Focus on non-impact movement.",
        "ar": "الهياكل العظمية عرضة للكسر تحت الضغط. يجب تجنب التحميل المحوري على العمود الفقري بشكل صارم. التركيز على الحركة غير التصادمية.",
    },
    "sciatica_nerve_flaring": {
        "en": "Lumbar nerve root is irritated. Spinal flexion and hamstring stretching are temporarily suspended to avoid nerve tension.",
        "ar": "جذر العصب القطني متهيج. يتم تعليق ثني العمود الفقري وإطالة أوتار الركبة مؤقتاً لتجنب إجهاد العصب.",
    },
}
