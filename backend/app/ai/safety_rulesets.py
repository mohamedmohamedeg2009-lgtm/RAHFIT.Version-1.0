"""
AI Safety Rulesets & Clinical Guidelines for RAHFIT Decision Engine.
Contains exercise rehabilitation mappings, chronic condition safety thresholds,
and post-surgery recovery protocols to support deterministic safety gates.
"""

from collections.abc import Sequence
from typing import TypedDict


class Substitution(TypedDict):
    original_pattern: str
    safe_alternative: str
    rationale_en: str
    rationale_ar: str
    muscle_groups_involved: Sequence[str]
    max_rpe: int


class SafetyProtocol(TypedDict):
    condition_name: str
    max_intensity_rpe: int
    extend_warmup_minutes: int
    restrict_valsalva: bool
    requires_glucose_check: bool
    warning_en: str
    warning_ar: str
    rehab_focus: Sequence[str]


# 1. Comprehensive Exercise Rehabilitation & Substitutions Mapping
# Covers all primary and secondary muscle groups and patterns.
EXERCISE_SUBSTITUTIONS: dict[str, Sequence[Substitution]] = {
    "knee": [
        {
            "original_pattern": "barbell_squat",
            "safe_alternative": "leg_press_high_foot_placement",
            "rationale_en": "Reduces shear stress on the patella tendon while maintaining quadriceps and gluteal engagement.",
            "rationale_ar": "يقلل من إجهاد القص على وتر الداغصة مع الحفاظ على تشغيل العضلة رباعية الرؤوس والألوية.",
            "muscle_groups_involved": ["quadriceps", "gluteus_maximus"],
            "max_rpe": 6,
        },
        {
            "original_pattern": "walking_lunge",
            "safe_alternative": "isometric_wall_sit",
            "rationale_en": "Eliminates dynamic shear force on the knee joint capsule during acute inflammatory phases.",
            "rationale_ar": "يلغي قوة القص الديناميكية على كبسولة مفصل الركبة خلال مراحل الالتهاب الحادة.",
            "muscle_groups_involved": ["quadriceps"],
            "max_rpe": 5,
        },
        {
            "original_pattern": "bulgarian_split_squat",
            "safe_alternative": "supported_step_up",
            "rationale_en": "Minimizes vertical knee travel and stabilizes the pelvis to reduce pressure on the patellofemoral track.",
            "rationale_ar": "يقلل من الحركة العمودية للركبة ويثبت الحوض لتقليل الضغط على المسار الرضفي الفخذي.",
            "muscle_groups_involved": ["quadriceps", "hamstrings"],
            "max_rpe": 6,
        },
        {
            "original_pattern": "leg_extension",
            "safe_alternative": "terminal_knee_extension_banded",
            "rationale_en": "Avoids open-chain terminal extension shear while building vastus medialis obliquus strength.",
            "rationale_ar": "يتجنب قوة القص عند الامتداد النهائي للمسار المفتوح مع بناء قوة العضلة المتسعة الإنسية.",
            "muscle_groups_involved": ["quadriceps"],
            "max_rpe": 5,
        },
    ],
    "shoulder": [
        {
            "original_pattern": "overhead_press",
            "safe_alternative": "landmine_press",
            "rationale_en": "Allows a neutral grip and angled pressing plane, avoiding subacromial impingement.",
            "rationale_ar": "يسمح بقبضة محايدة وزاوية دفع مائلة، مما يتجنب الاصطدام تحت الأخرم.",
            "muscle_groups_involved": ["deltoids", "triceps"],
            "max_rpe": 6,
        },
        {
            "original_pattern": "barbell_bench_press",
            "safe_alternative": "dumbbell_floor_press",
            "rationale_en": "Limits the range of motion at the bottom of the lift, protecting the anterior glenohumeral capsule.",
            "rationale_ar": "يحد من نطاق الحركة في الجزء السفلي من الرفعة، مما يحمي الكبسولة الحقانية العضدية الأمامية.",
            "muscle_groups_involved": ["pectoralis_major", "triceps"],
            "max_rpe": 7,
        },
        {
            "original_pattern": "wide_grip_pullup",
            "safe_alternative": "neutral_grip_lat_pulldown",
            "rationale_en": "Reduces extreme shoulder abduction and external rotation, preserving rotator cuff integrity.",
            "rationale_ar": "يقلل من إبعاد الكتف الشديد والدوران الخارجي، مما يحافظ على سلامة الكفة المدورة.",
            "muscle_groups_involved": ["latissimus_dorsi", "biceps"],
            "max_rpe": 6,
        },
        {
            "original_pattern": "dumbbell_fly",
            "safe_alternative": "cable_press_around",
            "rationale_en": "Maintains constant tension without placing the shoulder in a high-leverage vulnerable stretched position.",
            "rationale_ar": "يحافظ على شد مستمر دون وضع الكتف في وضع تمدد ضعيف ذي رافعة مالية عالية.",
            "muscle_groups_involved": ["pectoralis_major"],
            "max_rpe": 6,
        },
    ],
    "lower_back": [
        {
            "original_pattern": "conventional_deadlift",
            "safe_alternative": "trap_bar_deadlift_high_handles",
            "rationale_en": "Keeps the load closer to the body's center of gravity, reducing lumbar shear stress.",
            "rationale_ar": "يبقي الحمل أقرب إلى مركز جاذبية الجسم، مما يقلل من إجهاد القص القطني.",
            "muscle_groups_involved": ["erector_spinae", "gluteus_maximus", "hamstrings"],
            "max_rpe": 6,
        },
        {
            "original_pattern": "barbell_row",
            "safe_alternative": "chest_supported_dumbbell_row",
            "rationale_en": "Removes the requirement for spinal stabilization under load, sparing the lumbar spine.",
            "rationale_ar": "يزيل متطلبات تثبيت العمود الفقري تحت الحمل، مما يريح العمود الفقري القطني.",
            "muscle_groups_involved": ["latissimus_dorsi", "rhomboids"],
            "max_rpe": 7,
        },
        {
            "original_pattern": "standing_overhead_press",
            "safe_alternative": "seated_dumbbell_press_fully_supported",
            "rationale_en": "Prevents hyper-extension of the lumbar spine under axial loading.",
            "rationale_ar": "يمنع فرط تمدد العمود الفقري القطني تحت التحميل المحوري.",
            "muscle_groups_involved": ["deltoids", "triceps"],
            "max_rpe": 6,
        },
    ],
    "elbow": [
        {
            "original_pattern": "barbell_curl",
            "safe_alternative": "incline_dumbbell_hammer_curl",
            "rationale_en": "Puts the forearm in a neutral position, reducing strain on the lateral and medial epicondyle.",
            "rationale_ar": "يضع الساعد في وضع محايد، مما يقلل من الضغط على اللقيمة الجانبية والإنسية.",
            "muscle_groups_involved": ["biceps", "brachioradialis"],
            "max_rpe": 6,
        },
        {
            "original_pattern": "skull_crusher",
            "safe_alternative": "cable_triceps_pushdown_rope",
            "rationale_en": "Allows a flexible hand path and reduces elbow flexion torque at end range.",
            "rationale_ar": "يسمح بمسار يد مرن ويقلل من عزم ثني المرفق عند النطاق النهائي.",
            "muscle_groups_involved": ["triceps"],
            "max_rpe": 7,
        },
    ],
    "ankle": [
        {
            "original_pattern": "standing_calf_raise",
            "safe_alternative": "seated_calf_raise_isometric",
            "rationale_en": "Maintains Achilles tendon activation while avoiding dynamic overload in vulnerable dorsiflexion ranges.",
            "rationale_ar": "يحافظ على تنشيط وتر أخيل مع تجنب الحمل الزائد الديناميكي في نطاقات عطف ظهري ضعيفة.",
            "muscle_groups_involved": ["soleus"],
            "max_rpe": 6,
        },
        {
            "original_pattern": "barbell_back_squat",
            "safe_alternative": "box_squat_flat_foot",
            "rationale_en": "Limits ankle dorsiflexion requirements by keeping the shin vertical, sparing the anterior ankle joint.",
            "rationale_ar": "يحد من متطلبات العطف الظهري للكاحل عن طريق الحفاظ على عمودية قصبة الساق، مما يريح مفصل الكاحل الأمامي.",
            "muscle_groups_involved": ["quadriceps", "gluteus_maximus"],
            "max_rpe": 6,
        },
    ],
    "wrist": [
        {
            "original_pattern": "barbell_bench_press",
            "safe_alternative": "dumbbell_press_neutral_grip",
            "rationale_en": "Neutral grip prevents hyperextension of the wrist under heavy loads.",
            "rationale_ar": "تمنع القبضة المحايدة فرط تمدد المعصم تحت الأحمال الثقيلة.",
            "muscle_groups_involved": ["pectoralis_major", "triceps"],
            "max_rpe": 7,
        },
        {
            "original_pattern": "straight_bar_pushup",
            "safe_alternative": "dumbbell_supported_pushup_neutral_wrist",
            "rationale_en": "Keeping the wrist straight on handles removes the extreme extension stress.",
            "rationale_ar": "الحفاظ على استقامة المعصم على المقابض يزيل إجهاد التمدد الشديد.",
            "muscle_groups_involved": ["pectoralis_major", "triceps"],
            "max_rpe": 6,
        },
    ],
}

