import type { Locale } from "../contexts/LocaleContext";
import type {
  AssessmentCategory,
  AssessmentQuestion,
  QuestionOption,
  RiskLevel,
  SafetyStatus,
} from "../types/assessment";

export const assessmentCopy = {
  en: {
    brand: "RAHFIT AI",
    assessment: "Smart Assessment",
    welcomeEyebrow: "Your plan starts with understanding you",
    welcomeTitle: "A smarter path begins with the right questions.",
    welcomeBody:
      "This adaptive assessment learns about your goals, routine, experience, equipment, and safety needs. You will only see questions relevant to you.",
    start: "Start assessment",
    starting: "Preparing your assessment",
    privacy: "Your answers stay private and are used to personalize your RAHFIT experience.",
    adaptive: "Adaptive",
    adaptiveBody: "The next question is selected from your previous answers.",
    safe: "Safety first",
    safeBody: "Deterministic safety checks always take priority.",
    resumable: "Save and resume",
    resumableBody: "Every answer is saved so you can continue later.",
    resumeTitle: "Welcome back. Your assessment is waiting.",
    resumeBody: "Continue from the exact point where you stopped.",
    continueAssessment: "Continue assessment",
    startOverNotice: "Your saved answers and progress are ready.",
    completion: "Assessment completion",
    readiness: "Readiness score",
    category: "Category",
    previous: "Previous",
    next: "Save and continue",
    skip: "Skip for now",
    saving: "Saving your answer",
    saved: "Answer saved",
    required: "Required",
    optional: "Optional",
    yes: "Yes",
    no: "No",
    selectOne: "Select one option",
    selectMany: "Select all that apply",
    answerRequired: "Choose or enter an answer to continue.",
    review: "Review your assessment",
    reviewBody: "Check your answers and readiness before completing the assessment.",
    answers: "Your answers",
    missingCategories: "Missing categories",
    noMissingCategories: "All required categories are complete.",
    edit: "Edit",
    complete: "Complete assessment",
    completing: "Completing assessment",
    stopComplete: "Completion is paused until the safety restriction is resolved.",
    completedEyebrow: "Assessment complete",
    completedTitle: "Your foundation is ready.",
    completedBody:
      "RAHFIT now has the structured context needed to personalize your next experience safely.",
    continueDashboard: "Continue to Dashboard",
    summary: "Assessment summary",
    goals: "Goals",
    lifestyle: "Lifestyle",
    medical: "Medical considerations",
    equipment: "Equipment",
    experience: "Experience",
    trainingReadiness: "Training readiness",
    risk: "Risk level",
    loadError: "We could not load your assessment. Please try again.",
    retry: "Try again",
    theme: "Toggle color theme",
    language: "العربية",
    signOut: "Sign out",
    loading: "Loading assessment",
    step: "Question",
    of: "of",
    safetySafeTitle: "No safety restriction detected",
    safetyCautionTitle: "Continue with caution",
    safetyStopTitle: "Safety pause required",
    notAnswered: "Not answered",
  },
  ar: {
    brand: "RAHFIT AI",
    assessment: "التقييم الذكي",
    welcomeEyebrow: "خطتك تبدأ بفهمك جيدًا",
    welcomeTitle: "الطريق الأذكى يبدأ بالأسئلة الصحيحة.",
    welcomeBody:
      "يتعرّف هذا التقييم المتكيّف على أهدافك وروتينك وخبرتك ومعداتك واحتياجات السلامة، ولن يعرض إلا الأسئلة المناسبة لك.",
    start: "ابدأ التقييم",
    starting: "جارٍ تجهيز تقييمك",
    privacy: "تبقى إجاباتك خاصة وتُستخدم لتخصيص تجربتك داخل RAHFIT.",
    adaptive: "متكيّف",
    adaptiveBody: "يتم اختيار السؤال التالي بناءً على إجاباتك السابقة.",
    safe: "السلامة أولًا",
    safeBody: "فحوص السلامة الحتمية لها الأولوية دائمًا.",
    resumable: "حفظ واستكمال",
    resumableBody: "تُحفظ كل إجابة لتتمكن من المتابعة لاحقًا.",
    resumeTitle: "مرحبًا بعودتك، تقييمك في انتظارك.",
    resumeBody: "تابع من النقطة نفسها التي توقفت عندها.",
    continueAssessment: "استكمل التقييم",
    startOverNotice: "إجاباتك وتقدمك المحفوظان جاهزان.",
    completion: "نسبة اكتمال التقييم",
    readiness: "درجة الجاهزية",
    category: "الفئة",
    previous: "السابق",
    next: "احفظ وتابع",
    skip: "تخطَّ الآن",
    saving: "جارٍ حفظ إجابتك",
    saved: "تم حفظ الإجابة",
    required: "مطلوب",
    optional: "اختياري",
    yes: "نعم",
    no: "لا",
    selectOne: "اختر إجابة واحدة",
    selectMany: "اختر كل ما ينطبق",
    answerRequired: "اختر أو أدخل إجابة للمتابعة.",
    review: "راجع تقييمك",
    reviewBody: "راجع إجاباتك ودرجة جاهزيتك قبل إكمال التقييم.",
    answers: "إجاباتك",
    missingCategories: "الفئات الناقصة",
    noMissingCategories: "اكتملت جميع الفئات المطلوبة.",
    edit: "تعديل",
    complete: "إكمال التقييم",
    completing: "جارٍ إكمال التقييم",
    stopComplete: "تم إيقاف الإكمال حتى معالجة قيد السلامة.",
    completedEyebrow: "اكتمل التقييم",
    completedTitle: "أصبح أساس رحلتك جاهزًا.",
    completedBody: "يمتلك RAHFIT الآن المعلومات المنظمة اللازمة لتخصيص تجربتك التالية بأمان.",
    continueDashboard: "المتابعة إلى لوحة التحكم",
    summary: "ملخص التقييم",
    goals: "الأهداف",
    lifestyle: "نمط الحياة",
    medical: "الاعتبارات الطبية",
    equipment: "المعدات",
    experience: "الخبرة",
    trainingReadiness: "جاهزية التدريب",
    risk: "مستوى الخطورة",
    loadError: "تعذر تحميل تقييمك. حاول مرة أخرى.",
    retry: "حاول مرة أخرى",
    theme: "تبديل مظهر الألوان",
    language: "English",
    signOut: "تسجيل الخروج",
    loading: "جارٍ تحميل التقييم",
    step: "السؤال",
    of: "من",
    safetySafeTitle: "لم يتم اكتشاف قيد سلامة",
    safetyCautionTitle: "تابع بحذر",
    safetyStopTitle: "يلزم التوقف لأسباب تتعلق بالسلامة",
    notAnswered: "لم تتم الإجابة",
  },
} as const;

