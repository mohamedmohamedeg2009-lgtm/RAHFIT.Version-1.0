"""
Clinical Guidelines Data and Reference Manual for RAHFIT AI Decision Engine.
This module provides comprehensive reference data, safety warnings, Arabic and English translations,
and specific exercise guidelines for chronic conditions, acute injuries, and surgical recovery.
Used to support explainable AI justifications and clinical decision validation.
"""

from collections.abc import Sequence
from typing import TypedDict


class ClinicalGuideline(TypedDict):
    condition: str
    absolute_contraindications: Sequence[str]
    relative_contraindications: Sequence[str]
    aerobic_guidelines_en: str
    aerobic_guidelines_ar: str
    resistance_guidelines_en: str
    resistance_guidelines_ar: str
    monitoring_requirements_en: str
    monitoring_requirements_ar: str
    emergency_triggers_en: str
    emergency_triggers_ar: str


class PhysicalTherapyProtocol(TypedDict):
    injury_name: str
    acute_phase_en: str
    acute_phase_ar: str
    subacute_phase_en: str
    subacute_phase_ar: str
    reintegration_phase_en: str
    reintegration_phase_ar: str
    contraindicated_movements: Sequence[str]
    allowable_rehab_exercises: Sequence[str]


CLINICAL_GUIDELINES: dict[str, ClinicalGuideline] = {
    "hypertension": {
        "condition": "Hypertension (High Blood Pressure)",
        "absolute_contraindications": [
            "Resting systolic BP > 180 mmHg",
            "Resting diastolic BP > 110 mmHg",
            "Uncontrolled cardiac arrhythmias",
        ],
        "relative_contraindications": [
            "Moderate to severe aortic stenosis",
            "Uncontrolled metabolic disease",
            "Severe cognitive impairment",
        ],
        "aerobic_guidelines_en": "Focus on moderate-intensity continuous aerobic exercise (40-60% VO2 reserve) such as brisk walking, cycling, or swimming for 30-60 minutes on most days of the week.",
        "aerobic_guidelines_ar": "التركيز على التمارين الهوائية المستمرة متوسطة الشدة (40-60٪ من احتياطي أكسجين الجسم) مثل المشي السريع، ركوب الدراجات، أو السباحة لمدة 30-60 دقيقة في معظم أيام الأسبوع.",
        "resistance_guidelines_en": "Avoid high-resistance static loading and the Valsalva maneuver. Focus on high-repetition, low-load dynamic resistance training (15-20 repetitions per set at RPE 5-7).",
        "resistance_guidelines_ar": "تجنب التحميل الثابت عالي المقاومة ومناورة فالسالفا. ركز على تدريبات المقاومة الديناميكية ذات التكرار العالي والحمل المنخفض (15-20 تكراراً لكل مجموعة بمعدل جهد محسوس 5-7).",
        "monitoring_requirements_en": "Measure blood pressure before and 5 minutes post-exercise. Terminate session if systolic BP exceeds 220 mmHg or diastolic BP exceeds 105 mmHg.",
        "monitoring_requirements_ar": "قس ضغط الدم قبل التمرين وبعده بـ 5 دقائق. أنهِ الجلسة إذا تجاوز ضغط الدم الانقباضي 220 ملم زئبق أو ضغط الدم الانبساطي 105 ملم زئبق.",
        "emergency_triggers_en": "Immediate cessation of exercise and medical referral if patient experiences chest pain, severe dyspnea, dizziness, or sudden neurological deficits.",
        "emergency_triggers_ar": "الإيقاف الفوري للتمرين والإحالة الطبية إذا شعر المريض بألم في الصدر، ضيق تنفس شديد، دوار، أو قصور عصبي مفاجئ.",
    },
    "type_2_diabetes": {
        "condition": "Type 2 Diabetes Mellitus",
        "absolute_contraindications": [
            "Active retinal hemorrhage or recent laser surgery",
            "Severe autonomic neuropathy with unstable vitals",
            "Ketones present in urine",
        ],
        "relative_contraindications": [
            "Severe peripheral neuropathy (requires non-weight-bearing modes)",
            "Unhealed foot ulcers",
            "Recent episode of severe hypoglycemia within 24 hours",
        ],
        "aerobic_guidelines_en": "Engage in 150 minutes per week of moderate to vigorous aerobic exercise, spread over at least 3 days with no more than 2 consecutive days without activity.",
        "aerobic_guidelines_ar": "ممارسة 150 دقيقة أسبوعياً من التمارين الهوائية المعتدلة إلى الشديدة، موزعة على 3 أيام على الأقل مع عدم مرور أكثر من يومين متتاليين بدون نشاط.",
        "resistance_guidelines_en": "Progressive resistance training should be performed 2-3 times per week, targeting all major muscle groups (8-10 exercises, 1-3 sets of 10-15 repetitions at RPE 6-8).",
        "resistance_guidelines_ar": "يجب أداء تدريبات المقاومة التدريجية 2-3 مرات أسبوعياً، مستهدفة جميع المجموعات العضلية الرئيسية (8-10 تمارين، 1-3 مجموعات من 10-15 تكراراً بمعدل جهد محسوس 6-8).",
        "monitoring_requirements_en": "Monitor capillary blood glucose before, during, and after exercise. Consuming 15g of fast-acting carbohydrate if pre-exercise glucose is below 100 mg/dL.",
        "monitoring_requirements_ar": "راقب مستوى السكر في الدم قبل التمرين وأثناءه وبعده. تناول 15 جراماً من الكربوهيدرات سريعة الامتصاص إذا كان السكر قبل التمرين أقل من 100 ملغ/ديسيلتر.",
        "emergency_triggers_en": "Terminate session if blood glucose drops below 70 mg/dL or if symptoms of confusion, sweating, tremors, or loss of coordination occur.",
        "emergency_triggers_ar": "أنهِ الجلسة إذا انخواه سكر الدم عن 70 ملغ/ديسيلتر أو إذا ظهرت أعراض تشوش الذهن، التعرق المفرط، الرعشة، أو فقدان التوازن.",
    },
    "asthma": {
        "condition": "Asthma & Exercise-Induced Bronchoconstriction",
        "absolute_contraindications": [
            "Acute asthma exacerbation (resting wheezing or dyspnea)",
            "Peak expiratory flow < 60% of personal best",
            "Respiratory tract infection with systemic symptoms",
        ],
        "relative_contraindications": [
            "High exposure to environmental triggers (pollen, cold dry air)",
            "Poorly controlled baseline asthma",
        ],
        "aerobic_guidelines_en": "Perform aerobic exercise in warm, humid indoor environments. Progress from light walking to swimming or structured cycling. Limit high-ventilation running in cold climates.",
        "aerobic_guidelines_ar": "ممارسة التمارين الهوائية في بيئات داخلية دافئة ورطبة. تدرج من المشي الخفيف إلى السباحة أو ركوب الدراجات المنظم. تجنب الجري ذي التهوية العالية في الطقس البارد.",
        "resistance_guidelines_en": "Resistance training is well-tolerated. Ensure adequate rest periods between sets to prevent hyperventilation and broncho-spasm triggers (RPE 6-7).",
        "resistance_guidelines_ar": "تدريب المقاومة جيد التحمل. تأكد من فترات راحة كافية بين المجموعات لمنع زيادة تهوية الرئتين وتحفيز التشنج الشعبي (معدل جهد محسوس 6-7).",
        "monitoring_requirements_en": "Extend warm-up to 15 minutes to exploit the refractory period. Ensure rescue bronchodilator (albuterol) is present at the exercise station.",
        "monitoring_requirements_ar": "مدد الإحماء إلى 15 دقيقة للاستفادة من فترة الممانعة الطبيعية. تأكد من وجود موسع الشعب الهوائية الإسعافي (الالبوتيرول) في مكان التدريب.",
        "emergency_triggers_en": "Cease exercise immediately if wheezing, persistent coughing, chest tightness, or severe shortness of breath develops.",
        "emergency_triggers_ar": "أوقف التمرين فوراً إذا ظهر أزيز الصدر، أو السعال المستمر، أو ضيق الصدر، أو ضيق التنفس الشديد.",
    },
    "osteoarthritis": {
        "condition": "Osteoarthritis (Joint Degeneration)",
        "absolute_contraindications": [
            "Acute joint infection",
            "Severe, unmanaged joint effusion or swelling",
            "Acute mechanical block in the joint range of motion",
        ],
        "relative_contraindications": [
            "Severe joint instability",
            "Systemic inflammatory flare-up (e.g., rheumatoid arthritis crisis)",
        ],
        "aerobic_guidelines_en": "Low-impact aerobic conditioning is highly recommended. Focus on cycling, elliptical, water aerobics, or swimming to maintain cardiovascular fitness without joint loading.",
        "aerobic_guidelines_ar": "يوصى بشدة بالتمارين الهوائية منخفضة التأثير. ركز على ركوب الدراجة، جهاز الغزال الطائر، التمارين المائية، أو السباحة للحفاظ على اللياقة دون تحميل المفاصل.",
        "resistance_guidelines_en": "Isometric strength exercises around the affected joint during acute flare-ups. Progress to light dynamic loading (RPE 5-7). Emphasize strengthening supporting musculature.",
        "resistance_guidelines_ar": "تمارين القوة الثابتة حول المفصل المصاب أثناء النوبات الحادة. التدرج إلى التحميل الديناميكي الخفيف (معدل جهد محسوس 5-7). ركز على تقوية العضلات الداعمة.",
        "monitoring_requirements_en": "Monitor pain level. A mild increase in pain that subsides within 2 hours post-exercise is acceptable. Pain lasting > 24 hours indicates excessive loading.",
        "monitoring_requirements_ar": "راقب مستوى الألم. الزيادة الطفيفة في الألم التي تتلاشى خلال ساعتين بعد التمرين مقبولة. الألم المستمر لأكثر من 24 ساعة يشير إلى تحميل مفرط.",
        "emergency_triggers_en": "Stop exercise if sharp, stabbing pain, joint lock, or sudden swelling occurs during the session.",
        "emergency_triggers_ar": "أوقف التمرين إذا ظهر ألم حاد أو طاعن، أو قفل المفصل، أو تورم مفاجئ أثناء الجلسة.",
    },
    "chronic_kidney_disease": {
        "condition": "Chronic Kidney Disease (Stage 1-4)",
        "absolute_contraindications": [
            "Severe electrolyte imbalances (especially hyperkalemia)",
            "Unstable fluid overload status",
            "Severe renal osteodystrophy with risk of fracture",
        ],
        "relative_contraindications": [
            "Resting heart rate > 120 bpm",
            "Uncontrolled metabolic acidosis",
        ],
        "aerobic_guidelines_en": "Low to moderate intensity aerobic exercise (RPE 4-6). Walking, light cycling, or seated rowing. Avoid excessive volume to limit muscle catabolism.",
        "aerobic_guidelines_ar": "التمارين الهوائية منخفضة إلى متوسطة الشدة (معدل جهد محسوس 4-6). المشي، ركوب الدراجة الخفيف، أو التجديف جلوساً. تجنب الحجم المفرط للحد من هدم العضلات.",
        "resistance_guidelines_en": "Focus on high-repetition endurance patterns (12-15 reps). Avoid heavy single-rep efforts or Valsalva, which spike arterial blood pressure.",
        "resistance_guidelines_ar": "التركيز على أنماط تحمل التكرار العالي (12-15 تكراراً). تجنب محاولات التكرار الواحد الثقيل أو مناورة فالسالفا التي ترفع ضغط الدم الشرياني.",
        "monitoring_requirements_en": "Monitor hydration status meticulously. Do not exercise if severely dehydrated or exhibiting pitting edema in lower extremities.",
        "monitoring_requirements_ar": "راقب حالة الترطيب بدقة. لا تتمرن إذا كنت تعاني من الجفاف الشديد أو ظهور وذمة انطباعية في الأطراف السفلية.",
        "emergency_triggers_en": "Terminate session if patient experiences extreme muscle weakness, nausea, dizziness, or arrhythmias.",
        "emergency_triggers_ar": "أنهِ الجلسة إذا شعر المريض بضعف عضلي شديد، غثيان، دوار، أو اضطراب في ضربات القلب.",
    },
}