# 2. Chronic Medical Condition Safety Protocols
# Integrates with the safety check flow.
CHRONIC_CONDITION_PROTOCOLS: dict[str, SafetyProtocol] = {
    "hypertension": {
        "condition_name": "Hypertension",
        "max_intensity_rpe": 7,
        "extend_warmup_minutes": 5,
        "restrict_valsalva": True,
        "requires_glucose_check": False,
        "warning_en": "Avoid performing the Valsalva maneuver. Maintain steady breathing and limit maximum RPE to 7.",
        "warning_ar": "تجنب مناورة فالسالفا. حافظ على تنفس مستمر وحدد الحد الأقصى لمعدل الجهد المحسوس عند 7.",
        "rehab_focus": ["cardiovascular_efficiency", "aerobic_base"],
    },
    "type_2_diabetes": {
        "condition_name": "Type 2 Diabetes",
        "max_intensity_rpe": 8,
        "extend_warmup_minutes": 0,
        "restrict_valsalva": False,
        "requires_glucose_check": True,
        "warning_en": "Verify blood glucose levels are within 100-250 mg/dL before training. Keep fast-acting carbohydrates nearby.",
        "warning_ar": "تحقق من أن مستويات السكر في الدم تتراوح بين 100-250 ملغ/ديسيلتر قبل التمرين. احتفظ بكربوهيدرات سريعة الامتصاص قريبة منك.",
        "rehab_focus": ["insulin_sensitivity", "glucose_clearance"],
    },
    "asthma": {
        "condition_name": "Asthma",
        "max_intensity_rpe": 7,
        "extend_warmup_minutes": 10,
        "restrict_valsalva": False,
        "requires_glucose_check": False,
        "warning_en": "Perform a gradual 15-minute warm-up. Ensure your rescue inhaler is present and accessible.",
        "warning_ar": "قم بالإحماء التدريجي لمدة 15 دقيقة. تأكد من وجود بخاخ الربو الخاص بك وسهولة الوصول إليه.",
        "rehab_focus": ["bronchial_efficiency", "aerobic_capacity"],
    },
    "coronary_heart_disease": {
        "condition_name": "Coronary Heart Disease",
        "max_intensity_rpe": 5,
        "extend_warmup_minutes": 15,
        "restrict_valsalva": True,
        "requires_glucose_check": False,
        "warning_en": "Strict intensity restriction. Keep RPE below 5. Continuous heart rate monitoring recommended.",
        "warning_ar": "تقييد صارم للشدة. حافظ على معدل الجهد المحسوس أقل من 5. يوصى بمراقبة مستمرة لمعدل ضربات القلب.",
        "rehab_focus": ["cardiac_rehab", "circulation"],
    },
    "epilepsy": {
        "condition_name": "Epilepsy",
        "max_intensity_rpe": 7,
        "extend_warmup_minutes": 5,
        "restrict_valsalva": False,
        "requires_glucose_check": False,
        "warning_en": "Avoid extreme fatigue or hyperventilating patterns. Train with a partner when possible.",
        "warning_ar": "تجنب التعب الشديد أو أنماط التنفس المفرط. تدرب مع شريك كلما أمكن ذلك.",
        "rehab_focus": ["stress_reduction", "nervous_system_stability"],
    },
    "rheumatoid_arthritis": {
        "condition_name": "Rheumatoid Arthritis",
        "max_intensity_rpe": 6,
        "extend_warmup_minutes": 10,
        "restrict_valsalva": False,
        "requires_glucose_check": False,
        "warning_en": "Modify movements to avoid loading inflamed joints. Focus on range of motion over absolute weight.",
        "warning_ar": "قم بتعديل الحركات لتجنب تحميل المفاصل الملتهبة. ركز على نطاق الحركة بدلاً من الوزن المطلق.",
        "rehab_focus": ["joint_mobility", "synovial_flow"],
    },
}


