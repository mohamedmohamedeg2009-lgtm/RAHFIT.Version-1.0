"""
Clinical Guidelines Extra Part 7 and Muscle Physiology Manual Part 3 for RAHFIT AI Decision Engine.
This module provides additional recovery templates, motor unit synchronization guidelines,
and biomechanical assessment markers to support explainable AI and athletic decisions.
"""

from typing import TypedDict


class BiomechanicalImbalance(TypedDict):
    joint: str
    imbalance_pattern: str
    assessment_method_en: str
    assessment_method_ar: str
    corrective_exercise_en: str
    corrective_exercise_ar: str


BIOMECHANICAL_IMBALANCES: dict[str, BiomechanicalImbalance] = {
    "glenohumeral_joint": {
        "joint": "Glenohumeral (Shoulder) Joint",
        "imbalance_pattern": "Internal Rotation Dominance (Forward Rounded Shoulder)",
        "assessment_method_en": "Assess active internal vs external range of motion in 90-90 position.",
        "assessment_method_ar": "تقييم نطاق الحركة الداخلي مقابل الخارجي النشط في وضعية 90-90.",
        "corrective_exercise_en": "Dumbbell external rotation in scaption plane and stretch pectoralis minor.",
        "corrective_exercise_ar": "الدوران الخارجي بالدمبل في مستوى لوح الكتف وإطالة العضلة الصدرية الصغيرة.",
    },
    "hip_joint": {
        "joint": "Hip (Femoroacetabular) Joint",
        "imbalance_pattern": "Gluteus Medius Weakness (Trendelenburg Sign)",
        "assessment_method_en": "Observe pelvis level during single-leg stance or walking gait.",
        "assessment_method_ar": "ملاحظة مستوى الحوض أثناء الوقوف على ساق واحدة أو أثناء المشي.",
        "corrective_exercise_en": "Banded side-lying clam shells and single-leg box step-downs.",
        "corrective_exercise_ar": "تمرين المحار الجانبي بحزام المقاومة وهبوط الخطوة أحادي الجانب من الصندوق.",
    },
    "talocrural_joint": {
        "joint": "Talocrural (Ankle) Joint",
        "imbalance_pattern": "Limited Dorsiflexion Range",
        "assessment_method_en": "Half-kneeling wall touch test, measuring max distance from big toe to wall.",
        "assessment_method_ar": "اختبار لمس الحائط بوضعية نصف الركوع، قياس المسافة القصوى من إصبع القدم الكبير للحائط.",
        "corrective_exercise_en": "Self-myofascial release of soleus and banded ankle distraction.",
        "corrective_exercise_ar": "التحرير الذاتي اللفافي العضلي لعضلة النعلية وتمديد الكاحل بحزام المقاومة.",
    },
}