const categoryArabic: Record<AssessmentCategory, string> = {
  personal_information: "المعلومات الشخصية",
  goals: "الأهداف",
  lifestyle: "نمط الحياة",
  medical: "الصحة والسلامة",
  injuries: "الإصابات",
  sleep: "النوم",
  stress: "الضغط النفسي",
  experience: "الخبرة",
  equipment: "المعدات",
  nutrition: "التغذية",
  recovery: "الاستشفاء",
  sports: "الرياضة",
  football: "كرة القدم",
  goalkeeper: "حراسة المرمى",
};

const categoryEnglish: Record<AssessmentCategory, string> = {
  personal_information: "Personal information",
  goals: "Goals",
  lifestyle: "Lifestyle",
  medical: "Health and safety",
  injuries: "Injuries",
  sleep: "Sleep",
  stress: "Stress",
  experience: "Experience",
  equipment: "Equipment",
  nutrition: "Nutrition",
  recovery: "Recovery",
  sports: "Sports",
  football: "Football",
  goalkeeper: "Goalkeeper",
};

interface QuestionTranslation {
  title: string;
  description?: string;
  options?: Record<string, string>;
}

const arabicQuestions: Record<string, QuestionTranslation> = {
  age: { title: "ما عمرك؟" },
  user_gender: {
    title: "ما خيار النوع الذي ينبغي أن يستخدمه التقييم؟",
    description: "تُستخدم هذه الإجابة الاختيارية فقط لإظهار أقسام التقييم المناسبة.",
    options: {
      male: "ذكر",
      female: "أنثى",
      another_identity: "هوية أخرى",
      prefer_not_to_say: "أفضل عدم الإجابة",
    },
  },
  male_health_context: { title: "هل توجد اعتبارات صحية خاصة بالرجال تؤثر في التمرين؟" },
  height: { title: "ما طولك؟" },
  current_weight: { title: "ما وزنك الحالي؟" },
  primary_goal: {
    title: "ما هدفك الأساسي؟",
    options: {
      fat_loss: "خسارة الدهون",
      muscle_gain: "زيادة الكتلة العضلية",
      general_fitness: "تحسين اللياقة العامة",
      athletic_performance: "تحسين الأداء الرياضي",
    },
  },
  target_weight: { title: "ما وزنك المستهدف؟" },
  nutrition_pattern: {
    title: "أي نمط يصف روتينك الغذائي؟",
    options: {
      structured: "وجبات منظمة",
      irregular: "وجبات غير منتظمة",
      frequent_snacking: "وجبات خفيفة متكررة",
      other: "أخرى",
    },
  },
  has_injury: { title: "هل لديك إصابة أو محدودية حركية حاليًا؟" },
  injury_area: {
    title: "ما المناطق المتأثرة؟",
    options: { knee: "الركبة", ankle: "الكاحل", back: "الظهر", shoulder: "الكتف", other: "أخرى" },
  },
  knee_injury_details: { title: "صِف كيف تؤثر إصابة الركبة في حركتك." },
  serious_injury: { title: "هل الإصابة خطيرة أو لا تزال بانتظار تصريح طبي؟" },
  experience: {
    title: "ما مستوى خبرتك التدريبية؟",
    options: { beginner: "مبتدئ", intermediate: "متوسط", advanced: "متقدم" },
  },
  advanced_programming_style: {
    title: "ما أساليب البرمجة التدريبية المتقدمة التي تستخدمها؟",
    options: {
      periodization: "التخطيط الدوري",
      velocity_based: "التدريب المعتمد على السرعة",
      autoregulation: "التنظيم الذاتي",
    },
  },
  home_training: { title: "هل ستؤدي معظم تدريباتك في المنزل؟" },
  equipment_available: {
    title: "ما المعدات المنزلية المتاحة؟",
    options: {
      none: "لا توجد معدات",
      dumbbells: "دمبل",
      bands: "أشرطة مقاومة",
      bench: "مقعد تدريب",
      pull_up_bar: "عارضة عقلة",
    },
  },
  commercial_gym_equipment: {
    title: "ما معدات النادي المتاحة لك؟",
    options: {
      free_weights: "أوزان حرة",
      machines: "أجهزة مقاومة",
      cardio: "أجهزة كارديو",
      functional_area: "منطقة تدريب وظيفي",
    },
  },
  sleep_hours: { title: "كم ساعة تنام عادةً كل ليلة؟" },
  stress_level: { title: "كيف تقيّم مستوى الضغط النفسي الحالي؟" },
  pregnancy: { title: "هل الحمل عامل ذو صلة بتخطيط التمارين حاليًا؟" },
  chest_pain: { title: "هل تشعر بألم في الصدر أثناء النشاط أو الراحة؟" },
  recent_surgery: { title: "هل أجريت جراحة حديثة دون الحصول على تصريح؟" },
  heart_disease: { title: "هل شُخّصت بمرض في القلب؟" },
  uncontrolled_hypertension: { title: "هل لديك ارتفاع ضغط دم غير منضبط؟" },
  severe_dizziness: { title: "هل تعاني دوارًا شديدًا غير مفسر؟" },
  loss_of_consciousness: { title: "هل فقدت الوعي مؤخرًا دون سبب واضح؟" },
  medical_red_flags: { title: "هل طلب منك مختص تجنب التمرين إلى حين المراجعة؟" },
  sports: {
    title: "ما الرياضات التي تمارسها حاليًا؟",
    options: {
      football: "كرة القدم",
      running: "الجري",
      strength_sport: "رياضات القوة",
      other: "أخرى",
    },
  },
  football_position: {
    title: "ما مركزك الأساسي في كرة القدم؟",
    options: {
      goalkeeper: "حارس مرمى",
      defender: "مدافع",
      midfielder: "لاعب وسط",
      forward: "مهاجم",
    },
  },
  goalkeeper_focus: {
    title: "ما أولوياتك الحالية كحارس مرمى؟",
    options: {
      reaction: "سرعة رد الفعل",
      jumping: "القفز",
      distribution: "توزيع الكرة",
      agility: "الرشاقة",
    },
  },
};