# 3. Phased Surgery Recovery Guidelines
# Maps weeks elapsed since surgery to specific safety restrictions.
class SurgeryRule(TypedDict):
    status: str
    allowed_rpe: int
    volume_multiplier: float
    restrictions_en: str
    restrictions_ar: str


SURGERY_RECOVERY_GUIDELINES: dict[str, Sequence[SurgeryRule]] = {
    "lumbar_microdiscectomy": [
        {
            "status": "acute",
            "allowed_rpe": 0,
            "volume_multiplier": 0.0,
            "restrictions_en": "Weeks 1-6: Strictly walking only. No lifting > 5 lbs. Spinal neutral at all times.",
            "restrictions_ar": "الأسابيع 1-6: المشي فقط بشكل صارم. لا ترفع أوزاناً تزيد عن 5 أرطال. حافظ على استقامة العمود الفقري دائماً.",
        },
        {
            "status": "subacute",
            "allowed_rpe": 5,
            "volume_multiplier": 0.4,
            "restrictions_en": "Weeks 7-12: Core stabilization, bodyweight flat-back exercises only. No spinal flexion or rotation.",
            "restrictions_ar": "الأسابيع 7-12: تثبيت الجذع، تمارين بوزن الجسم مع استواء الظهر فقط. لا تثني العمود الفقري أو تدوره.",
        },
        {
            "status": "reintegration",
            "allowed_rpe": 6,
            "volume_multiplier": 0.7,
            "restrictions_en": "Weeks 12+: Cautious introduction of light axial load. Keep lumbar brace pattern.",
            "restrictions_ar": "الأسابيع 12+: إدخال حذر للأحمال المحورية الخفيفة. حافظ على نمط دعم العمود الفقري القطني.",
        },
    ],
    "acl_reconstruction": [
        {
            "status": "acute",
            "allowed_rpe": 3,
            "volume_multiplier": 0.2,
            "restrictions_en": "Weeks 1-4: Leg in extension brace. Upper body training allowed seated only. No lower body loading.",
            "restrictions_ar": "الأسابيع 1-4: الساق في دعامة التمديد. يسمح بتدريب الجزء العلوي من الجسم جلوساً فقط. لا تحميل على الجزء السفلي.",
        },
        {
            "status": "subacute",
            "allowed_rpe": 6,
            "volume_multiplier": 0.5,
            "restrictions_en": "Weeks 5-12: Closed-chain double leg loading only. Leg press allowable. No shearing forces or pivoting.",
            "restrictions_ar": "الأسابيع 5-12: تحميل ثنائي الساق بالمسار المغلق فقط. يسمح بضغط الرجلين. لا توجد قوى قص أو التواء.",
        },
        {
            "status": "reintegration",
            "allowed_rpe": 7,
            "volume_multiplier": 0.8,
            "restrictions_en": "Weeks 12-24: Linear running permitted, unilateral strength training. No pivoting, cutting or jumping.",
            "restrictions_ar": "الأسابيع 12-24: يسمح بالجري المستقيم، تدريب القوة أحادي الجانب. لا التواء أو قطع أو قفز.",
        },
    ],
    "rotator_cuff_repair": [
        {
            "status": "acute",
            "allowed_rpe": 0,
            "volume_multiplier": 0.0,
            "restrictions_en": "Weeks 1-6: Arm in sling. Passive range of motion only. No active upper body recruitment.",
            "restrictions_ar": "الأسابيع 1-6: الذراع في علاقة. نطاق حركة سلبي فقط. لا تمرين نشط للجزء العلوي من الجسم.",
        },
        {
            "status": "subacute",
            "allowed_rpe": 5,
            "volume_multiplier": 0.3,
            "restrictions_en": "Weeks 7-12: Active-assisted exercises. Light bands permitted. No overhead range or heavy load.",
            "restrictions_ar": "الأسابيع 7-12: تمارين بمساعدة نشطة. يسمح بأحزمة مقاومة خفيفة. لا حركات فوق الرأس أو أحمال ثقيلة.",
        },
        {
            "status": "reintegration",
            "allowed_rpe": 6,
            "volume_multiplier": 0.6,
            "restrictions_en": "Weeks 12+: Return to light pressing and pulling patterns below shoulder height.",
            "restrictions_ar": "الأسابيع 12+: العودة إلى أنماط الدفع والسحب الخفيفة أسفل مستوى ارتفاع الكتف.",
        },
    ],
}

