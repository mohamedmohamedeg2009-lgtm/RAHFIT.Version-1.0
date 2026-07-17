"""
Clinical Guidelines Extra and Athletic Reference Manual for RAHFIT AI Decision Engine.
This module provides comprehensive sports periodization models, structural balancing protocols,
and nutrition hydration guidelines to support explainable AI and athletic decisions.
"""

from collections.abc import Sequence
from typing import TypedDict


class PeriodizationPhase(TypedDict):
    phase_name: str
    duration_weeks: int
    focus_en: str
    focus_ar: str
    volume_progression: Sequence[float]
    intensity_rpe_progression: Sequence[int]
    recommended_recovery_hours: int


PERIODIZATION_MODELS: dict[str, PeriodizationPhase] = {
    "hypertrophy": {
        "phase_name": "Hypertrophy and Muscle Accumulation",
        "duration_weeks": 4,
        "focus_en": "Maximize mechanical tension and metabolic stress. Accumulate volume gradually over 3 loading weeks, followed by a 1-week deload.",
        "focus_ar": "تعظيم التوتر الميكانيكي والإجهاد الأيضي. تراكم حجم التمرين تدريجياً على مدى 3 أسابيع تحميل، يليه أسبوع واحد لتخفيف الحمل (deload).",
        "volume_progression": [1.0, 1.1, 1.2, 0.6],
        "intensity_rpe_progression": [7, 8, 9, 5],
        "recommended_recovery_hours": 72,
    },
    "strength": {
        "phase_name": "Basic Strength and Neural Drive",
        "duration_weeks": 4,
        "focus_en": "Increase rate of force development and motor unit recruitment. Higher intensity, lower volume, extended rest periods between sets.",
        "focus_ar": "زيادة معدل تطوير القوة وتوظيف الوحدات الحركية. شدة أعلى، حجم أقل، فترات راحة ممتدة بين المجموعات.",
        "volume_progression": [0.8, 0.85, 0.9, 0.5],
        "intensity_rpe_progression": [8, 9, 10, 6],
        "recommended_recovery_hours": 96,
    },
    "power": {
        "phase_name": "Power, Velocity and Tapering",
        "duration_weeks": 3,
        "focus_en": "Maximize velocity of contraction. Focus on explosive concentric movements, plyometrics, and low fatigue accumulation.",
        "focus_ar": "تعظيم سرعة الانقباض. التركيز على الحركات الانقباضية الانفجارية، البليومتريكس، وتراكم التعب المنخفض.",
        "volume_progression": [0.6, 0.65, 0.4],
        "intensity_rpe_progression": [8, 8, 6],
        "recommended_recovery_hours": 48,
    },
}

ATHLETIC_HYDRATION_GUIDELINES: dict[str, dict[str, str]] = {
    "pre_workout": {
        "en": "Consume 5-7 mL of water or electrolyte solution per kg of body weight at least 4 hours prior to exercise. If urine is dark, consume an additional 3-5 mL per kg 2 hours prior.",
        "ar": "تناول 5-7 مل من الماء أو محلول الكتروليت لكل كيلوغرام من وزن الجسم قبل 4 ساعات على الأقل من التمرين. إذا كان البول داكناً، تناول 3-5 مل إضافية لكل كيلوغرام قبل ساعتين.",
    },
    "intra_workout": {
        "en": "Aim to limit body mass loss to < 2% of initial weight. Typically consume 400-800 mL of fluid per hour of intense exercise, incorporating 6-8% carbohydrate concentration in hot environments.",
        "ar": "احرص على ألا يتجاوز فقدان كتلة الجسم 2٪ من الوزن الأولي. عادة ما يتم استهلاك 400-800 مل من السوائل لكل ساعة من التمرين الشديد، مع دمج تركيز كربوهيدرات بنسبة 6-8٪ في البيئات الحارة.",
    },
    "post_workout": {
        "en": "Consume 1.5 liters of fluid for every 1 kg of body mass lost during exercise. Ensure adequate sodium content to promote fluid retention and plasma volume restoration.",
        "ar": "تناول 1.5 لتر من السوائل مقابل كل 1 كيلوغرام من كتلة الجسم المفقودة أثناء التمرين. تأكد من وجود محتوى كافٍ من الصوديوم لتعزيز احتباس السوائل واستعادة حجم البلازما.",
    },
}

STRUCTURAL_BALANCE_PROTOCOLS: dict[str, dict[str, str]] = {
    "upper_body_push_pull": {
        "en": "Maintain a 1:1 ratio between horizontal pushing volume and horizontal pulling volume to preserve glenohumeral stability and thoracic posture.",
        "ar": "حافظ على نسبة 1:1 بين حجم الدفع الأفقي وحجم السحب الأفقي للحفاظ على استقرار المفصل الحقاني العضدية ووضعية الصدر.",
    },
    "quad_hamstring_ratio": {
        "en": "Target hamstring strength (specifically eccentric knee flexion) to be at least 60% of quadriceps concentric strength to reduce ACL strain.",
        "ar": "استهدف أن تكون قوة أوتار الركبة (تحديداً ثني الركبة اللامركزي) 60٪ على الأقل من قوة العضلة رباعية الرؤوس التركيزية لتقليل إجهاد الرباط الصليبي الأمامي.",
    },
    "hip_extension_vs_flexion": {
        "en": "Perform active hip flexor stretching in conjunction with gluteal activation drills to prevent anterior pelvic tilt and lower back loading.",
        "ar": "قم بتمارين إطالة عضلات الورك القابضة النشطة بالتزامن مع تمارين تنشيط الألوية لمنع ميل الحوض الأمامي وتحميل أسفل الظهر.",
    },
}

COACH_EXPLAINER_BUNLDES: dict[str, dict[str, str]] = {
    "overtraining_syndrome": {
        "en": "Persistent drop in heart rate variability (HRV), elevated resting heart rate, insomnia, and mood changes. Recommend immediate deload or cessation of training for 7-14 days.",
        "ar": "انخفاض مستمر في تقلب معدل ضربات القلب (HRV)، وارتفاع معدل ضربات القلب أثناء الراحة، والأرق، وتغيرات الحالة المزاجية. يوصى بتخفيف الحمل الفوري أو التوقف عن التدريب لمدة 7-14 يوماً.",
    },
    "rhabdomyolysis_warning": {
        "en": "Extreme muscle pain, profound weakness, and dark tea-colored urine. Immediately block all exercise, recommend emergency medical consultation, and restrict fluid intake to medical supervision.",
        "ar": "ألم عضلي شديد، ضعف شديد، وبول داكن اللون مثل الشاي. أوقف جميع التمارين فوراً، ويوصى باستشارة طبية طارئة، وتقييد تناول السوائل تحت الإشراف الطبي.",
    },
    "metabolic_adaptation_delay": {
        "en": "Biological slowing of metabolic rate due to prolonged caloric deficit. Prevent further calorie cuts; prescribe a 1-2 week metabolic break at maintenance calories.",
        "ar": "تباطؤ بيولوجي لمعدل الأيض بسبب العجز الطويل في السعرات الحرارية. منع المزيد من خفض السعرات الحرارية؛ حدد فترة استراحة أيضية لمدة 1-2 أسبوع عند سعرات المحافظة.",
    },
}
