"""
Clinical Guidelines Extra Part 3 and Recovery Drills Manual for RAHFIT AI Decision Engine.
This module provides comprehensive neurological assessments, respiration training protocols,
and psychological recovery guides to support explainable AI and athletic decisions.
"""

from typing import TypedDict


class NeuroAssessment(TypedDict):
    test_name: str
    description_en: str
    description_ar: str
    dermatome_level: str
    myotome_test_en: str
    myotome_test_ar: str
    clinical_implication_en: str
    clinical_implication_ar: str


NEUROLOGICAL_ASSESSMENTS: dict[str, NeuroAssessment] = {
    "l4_nerve_root": {
        "test_name": "L4 Nerve Root Assessment",
        "description_en": "Assess patellar reflex and light touch sensation at the medial malleolus.",
        "description_ar": "تقييم منعكس الداغصة وحساسية اللمس الخفيف عند الكاحل الإنسي.",
        "dermatome_level": "L4",
        "myotome_test_en": "Ankle dorsiflexion against manual resistance (tibialis anterior).",
        "myotome_test_ar": "العطف الظهري للكاحل ضد المقاومة اليدوية (العضلة الظنبوبية الأمامية).",
        "clinical_implication_en": "Weakness indicates potential lumbar disc compression at L3-L4 level.",
        "clinical_implication_ar": "يشير الضعف إلى ضغط محتمل في القرص القطني عند مستوى L3-L4.",
    },
    "l5_nerve_root": {
        "test_name": "L5 Nerve Root Assessment",
        "description_en": "Assess light touch sensation at the dorsum of the foot and first web space.",
        "description_ar": "تقييم حساسية اللمس الخفيف عند ظهر القدم والمسافة بين الإصبعين الأول والثاني.",
        "dermatome_level": "L5",
        "myotome_test_en": "Great toe extension (extensor hallucis longus) and hip abduction.",
        "myotome_test_ar": "تمديد إصبع القدم الكبير (مادة إبهام القدم الطويلة) وإبعاد الورك.",
        "clinical_implication_en": "Weakness indicates potential disc protrusion at L4-L5 level.",
        "clinical_implication_ar": "يشير الضعف إلى بروز محتمل للقرص القطني عند مستوى L4-L5.",
    },
    "s1_nerve_root": {
        "test_name": "S1 Nerve Root Assessment",
        "description_en": "Assess Achilles tendon reflex and sensation at the lateral border of the foot.",
        "description_ar": "تقييم منعكس وتر أخيل والإحساس عند الحافة الجانبية للقدم.",
        "dermatome_level": "S1",
        "myotome_test_en": "Ankle plantarflexion (gastrocnemius/soleus) and eversion.",
        "myotome_test_ar": "العطف الأخمصي للكاحل (العضلة التوأمية/النعلية) وقلب القدم للخارج.",
        "clinical_implication_en": "Diminished reflex indicates potential compression at L5-S1 junction.",
        "clinical_implication_ar": "يشير ضعف المنعكس إلى ضغط محتمل عند التقاء L5-S1.",
    },
}

RESPIRATORY_RECOVERY_PROTOCOLS: dict[str, dict[str, str]] = {
    "box_breathing": {
        "en": "Inhale for 4 seconds, hold for 4 seconds, exhale for 4 seconds, hold empty for 4 seconds. Repeat for 5-10 cycles. Promotes parasympathetic nervous system activation and reduces acute stress.",
        "ar": "استنشق لمدة 4 ثوانٍ، احبس النفس لمدة 4 ثوانٍ، ازفر لمدة 4 ثوانٍ، احبس الرئة فارغة لمدة 4 ثوانٍ. كرر لمدة 5-10 دورات. يعزز تنشيط الجهاز العصبي الباراسمبثاوي ويقلل من التوتر الحاد.",
    },
    "diaphragmatic_activation": {
        "en": "Place one hand on upper chest and the other on abdomen. Inhale deeply through the nose, ensuring only the abdominal hand rises. Exhale slowly through pursed lips. Improves respiratory efficiency and ribcage mobility.",
        "ar": "ضع يدًا واحدة على الجزء العلوي من الصدر والأخرى على البطن. استنشق بعمق من الأنف، وتأكد من ارتفاع اليد الموضوعة على البطن فقط. ازفر ببطء من خلال شفاه مضمومة. يحسن كفاءة التنفس وحركة القفص الصدري.",
    },
    "co2_tolerance_drill": {
        "en": "Perform 4 deep breaths followed by a maximal exhale hold. Repeat 3 times with 2 minutes normal breathing between sets. Enhances metabolic tolerance to hypercapnia and delays dyspnea during high-intensity training.",
        "ar": "أداء 4 أنفاس عميقة يتبعها حبس للنفس عند الزفير الأقصى. كرر 3 مرات مع دقيقتين من التنفس الطبيعي بين المجموعات. يعزز التسامح الأيضي مع زيادة ثاني أكسيد الكربون ويؤخر ضيق التنفس أثناء التدريب عالي الشدة.",
    },
}

ATHLETE_BURNOUT_INDICATORS: dict[str, dict[str, str]] = {
    "emotional_exhaustion": {
        "en": "Feelings of psychological fatigue and depleted energy levels stemming from excessive training loads without adequate recovery. Prescribe active recovery, sleep optimization, and training load reduction.",
        "ar": "مشاعر التعب النفسي ونفاذ مستويات الطاقة الناتجة عن أحمال التدريب المفرطة دون استشفاء كافٍ. تحديد استشفاء نشط، تحسين النوم، وتقليل حمل التدريب.",
    },
    "reduced_accomplishment": {
        "en": "Negative evaluation of performance capacity and athletic abilities. Often linked to lack of physical progression. Focus on small, achievable motor skills and subjective satisfaction indicators.",
        "ar": "تقييم سلبي للقدرة على الأداء والقدرات الرياضية. غالباً ما يرتبط بنقص التقدم البدني. ركز على المهارات الحركية الصغيرة القابلة للتحقيق ومؤشرات الرضا الذاتي.",
    },
    "sport_devaluation": {
        "en": "Loss of interest in physical progression, training routines, and athletic excellence. Immediate indicator of overreaching. Require training load reset and team consultation.",
        "ar": "فقدان الاهتمام بالتقدم البدني وروتين التدريب والتميز الرياضي. مؤشر فوري على الإجهاد المفرط. يتطلب إعادة ضبط حمل التدريب واستشارة الفريق.",
    },
}