PHYSICAL_THERAPY_PROTOCOLS: dict[str, PhysicalTherapyProtocol] = {
    "patellar_tendinopathy": {
        "injury_name": "Patellar Tendinopathy (Jumper's Knee)",
        "acute_phase_en": "Prescribe 30-second isometric single-leg wall sits at 60-degree knee flexion, 4-5 sets, twice daily. Avoid rapid eccentric actions and jumping.",
        "acute_phase_ar": "تحديد تمرين الجلوس على الحائط أحادي الجانب الثابت لمدة 30 ثانية عند زاوية 60 درجة لثني الركبة، 4-5 مجموعات، مرتين يومياً. تجنب الحركات اللامركزية السريعة والقفز.",
        "subacute_phase_en": "Introduce heavy slow resistance (HSR) squats (3 seconds concentric, 4 seconds eccentric) up to 70% 1RM. Limit range of motion to painless zones.",
        "subacute_phase_ar": "إدخال تمارين القرفصاء ذات المقاومة الثقيلة البطيئة (3 ثوانٍ تركيزي، 4 ثوانٍ لامركزي) حتى 70٪ من أقصى وزن لتكرار واحد. حدد نطاق الحركة في المناطق الخالية من الألم.",
        "reintegration_phase_en": "Gradual progression to double-leg depth lands, shallow squat jumps on soft surfaces, and sports-specific decelerations under control.",
        "reintegration_phase_ar": "التدرج إلى الهبوط الثنائي من عمق مرتفع، وقفز القرفصاء الضحل على أسطح ناعمة، وتباطؤ الحركة الخاص بالرياضة تحت السيطرة.",
        "contraindicated_movements": ["deep_barbell_squat", "box_jump", "high_velocity_lunge"],
        "allowable_rehab_exercises": ["isometric_leg_press", "spanish_squat", "glute_bridge"],
    },
    "shoulder_impingement": {
        "injury_name": "Subacromial Shoulder Impingement",
        "acute_phase_en": "Focus on passive range of motion, scaption plane raises below 90 degrees, and isometric internal/external rotation with arm at side.",
        "acute_phase_ar": "التركيز على نطاق الحركة السلبي، ورفع الذراع في مستوى لوح الكتف أقل من 90 درجة، والدوران الداخلي/الخارجي الثابت مع إبقاء الذراع بجانب الجسم.",
        "subacute_phase_en": "Strengthen lower trapezius and serratus anterior using cable face pulls, prone Y-raises, and dumbbell scapular pushes. Limit overhead movements.",
        "subacute_phase_ar": "تقوية العضلات شبه المنحرفة السفلية والعضلة المنشارية الأمامية باستخدام تمارين السحب للوجه بالكابل، ورفرفة Y بوضعية الانبطاح، ودفع الكتف بالدمبل. حدد الحركات فوق الرأس.",
        "reintegration_phase_en": "Reintroduce overhead movements gradually using landmine presses, neutral grip dumbbell overhead presses, and dynamic rotator cuff drills.",
        "reintegration_phase_ar": "إعادة إدخال الحركات فوق الرأس تدريجياً باستخدام دفع المايندلاين، ودفع الكتف بالدمبل بقبضة محايدة، وتمارين الكفة المدورة الديناميكية.",
        "contraindicated_movements": [
            "barbell_bench_press",
            "behind_neck_lat_pulldown",
            "barbell_overhead_press",
        ],
        "allowable_rehab_exercises": ["dumbbell_floor_press", "cable_face_pull", "scapular_shrug"],
    },
    "lumbar_disc_herniation": {
        "injury_name": "Lumbar Disc Herniation / Bulge",
        "acute_phase_en": "Prescribe Mackenzie extension protocols, prone elbow propping, and core bracing. Strictly avoid spinal flexion, rotation, and seated loading.",
        "acute_phase_ar": "وصف بروتوكولات ماكنزي للتمديد، ودعم الكوع بوضعية الانبطاح، وتثبيت الجذع. تجنب ثني العمود الفقري والالتواء والتحميل جلوساً بشكل صارم.",
        "subacute_phase_en": "Introduce bird-dog, side plank, and dead-bug core stability patterns. Allow neutral spine standing leg press or bodyweight glute bridges.",
        "subacute_phase_ar": "إدخال أنماط ثبات الجذع (كلب الطير، اللوح الجانبي، الحشرة الميتة). يسمح بضغط الساق واقفاً مع استقامة العمود الفقري أو جسور الألوية بوزن الجسم.",
        "reintegration_phase_en": "Gradual progression to trap-bar deadlifts with high handles and chest-supported rows. Spine must remain neutral under strict coach monitoring.",
        "reintegration_phase_ar": "التدرج إلى رفعة الموت بقضيب التراب بمقابض مرتفعة والتجديف المدعوم للصدر. يجب أن يظل العمود الفقري مستوياً تحت مراقبة المدرب الصارمة.",
        "contraindicated_movements": [
            "conventional_deadlift",
            "seated_barbell_row",
            "barbell_back_squat",
        ],
        "allowable_rehab_exercises": ["plank", "bird_dog", "glute_bridge", "rack_pull_high_hang"],
    },
}

