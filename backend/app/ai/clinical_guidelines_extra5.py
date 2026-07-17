"""
Clinical Guidelines Extra Part 5 and Muscle Physiology Manual for RAHFIT AI Decision Engine.
This module provides comprehensive muscle fiber recruitment guidelines, bioenergetics system training parameters,
and cognitive readiness drills to support explainable AI and athletic decisions.
"""

from typing import TypedDict


class BioenergeticSystem(TypedDict):
    system_name: str
    primary_fuel: str
    duration_limit_seconds: int
    intensity_range_percent: str
    recovery_ratio: str
    recommended_intervals_en: str
    recommended_intervals_ar: str


BIOENERGETICS_SYSTEM_TRAINING: dict[str, BioenergeticSystem] = {
    "phosphagen_system": {
        "system_name": "ATP-CP (Phosphagen) System",
        "primary_fuel": "Intracellular ATP and Creatine Phosphate",
        "duration_limit_seconds": 10,
        "intensity_range_percent": "95-100% of maximum power",
        "recovery_ratio": "1:12 to 1:20 rest-to-work ratio",
        "recommended_intervals_en": "5-10 second sprints or heavy explosive lifts with 2-3 minutes complete rest between repetitions.",
        "recommended_intervals_ar": "سبرنتات من 5 إلى 10 ثوانٍ أو رفع أوزان انفجارية ثقيلة مع راحة كاملة لمدة 2-3 دقائق بين التكرارات.",
    },
    "glycolytic_system": {
        "system_name": "Anaerobic Lactic (Glycolytic) System",
        "primary_fuel": "Blood glucose and muscle glycogen",
        "duration_limit_seconds": 90,
        "intensity_range_percent": "75-90% of maximum effort",
        "recovery_ratio": "1:3 to 1:5 rest-to-work ratio",
        "recommended_intervals_en": "30-60 second high-intensity intervals (e.g., 400m sprint) with 2-3 minutes active rest.",
        "recommended_intervals_ar": "فترات عالية الشدة من 30 إلى 60 ثانية (مثل سبرنت 400 متر) مع دقيقتين إلى 3 دقائق من الراحة النشطة.",
    },
    "oxidative_system": {
        "system_name": "Aerobic (Oxidative) System",
        "primary_fuel": "Fatty acids, carbohydrates, and amino acids",
        "duration_limit_seconds": 7200,
        "intensity_range_percent": "40-70% of maximum VO2",
        "recovery_ratio": "1:1 or 1:2 rest-to-work ratio",
        "recommended_intervals_en": "Continuous low-intensity steady-state (LISS) exercise for 30-120 minutes, or aerobic intervals.",
        "recommended_intervals_ar": "تمارين مستمرة منخفضة الشدة وثابتة الحالة (LISS) لمدة 30-120 دقيقة، أو فترات هوائية.",
    },
}

MUSCLE_FIBER_RECRUITMENT: dict[str, dict[str, str]] = {
    "size_principle": {
        "en": "Henneman's Size Principle states that motor units are recruited in an orderly fashion from smallest to largest. Low-force requirements recruit slow-twitch (Type I) fibers first. Progressive load or high-velocity requirements recruit fast-twitch (Type IIa and IIx) fibers.",
        "ar": "ينص مبدأ حجم هينمان على أن الوحدات الحركية يتم تجنيدها بشكل منظم من الأصغر إلى الأكبر. متطلبات القوة المنخفضة تجند الألياف بطيئة الانقباض (النوع الأول) أولاً. بينما تجند الأحمال التدريجية أو متطلبات السرعة العالية الألياف سريعة الانقباض (النوع IIa و IIx).",
    },
    "rate_coding": {
        "en": "Rate coding refers to the frequency of motor unit firing. Increasing firing frequency increases total muscular force production. Critical during peak power and explosive strength movements.",
        "ar": "يشير ترميز المعدل إلى تردد إطلاق الوحدات الحركية. تؤدي زيادة تردد الإطلاق إلى زيادة إجمالي إنتاج القوة العضلية. أمر بالغ الأهمية أثناء ذروة القوة وحركات القوة الانفجارية.",
    },
    "mechanical_tension": {
        "en": "Mechanical tension is the primary driver of exercise-induced muscle hypertrophy. It occurs when a muscle fiber experiences stretch under load, activating focal adhesion complexes and downstream signaling pathways.",
        "ar": "التوتر الميكانيكي هو المحرك الأساسي لتضخم العضلات الناتج عن التمرين. يحدث عندما تتعرض الألياف العضلية للتمدد تحت الحمل، مما ينشط معقدات الالتصاق البؤري ومسارات الإشارات اللاحقة.",
    },
}
