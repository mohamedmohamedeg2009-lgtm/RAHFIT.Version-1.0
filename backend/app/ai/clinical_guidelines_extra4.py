"""
Clinical Guidelines Extra Part 4 and Sleep Biology Manual for RAHFIT AI Decision Engine.
This module provides comprehensive sleep hygiene guidelines, amino acid recovery thresholds,
and soft-tissue rehabilitation protocols to support explainable AI and athletic decisions.
"""

from typing import TypedDict


class SleepRule(TypedDict):
    parameter: str
    target: str
    guideline_en: str
    guideline_ar: str
    physiological_impact_en: str
    physiological_impact_ar: str


SLEEP_BIOLOGY_RULES: dict[str, SleepRule] = {
    "circadian_alignment": {
        "parameter": "Circadian Phase Synchronization",
        "target": "Consistent wake times within a 30-minute window daily.",
        "guideline_en": "Expose eyes to 10,000 lux of sunlight within 30 minutes of waking. Avoid blue light exposure after 9:00 PM.",
        "guideline_ar": "عرض العينين لـ 10,000 لوكس من ضوء الشمس في غضون 30 دقيقة من الاستيقاظ. تجنب التعرض للضوء الأزرق بعد الساعة 9:00 مساءً.",
        "physiological_impact_en": "Optimizes cortisol awakening response (CAR) and regulates nocturnal melatonin secretion.",
        "physiological_impact_ar": "يحسن استجابة استيقاظ الكورتيزول (CAR) وينظم إفراز الميلاتونين الليلي.",
    },
    "sleep_pressure": {
        "parameter": "Adenosine Accumulation Management",
        "target": "Sufficient sleep pressure to ensure rapid sleep onset (under 15 minutes).",
        "guideline_en": "Avoid caffeine intake within 10 hours of planned bedtime. Engage in moderate physical activity during the day.",
        "guideline_ar": "تجنب تناول الكافيين في غضون 10 ساعات من وقت النوم المخطط له. مارس نشاطاً بدنياً معتدلاً خلال اليوم.",
        "physiological_impact_en": "Prevents competitive antagonism of adenosine receptors, allowing normal homeostatic sleep drive.",
        "physiological_impact_ar": "يمنع التضاد التنافسي لمستقبلات الأدينوزين، مما يسمح بالدافع الطبيعي للنوم المتوازن.",
    },
    "temperature_drop": {
        "parameter": "Thermoregulation Control",
        "target": "Core body temperature drop of 1 degree Celsius.",
        "guideline_en": "Maintain bedroom temperature at 18-20 degrees Celsius. Take a warm shower 90 minutes before sleep.",
        "guideline_ar": "الحفاظ على درجة حرارة غرفة النوم عند 18-20 درجة مئوية. خذ حماماً دافئاً قبل النوم بـ 90 دقيقة.",
        "physiological_impact_en": "Facilitates peripheral vasodilation, acceleration of core cooling, and rapid entry into deep sleep stages.",
        "physiological_impact_ar": "يسهل توسع الأوعية الطرفية، وتسريع التبريد الأساسي للجسم، والدخول السريع في مراحل النوم العميق.",
    },
}

AMINO_ACID_THRESHOLD_GUIDELINES: dict[str, dict[str, str]] = {
    "leucine_trigger": {
        "en": "Consume at least 3.0g of leucine per meal to saturate the Sestrin2 sensor and trigger maximal mTORC1 activation for muscle protein synthesis.",
        "ar": "تناول ما لا يقل عن 3.0 جرام من الليوسين لكل وجبة لإشباع مستشعر Sestrin2 وتحفيز تنشيط mTORC1 الأقصى لبناء بروتين العضلات.",
    },
    "pre_sleep_casein": {
        "en": "Consume 40g of slow-digesting micellar casein protein 30 minutes before sleep to maintain elevated amino acid levels and prevent nocturnal muscle catabolism.",
        "ar": "تناول 40 جراماً من بروتين الكازين بطيء الهضم قبل النوم بـ 30 دقيقة للحفاظ على مستويات مرتفعة من الأحماض الأمينية ومنع هدم العضلات أثناء الليل.",
    },
    "essential_amino_acids": {
        "en": "Ensure daily intake contains all 9 essential amino acids in a balanced ratio. Recommended baseline intake of 1.6-2.2g of total protein per kg of body mass.",
        "ar": "تأكد من أن المدخول اليومي يحتوي على جميع الأحماض الأمينية الـ 9 الأساسية بنسبة متوازنة. المدخول الأساسي الموصى به هو 1.6-2.2 جرام من إجمالي البروتين لكل كيلوغرام من وزن الجسم.",
    },
}

SOFT_TISSUE_REHAB_PROTOCOLS: dict[str, dict[str, str]] = {
    "plantar_fasciitis": {
        "en": "Perform Rathleff protocols: single-leg calf raises with a towel rolled under the toes to engage the windlass mechanism. 3 sets of 12 reps, every other day.",
        "ar": "أداء بروتوكولات راثليف: رفع ربلة الساق أحادي الجانب مع وضع منشفة ملفوفة تحت أصابع القدم لتشغيل آلية الرافعة. 3 مجموعات من 12 تكراراً، يوماً بعد يوم.",
    },
    "lateral_epicondylitis": {
        "en": "Prescribe Tyler Twist protocols using a flexible rubber bar to induce eccentric wrist extension loading. Focus on high repetition, pain-free range.",
        "ar": "وصف بروتوكولات تايلر تويست باستخدام شريط مطاطي مرن لتحفيز تحميل تمديد المعصم اللامركزي. التركيز على التكرار العالي، والنطاق الخالي من الألم.",
    },
    "hamstring_strain": {
        "en": "Progressive eccentric loading using Nordic hamstring curls and slider curls. Ensure zero pain on palpation and symmetrical active hip flexion prior to running.",
        "ar": "تحميل لامركزي تدريجي باستخدام تمارين نورديك لربلة الساق وتمارين الانزلاق. تأكد من عدم وجود ألم عند اللمس وتماثل ثني الورك النشط قبل الجري.",
    },
}