RECOVERY_TEMPLATE_GUIDELINES: dict[str, dict[str, str]] = {
    "optimal": {
        "en": "Physiological readiness is optimal. Excellent sleep duration and quality. Body is primed for muscle protein synthesis and progressive overload.",
        "ar": "الجاهزية الفسيولوجية مثالية. مدة وجودة نوم ممتازة. الجسم مهيأ لتركيب بروتين العضلات والزيادة التدريجية للحمل.",
    },
    "accumulated_fatigue": {
        "en": "Accumulated neuromuscular fatigue detected. CNS recovery is compromised. Reduce training volume by 20-30% and focus on active mobility.",
        "ar": "تم اكتشاف تعب عصبي عضلي متراكم. تعافي الجهاز العصبي المركزي متأثر. قلل حجم التدريب بنسبة 20-30٪ وركز على الحركة النشطة.",
    },
    "high_stress": {
        "en": "Cortisol levels are likely elevated due to lifestyle stress. Skeletal muscle recovery is slower. Limit training intensity to RPE 7 and extend cooldown.",
        "ar": "مستويات الكورتيزول مرتفعة غالباً بسبب ضغوط الحياة. تعافي العضلات الهيكلية أبطأ. حدد شدة التدريب عند معدل جهد 7 ومدد فترة التبريد.",
    },
    "critical_sleep": {
        "en": "Critical sleep deficit (<5 hours) restricts physical performance, decreases reaction time, and spikes injury risk. Active recovery or full rest is mandatory.",
        "ar": "عجز النوم الحرج (<5 ساعات) يقيد الأداء البدني، ويقلل وقت رد الفعل، ويرفع خطر الإصابة. الاستشفاء النشط أو الراحة التامة إلزامي.",
    },
    "severe_soreness": {
        "en": "Severe delayed onset muscle soreness (DOMS) indicates structural micro-damage. Avoid targeting sore muscle groups; prescribe flushing protocol (low load, high repetition).",
        "ar": "يشير ألم العضلات المتأخر الشديد (DOMS) إلى تلف بنيوي دقيق. تجنب استهداف المجموعات العضلية المؤلمة؛ حدد بروتوكول تحفيز الدورة الدموية (حمل خفيف، تكرار عالٍ).",
    },
}

