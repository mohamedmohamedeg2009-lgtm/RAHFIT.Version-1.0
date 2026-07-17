"""
Clinical Guidelines Extra Part 6 and Muscle Physiology Manual Part 2 for RAHFIT AI Decision Engine.
This module provides additional recovery templates, motor unit synchronization guidelines,
and biomechanical assessment markers to support explainable AI and athletic decisions.
"""

from typing import TypedDict


class MuscleFiberRecovery(TypedDict):
    fiber_type: str
    fatigue_threshold: str
    recovery_duration_hours: int
    optimal_intensity_percent: str
    rehab_focus_en: str
    rehab_focus_ar: str


MUSCLE_FIBER_RECOVERY_MODELS: dict[str, MuscleFiberRecovery] = {
    "type_i_slow_twitch": {
        "fiber_type": "Type I (Slow-Twitch, Oxidative)",
        "fatigue_threshold": "High fatigue resistance, slow contraction velocity.",
        "recovery_duration_hours": 24,
        "optimal_intensity_percent": "40-60% 1RM",
        "rehab_focus_en": "Focus on high frequency, dynamic endurance, postural control, and cardiovascular efficiency.",
        "rehab_focus_ar": "التركيز على التردد العالي، التحمل الديناميكي، التحكم في القوام، وكفاءة القلب والأوعية الدموية.",
    },
    "type_iia_fast_twitch": {
        "fiber_type": "Type IIa (Fast-Twitch, Glycolytic-Oxidative)",
        "fatigue_threshold": "Moderate fatigue resistance, high contraction velocity.",
        "recovery_duration_hours": 48,
        "optimal_intensity_percent": "60-80% 1RM",
        "rehab_focus_en": "Focus on hypertrophy, sustained power output, moderate rest intervals, and progressive resistance loading.",
        "rehab_focus_ar": "التركيز على تضخم العضلات، إنتاج القوة المستمر، فترات الراحة المعتدلة، وتحميل المقاومة التدريجي.",
    },
    "type_iix_fast_twitch": {
        "fiber_type": "Type IIx (Fast-Twitch, Glycolytic)",
        "fatigue_threshold": "Low fatigue resistance, extremely high contraction velocity.",
        "recovery_duration_hours": 72,
        "optimal_intensity_percent": "85-100% 1RM",
        "rehab_focus_en": "Focus on absolute strength, explosive power, neural synchronization, and complete recovery intervals.",
        "rehab_focus_ar": "التركيز على القوة المطلقة، القوة الانفجارية، التزامن العصبي، وفترات الاستشفاء الكاملة.",
    },
}

MOTOR_UNIT_SYNCHRONIZATION: dict[str, dict[str, str]] = {
    "intermuscular_coordination": {
        "en": "Intermuscular coordination refers to the synergistic action of multiple muscles during complex movements. Prescribing multi-joint compound exercises optimizes kinetic chain efficiency.",
        "ar": "يشير التنسيق بين العضلات إلى العمل التآزري لعضلات متعددة أثناء الحركات المعقدة. يؤدي تحديد التمارين المركبة متعددة المفاصل إلى تحسين كفاءة السلسلة الحركية.",
    },
    "intramuscular_coordination": {
        "en": "Intramuscular coordination refers to the synchronization and rate coding within a single muscle. High-force loading stimulates motor unit firing rate and synchronization.",
        "ar": "يشير التنسيق داخل العضلة إلى التزامن وترميز المعدل داخل عضلة واحدة. يحفز تحميل القوة العالية معدل إطلاق الوحدات الحركية وتزامنها.",
    },
}