const safetyArabic: Record<string, string> = {
  "No answered safety item currently triggers a restriction.":
    "لا توجد إجابة حالية تستدعي قيدًا متعلقًا بالسلامة.",
  "Reported chest pain requires medical clearance before personalized exercise guidance.":
    "يتطلب ألم الصدر المبلغ عنه تصريحًا طبيًا قبل تقديم إرشادات تمرين مخصصة.",
  "Reported loss of consciousness requires medical clearance before continuing.":
    "يتطلب فقدان الوعي المبلغ عنه تصريحًا طبيًا قبل المتابعة.",
  "A reported medical red flag requires professional review before continuing.":
    "تتطلب علامة الخطر الطبية المبلغ عنها مراجعة مختص قبل المتابعة.",
  "Recent surgery requires professional clearance before personalized training.":
    "تتطلب الجراحة الحديثة تصريحًا من مختص قبل التدريب المخصص.",
  "Reported heart disease requires medical clearance before personalized training.":
    "يتطلب مرض القلب المبلغ عنه تصريحًا طبيًا قبل التدريب المخصص.",
  "Reported uncontrolled hypertension requires medical clearance before continuing.":
    "يتطلب ارتفاع ضغط الدم غير المنضبط تصريحًا طبيًا قبل المتابعة.",
  "Reported severe dizziness requires professional review before training guidance.":
    "يتطلب الدوار الشديد المبلغ عنه مراجعة مختص قبل إرشادات التدريب.",
  "A reported serious injury requires professional clearance before continuing.":
    "تتطلب الإصابة الخطيرة المبلغ عنها تصريحًا من مختص قبل المتابعة.",
  "Pregnancy requires conservative guidance and appropriate professional advice.":
    "يتطلب الحمل إرشادات حذرة واستشارة مهنية مناسبة.",
  "A reported injury requires conservative exercise selection and monitoring.":
    "تتطلب الإصابة المبلغ عنها اختيار تمارين حذرًا ومتابعة مستمرة.",
};