CLINICAL_JUSTIFICATIONS: dict[str, dict[str, str]] = {
    "progressive_overload": {
        "en": "Consistent adherence and high readiness justify progression. Increasing volume by 5% to stimulate adaptive response.",
        "ar": "الالتزام المستمر والجاهزية العالية يبرران التقدم. زيادة حجم التمرين بنسبة 5٪ لتحفيز الاستجابة التكيفية.",
    },
    "injury_deload": {
        "en": "Active localized inflammatory markers require complete deload of the joint and neural pathway. Mechanical substitution applied.",
        "ar": "تتطلب مؤشرات الالتهاب الموضعية النشطة تخفيفاً كاملاً للحمل على المفصل والمسار العصبي. تم تطبيق الاستبدال ميكانيكي.",
    },
    "metabolic_preservation": {
        "en": "Metabolic and hormonal conservation protocol triggered. Ensuring caloric intake matches baseline resting metabolic rate to prevent endocrine dysfunction.",
        "ar": "تم تفعيل بروتوكول الحفاظ على التمثيل الغذائي والهرمونات. ضمان مطابقة السعرات الحرارية لمعدل الأيض الأساسي لمنع خلل الغدد الصماء.",
    },
    "deconditioning_prevention": {
        "en": "Deconditioning prevention logic active. Supplying safe minimum physical stimulus during restricted status to maintain neuromuscular pathways.",
        "ar": "منطق منع فقدان اللياقة نشط. تقديم الحد الأدنى الآمن من التحفيز البدني أثناء الحالة المقيدة للحفاظ على المسارات العصبية العضلية.",
    },
}