# 4. English and Arabic Detailed Medical Guideline Warnings
# Provides clinical explanations for coaches and users.
CLINICAL_TRANSLATIONS: dict[str, dict[str, str]] = {
    "safety.urgent_symptoms": {
        "title_en": "Emergency Block - Urgent Symptoms",
        "title_ar": "إيقاف طارئ - أعراض حرجة",
        "desc_en": "Emergency physical symptoms detected. Exercise is unsafe. Consult a physician immediately.",
        "desc_ar": "تم اكتشاف أعراض جسدية طارئة. ممارسة الرياضة غير آمنة. استشر الطبيب فوراً.",
    },
    "safety.medical_clearance_required": {
        "title_en": "Professional Medical Clearance Required",
        "title_ar": "مطلوب فحص طبي معتمد",
        "desc_en": "Safety engines flagged a requirement for professional medical clearance before personalized exercise plans can be generated.",
        "desc_ar": "أشارت محركات السلامة إلى ضرورة الحصول على تصريح طبي معتمد قبل إعداد خطة تمرين مخصصة.",
    },
    "injury.exercise_exclusion": {
        "title_en": "Movement Pattern Restriction",
        "title_ar": "تقييد نمط الحركة",
        "desc_en": "Active localized injury requires exclusion of mechanical patterns loading the affected joint structures.",
        "desc_ar": "تتطلب الإصابة الموضعية النشطة استبعاد الأنماط الميكانيكية التي تضغط على بنية المفصل المصاب.",
    },
    "readiness.critical_low": {
        "title_en": "Prescribed Rest Day",
        "title_ar": "يوم راحة محدد",
        "desc_en": "Physical readiness score has dropped below the safety threshold (40). Absolute physiological rest required.",
        "desc_ar": "انخفضت درجة الجاهزية البدنية عن حد الأمان (40). مطلوب راحة فسيولوجية تامة.",
    },
    "readiness.low": {
        "title_en": "Volume & Intensity Auto-Regulation",
        "title_ar": "التنظيم التلقائي للحجم والشدة",
        "desc_en": "Accumulated physical strain detected. Automatically regulated load to prevent fatigue and support recovery.",
        "desc_ar": "تم اكتشاف إجهاد بدني متراكم. تنظيم تلقائي للحمل لمنع الإرهاق ودعم التعافي.",
    },
    "nutrition.extreme_deficit_risk": {
        "title_en": "Caloric Target Override",
        "title_ar": "تجاوز السعرات الحرارية المستهدفة",
        "desc_en": "Unsafe deficit targets detected. Safety override applied to maintain metabolic health and skeletal muscle mass.",
        "desc_ar": "تم رصد عجز حراري غير آمن. تم تطبيق تجاوز الأمان للحفاظ على صحة التمثيل الغذائي والكتلة العضلية.",
    },
}