export function categoryLabel(category: AssessmentCategory, locale: Locale): string {
  return locale === "ar" ? categoryArabic[category] : categoryEnglish[category];
}

export function localizeQuestion(question: AssessmentQuestion, locale: Locale): AssessmentQuestion {
  if (locale === "en") return question;
  const translation = arabicQuestions[question.id];
  if (!translation) return question;
  const options: QuestionOption[] = question.options.map((option) => ({
    ...option,
    label: translation.options?.[option.value] ?? option.label,
  }));
  return {
    ...question,
    title: translation.title,
    description: translation.description ?? question.description,
    options,
  };
}

export function safetyTitle(status: SafetyStatus, locale: Locale): string {
  const copy = assessmentCopy[locale];
  return {
    safe: copy.safetySafeTitle,
    caution: copy.safetyCautionTitle,
    stop: copy.safetyStopTitle,
  }[status];
}

export function localizeSafetyExplanation(explanation: string, locale: Locale): string {
  return locale === "ar" ? (safetyArabic[explanation] ?? explanation) : explanation;
}

export function riskLabel(risk: RiskLevel, locale: Locale): string {
  const labels: Record<Locale, Record<RiskLevel, string>> = {
    en: { low: "Low", medium: "Medium", high: "High", critical: "Critical" },
    ar: { low: "منخفض", medium: "متوسط", high: "مرتفع", critical: "حرج" },
  };
  return labels[locale][risk];
}

export function answerLabel(
  question: AssessmentQuestion,
  value: string | number | boolean | string[],
  locale: Locale,
): string {
  const localized = localizeQuestion(question, locale);
  if (typeof value === "boolean")
    return value ? assessmentCopy[locale].yes : assessmentCopy[locale].no;
  if (Array.isArray(value)) {
    return value
      .map((item) => localized.options.find((option) => option.value === item)?.label ?? item)
      .join(locale === "ar" ? "، " : ", ");
  }
  const option = localized.options.find((item) => item.value === String(value));
  const unit = localized.unit ? ` ${localized.unit}` : "";
  return option?.label ?? `${value}${unit}`;
}

export function localizeSummaryText(text: string, locale: Locale): string {
  if (locale === "en") return text;
  const exact: Record<string, string> = {
    "Ready for standard assessment-based training guidance.":
      "جاهز لإرشادات تدريب قياسية مبنية على التقييم.",
    "Ready only for conservative guidance with stated cautions.":
      "جاهز لإرشادات حذرة فقط مع مراعاة التنبيهات المذكورة.",
    "Not ready for personalized training pending professional clearance.":
      "غير جاهز للتدريب المخصص حتى الحصول على تصريح من مختص.",
    home: "المنزل",
    dumbbells: "دمبل",
    bands: "أشرطة مقاومة",
    bench: "مقعد تدريب",
    pull_up_bar: "عارضة عقلة",
    free_weights: "أوزان حرة",
    machines: "أجهزة مقاومة",
    cardio: "أجهزة كارديو",
    functional_area: "منطقة تدريب وظيفي",
    beginner: "مبتدئ",
    intermediate: "متوسط",
    advanced: "متقدم",
  };
  if (exact[text]) return exact[text];
  if (safetyArabic[text]) return safetyArabic[text];
  const goal = /^Primary goal: ([a-z_]+)\.$/.exec(text);
  if (goal?.[1]) {
    const label = arabicQuestions.primary_goal?.options?.[goal[1]] ?? goal[1];
    return `الهدف الأساسي: ${label}.`;
  }
  const target = /^Target weight: (.+) kg\.$/.exec(text);
  if (target?.[1]) return `الوزن المستهدف: ${target[1]} كجم.`;
  const sleep = /^Reported sleep: (.+) hours per night\.$/.exec(text);
  if (sleep?.[1]) return `النوم المبلغ عنه: ${sleep[1]} ساعة كل ليلة.`;
  if (text === "Primary training setting: home.") return "مكان التدريب الأساسي: المنزل.";
  if (text === "Primary training setting: gym or other locations.") {
    return "مكان التدريب الأساسي: النادي أو أماكن أخرى.";
  }
  return text;
}