CARDIOVASCULAR_RISK_PROFILES: dict[str, dict[str, str]] = {
    "low_risk": {
        "en": "Asymptomatic individuals with fewer than two cardiovascular risk factors. Cleared for vigorous exercise without direct supervision.",
        "ar": "الأفراد الذين لا يعانون من أعراض ولديهم أقل من عاملين من عوامل خطر الإصابة بأمراض القلب والأوعية الدموية. مصرح لهم بالتمارين الشديدة دون إشراف مباشر.",
    },
    "moderate_risk": {
        "en": "Asymptomatic individuals with two or more risk factors. Cleared for moderate exercise; medical consultation recommended before initiating high-intensity regimens.",
        "ar": "الأفراد الذين لا يعانون من أعراض ولديهم عاملان أو أكثر من عوامل الخطر. مصرح لهم بالتمارين المعتدلة؛ يوصى باستشارة طبية قبل البدء في الأنظمة عالية الشدة.",
    },
    "high_risk": {
        "en": "Individuals with known cardiovascular, pulmonary, or metabolic disease, or one or more major signs and symptoms. Requires professional clearance.",
        "ar": "الأفراد المصابون بأمراض معروفة في القلب أو الرئتين أو الأيض، أو لديهم علامة أو عرض رئيسي واحد أو أكثر. يتطلب موافقة طبية معتمدة.",
    },
}

