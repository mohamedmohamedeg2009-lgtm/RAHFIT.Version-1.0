"""
Clinical Guidelines Extra Part 2 and Assessment Manual for RAHFIT AI Decision Engine.
This module provides comprehensive orthopedic assessment tests, muscle imbalance markers,
and sports-specific return-to-play criteria to support explainable AI and athletic decisions.
"""

from typing import TypedDict


class OrthopedicTest(TypedDict):
    test_name: str
    target_structure: str
    procedure_en: str
    procedure_ar: str
    positive_indicators_en: str
    positive_indicators_ar: str
    recommendation_if_positive_en: str
    recommendation_if_positive_ar: str


ORTHOPEDIC_ASSESSMENTS: dict[str, OrthopedicTest] = {
    "neers_test": {
        "test_name": "Neer's Impingement Test",
        "target_structure": "Subacromial space, supraspinatus tendon",
        "procedure_en": "The coach stabilizes the scapula and vertically raises the user's arm in internal rotation and pronation.",
        "procedure_ar": "يقوم المدرب بتثبيت لوح الكتف ويرفع ذراع المستخدم عمودياً في حالة دوران داخلي وبطح.",
        "positive_indicators_en": "Pain in the anterior-lateral aspect of the shoulder at terminal flexion range.",
        "positive_indicators_ar": "ألم في الجانب الأمامي الجانبي للكتف عند النطاق النهائي للثني.",
        "recommendation_if_positive_en": "Restrict vertical shoulder movements. Prescribe landmine presses and avoid behind-neck exercises.",
        "recommendation_if_positive_ar": "تقييد حركات الكتف العمودية. تحديد ضغط المايندلاين وتجنب التمارين خلف الرقبة.",
    },
    "lachman_test": {
        "test_name": "Lachman Test (ACL Integrity)",
        "target_structure": "Anterior Cruciate Ligament",
        "procedure_en": "Place knee at 30 degrees flexion. Stabilize the femur and translate the tibia anteriorly to assess laxity.",
        "procedure_ar": "ضع الركبة عند 30 درجة من الثني. قم بتثبيت الفخذ وحرك قصبة الساق للأمام لتقييم الارتخاء.",
        "positive_indicators_en": "Soft endpoint or excessive anterior translation of the tibia compared to the contralateral leg.",
        "positive_indicators_ar": "نهاية حركة لينة أو حركة أمامية مفرطة لقصبة الساق مقارنة بالساق الأخرى.",
        "recommendation_if_positive_en": "Absolute ban on knee pivoting, jumping, and deep squats. Require orthopedic doctor consultation.",
        "recommendation_if_positive_ar": "منع تام لالتواء الركبة والقفز والقرفصاء العميق. يتطلب استشارة طبيب العظام.",
    },
    "thomas_test": {
        "test_name": "Thomas Test (Hip Flexion Length)",
        "target_structure": "Iliopsoas, rectus femoris, tensor fasciae latae",
        "procedure_en": "User lies supine at edge of table, hugging one knee to chest. Observe if the opposite thigh remains flat on table.",
        "procedure_ar": "يستلقي المستخدم على ظهره عند حافة الطاولة، ويضم ركبة واحدة إلى صدره. لاحظ ما إذا كان الفخذ المقابل يظل مستوياً على الطاولة.",
        "positive_indicators_en": "Thigh remains elevated off the table, indicating hip flexor tightness or contracture.",
        "positive_indicators_ar": "يظل الفخذ مرتفعاً عن الطاولة، مما يشير إلى ضيق أو قصر في عضلات الورك القابضة.",
        "recommendation_if_positive_en": "Prescribe active stretching for iliopsoas. Perform glute bridge activation prior to lower body training.",
        "recommendation_if_positive_ar": "وصف تمارين الإطالة النشطة للعضلة الحرقفية الخصرية. أداء تمارين تنشيط الألوية قبل تدريب الجزء السفلي.",
    },
}

MUSCLE_IMBALANCE_INDICATORS: dict[str, dict[str, str]] = {
    "upper_crossed_syndrome": {
        "en": "Tight upper trapezius, levator scapulae, and pectoralis major, combined with weak deep neck flexors and lower serratus anterior. Results in forward head posture.",
        "ar": "ضيق العضلة شبه المنحرفة العلوية، رافعة الكتف، والصدرية الكبرى، بالتزامن مع ضعف عضلات الرقبة القابضة العميقة والمنشارية الأمامية السفلية. يؤدي إلى وضعية الرأس للأمام.",
    },
    "lower_crossed_syndrome": {
        "en": "Tight iliopsoas and erector spinae, combined with weak gluteals and rectus abdominis. Results in anterior pelvic tilt and increased lumbar lordosis.",
        "ar": "ضيق العضلة الحرقفية الخصرية ومقومات العمود الفقري، بالتزامن مع ضعف الألوية والعضلة البطنية المستقيمة. يؤدي إلى ميل الحوض الأمامي وزيادة القعس القطني.",
    },
    "pronator_distortion_syndrome": {
        "en": "Tight gastrocnemius, soleus, hip adductors, and IT band, combined with weak tibialis anterior, gluteus medius, and vastus medialis. Results in knee valgus during squat.",
        "ar": "ضيق العضلتين التوأمية والنعلية، ومقربات الورك، والشريط الحرقفي الظنبوبي، بالتزامن مع ضعف العضلة الظنبوبية الأمامية، الألوية الوسطى، والمتسعة الإنسية. يؤدي إلى تقوس الركبة للداخل أثناء القرفصاء.",
    },
}

SPORTS_RETURN_TO_PLAY_CRITERIA: dict[str, dict[str, str]] = {
    "knee_rehab_exit": {
        "en": "Requires limb symmetry index (LSI) > 90% in single-leg hop tests, pain-free full range of motion, and zero joint effusion post-activity.",
        "ar": "يتطلب مؤشر تماثل الأطراف (LSI) بنسبة > 90٪ في اختبارات القفز على ساق واحدة، ونطاق حركة كامل خالٍ من الألم، وعدم وجود تورم في المفصل بعد النشاط.",
    },
    "shoulder_rehab_exit": {
        "en": "Requires symmetrical internal and external rotation strength, pain-free dynamic pushup, and cleared overhead Y-press at bodyweight load.",
        "ar": "يتطلب قوة متماثلة في الدوران الداخلي والخارجي، وتمرين ضغط ديناميكي خالٍ من الألم، وأداء ضغط Y فوق الرأس بحمل وزن الجسم.",
    },
    "lumbar_rehab_exit": {
        "en": "Requires painless isometric plank hold for 90 seconds, side plank for 60 seconds, and dynamic carry patterns without spinal deviation.",
        "ar": "يتطلب ثبات لوح ثابت خالٍ من الألم لمدة 90 ثانية، ولوح جانبي لمدة 60 ثانية، وأنماط حمل ديناميكية دون انحراف العمود الفقري.",
    },
}