SPECIAL_POPULATIONS_PROTOCOLS: dict[str, dict[str, str]] = {
    "geriatric": {
        "title_en": "Geriatric Strength & Balance Protocol",
        "title_ar": "بروتوكول القوة والتوازن لكبار السن",
        "guideline_en": "Focus on multi-joint functional patterns. Emphasize unilateral balance and low-impact resistance training. Limit absolute axial load and strictly avoid explosive jumps. Target RPE 5-6.",
        "guideline_ar": "التركيز على الأنماط الوظيفية متعددة المفاصل. التأكيد على التوازن أحادي الجانب وتدريبات المقاومة منخفضة التأثير. تقييد الحمل المحوري المطلق وتجنب القفزات الانفجارية تماماً. معدل الجهد المحسوس المستهدف 5-6.",
    },
    "prenatal": {
        "title_en": "Pre-Natal (Pregnancy) Exercise Safety Protocol",
        "title_ar": "بروتوكول سلامة التمرين للحوامل",
        "guideline_en": "Avoid supine exercises after week 16 to prevent aortocaval compression. Limit core strain and heavy pelvic loading. Maintain RPE below 7. Keep body temperature regulated.",
        "guideline_ar": "تجنب التمارين على الظهر بعد الأسبوع 16 لمنع ضغط الوريد الأجوف الأبهر. تقييد إجهاد الجذع والتحميل الحوضي الثقيل. الحفاظ على معدل الجهد المحسوس أقل من 7. الحفاظ على تنظيم درجة حرارة الجسم.",
    },
    "postnatal": {
        "title_en": "Post-Natal Return-to-Play Progression",
        "title_ar": "تدرج العودة للنشاط بعد الولادة",
        "guideline_en": "Prioritize pelvic floor rehabilitation and deep transverse abdominis activation. Avoid high-impact running or jumping until pelvic stability is restored. Target RPE 4-6.",
        "guideline_ar": "إعطاء الأولوية لإعادة تأهيل قاع الحوض وتنشيط العضلة البطنية المستعرضة العميقة. تجنب الجري أو القفز عالي التأثير حتى استعادة استقرار الحوض. معدل الجهد المحسوس المستهدف 4-6.",
    },
    "adolescent": {
        "title_en": "Adolescent Athlete Development Framework",
        "title_ar": "إطار تطوير الرياضيين المراهقين",
        "guideline_en": "Prioritize movement quality, multi-directional coordination, and bodyweight skill acquisition. Restrict maximal lift attempts (1RM). Emphasize structural recovery and sports variety.",
        "guideline_ar": "إعطاء الأولوية لجودة الحركة، والتنسيق متعدد الاتجاهات، واكتساب مهارات وزن الجسم. تقييد محاولات الرفعة القصوى (1RM). التركيز على الاستشفاء البنيوي وتنوع الرياضات.",
    },
}

REHAB_EXERCISE_DATABASE: dict[str, dict[str, str]] = {
    "spanish_squat": {
        "name_en": "Spanish Squat (Banded)",
        "name_ar": "قرفصاء إسبانية (بالحزام المطاطي)",
        "setup_en": "Anchor a heavy resistance band to a secure post. Loop the band behind both knees, pull back until there is tension, and squat down keeping shins vertical.",
        "setup_ar": "ثبت حزام مقاومة ثقيل بعمود آمن. ضع الحزام خلف الركبتين، واسحب للخلف حتى يتشكل شد، ثم قم بالقرفصاء مع الحفاظ على عمودية الساقين.",
        "rehab_purpose_en": "Induces high quadriceps activation while reducing patellar tendon stress by maintaining a vertical shin angle.",
        "rehab_purpose_ar": "يؤدي إلى تنشيط عالٍ للعضلة رباعية الرؤوس مع تقليل الضغط على وتر الرضفة عن طريق الحفاظ على زاوية ساق عمودية.",
    },
    "cable_face_pull": {
        "name_en": "Cable Face Pull with External Rotation",
        "name_ar": "سحب كابل للوجه مع الدوران الخارجي",
        "setup_en": "Set a cable machine at upper chest height. Grab the rope with thumbs pointing back. Pull the rope toward your face while opening the hands outwards.",
        "setup_ar": "اضبط جهاز الكابل عند مستوى الصدر العلوي. امسك الحبل مع توجيه الإبهامين للخلف. اسحب الحبل نحو وجهك مع فتح اليدين للخارج.",
        "rehab_purpose_en": "Strengthens the posterior deltoid, rhomboids, and external rotator cuff muscles to correct shoulder biomechanics.",
        "rehab_purpose_ar": "يقوي العضلة الدالية الخلفية، المعينية، وعضلات الكفة المدورة الخارجية لتصحيح الميكانيكا الحيوية للكتف.",
    },
    "isometric_wall_sit": {
        "name_en": "Isometric Wall Sit",
        "name_ar": "الجلوس الثابت على الحائط",
        "setup_en": "Lean your back flat against a wall and slide down until knees are bent to 90 degrees or a pain-free angle. Hold the position under time control.",
        "setup_ar": "أسنِد ظهرك بشكل مستوٍ على حائط وانزلق لأسفل حتى تنثني الركبتان بزاوية 90 درجة أو زاوية خالية من الألم. حافظ على الوضعية تحت التحكم بالوقت.",
        "rehab_purpose_en": "Provides isometric loading to the knee extensors without joint motion, bypassing patellofemoral friction.",
        "rehab_purpose_ar": "يوفر تحميلاً ثابتاً لباسطات الركبة دون حركة المفصل، متجاوزاً الاحتكاك الرضفي الفخذي.",
    },
    "prone_cobra": {
        "name_en": "Prone Cobra (Spinal Extension)",
        "name_ar": "تمرين الكوبرا بوضعية الانبطاح (تمديد العمود الفقري)",
        "setup_en": "Lie face down. Lift your chest, shoulders, and arms off the floor while squeezing the shoulder blades together and rotating thumbs to the ceiling.",
        "setup_ar": "استلقِ على بطنك. ارفع صدرك وكتفيك وذراعيك عن الأرض مع ضم لوحي الكتف معاً وتدوير الإبهامين نحو السقف.",
        "rehab_purpose_en": "Strengthens lower traps and spinal erectors, promoting optimal thoracic extension and spinal alignment.",
        "rehab_purpose_ar": "يقوي العضلة شبه المنحرفة السفلية ومقومات العمود الفقري، مما يعزز التمدد الصدري المثالي واستقامة العمود الفقري.",
    },
    "tibialis_raise": {
        "name_en": "Tibialis Anterior Raise",
        "name_ar": "رفع العضلة الظنبوبية الأمامية",
        "setup_en": "Lean your back against a wall, place feet forward, and pull your toes up toward the shins while keeping the knees straight.",
        "setup_ar": "أسنِد ظهرك على حائط، وضع قدميك للأمام، واسحب أصابع قدميك لأعلى نحو الساقين مع الحفاظ على استقامة الركبتين.",
        "rehab_purpose_en": "Builds the tibialis anterior muscle to absorb ground impact and decrease patellofemoral pressure.",
        "rehab_purpose_ar": "يبني العضلة الظنبوبية الأمامية لامتصاص تأثير الصدمات على الأرض وتقليل الضغط الرضفي الفخذي.",
    },
}
