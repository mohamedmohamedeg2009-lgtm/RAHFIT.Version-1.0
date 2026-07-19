import type { Locale } from "../contexts/LocaleContext";
import type {
  ReadinessLevel,
  RecommendedAction,
} from "../services/dailyCheckInService";

export const dailyCheckInCopy = {
  en: {
    title: "Daily AI Check-in",
    subtitle: "Log today's readiness signals to personalize your training & recovery guidance",
    todayStatus: "Today's Status",
    completedToday: "Daily check-in completed for today",
    notCompletedToday: "No check-in recorded for today yet",
    startCheckIn: "Complete Check-in",
    updateCheckIn: "Update Check-in",
    
    inputs: {
      sleepHours: "Sleep Duration (Hours)",
      sleepQuality: "Sleep Quality (1-5)",
      energyLevel: "Energy Level (1-5)",
      stressLevel: "Stress Level (1-5)",
      muscleSoreness: "Muscle Soreness (1-5)",
      painLevel: "Pain Level (0-10)",
      hydrationStatus: "Hydration Status",
      mood: "Mood (1-5)",
      optionalNote: "Daily Notes (Optional)",
      notePlaceholder: "Add any context e.g. felt tired after travel, slight tension...",
      hydrationLow: "Low (Dehydrated)",
      hydrationModerate: "Moderate",
      hydrationGood: "Good (Optimal)",
    },

    summary: {
      readinessScore: "Readiness Score",
      recoveryScore: "Recovery Index",
      sleepScore: "Sleep Quality",
      stressScore: "Stress Index",
      hydrationScore: "Hydration Level",
      recommendedAction: "Recommended Action",
      warnings: "Key Signals & Warnings",
      askCoach: "Explain Today's Readiness with AI Coach",
      calmNoticeTitle: "Safety Guidance Notice",
      calmNoticeText: "High physical discomfort or pain reported. We recommend prioritizing rest and consulting a qualified professional.",
    },
  },
  ar: {
    title: "الفحص اليومي بالذكاء الاصطناعي",
    subtitle: "سجّل مؤشرات جاهزيتك اليوم لتخصيص توجيهات التدريب والاستشفاء",
    todayStatus: "حالة اليوم",
    completedToday: "تم إكمال الفحص اليومي لهذا اليوم",
    notCompletedToday: "لم يتم تسجيل الفحص اليومي لهذا اليوم بعد",
    startCheckIn: "إكمال الفحص اليومي",
    updateCheckIn: "تحديث الفحص اليومي",

    inputs: {
      sleepHours: "ساعات النوم (بالساعات)",
      sleepQuality: "جودة النوم (١-٥)",
      energyLevel: "مستوى الطاقة (١-٥)",
      stressLevel: "مستوى التوتر (١-٥)",
      muscleSoreness: "إجهاد العضلات (١-٥)",
      painLevel: "مستوى الألم (٠-١٠)",
      hydrationStatus: "مستوى الترطيب والمياه",
      mood: "المزاج (١-٥)",
      optionalNote: "ملاحظات يومية (اختياري)",
      notePlaceholder: "أضف أي تفاصيل مثل: شعور بالإرهاق بعد السفر...",
      hydrationLow: "منخفض (جفاف)",
      hydrationModerate: "معتدل",
      hydrationGood: "ممتاز (مثالي)",
    },

    summary: {
      readinessScore: "مؤشر الجاهزية",
      recoveryScore: "مؤشر الاستشفاء",
      sleepScore: "جودة النوم",
      stressScore: "مستوى التوتر",
      hydrationScore: "مستوى الترطيب",
      recommendedAction: "التوصية المعتمدة",
      warnings: "الإشارات والإنذارات الرئيسية",
      askCoach: "اشرح جاهزيتي اليوم مع المدرب الذكي",
      calmNoticeTitle: "تنبيه التوجيه والسلامة",
      calmNoticeText: "تم تسجيل مستويات إجهاد أو ألم مرتفعة. نوصي بمنح جسمك الراحة واستشارة أخصائي عند الحاجة.",
    },
  },
};

export function getReadinessLevelLabel(level: ReadinessLevel, locale: Locale): string {
  const labels: Record<ReadinessLevel, { en: string; ar: string }> = {
    high: { en: "High Readiness", ar: "جاهزية عالية" },
    moderate: { en: "Moderate Readiness", ar: "جاهزية متوسطة" },
    low: { en: "Low Readiness", ar: "جاهزية منخفضة" },
    recovery_required: { en: "Recovery Required", ar: "يتطلب راحة واستشفاء" },
  };
  return labels[level]?.[locale] || level;
}

export function getRecommendedActionLabel(action: RecommendedAction, locale: Locale): string {
  const labels: Record<RecommendedAction, { en: string; ar: string }> = {
    normal_training: { en: "Normal Training", ar: "التدريب المعتاد" },
    reduced_intensity: { en: "Reduced Intensity", ar: "تدريب بخفّة وتعديل الجهد" },
    recovery_session: { en: "Recovery & Light Session", ar: "جلسة استشفاء خفيفة" },
    rest_and_professional_guidance: {
      en: "Rest & Professional Guidance",
      ar: "راحة تامة واستشارة مختص",
    },
  };
  return labels[action]?.[locale] || action;
}

export function getWarningCodeLabel(code: string, locale: Locale): string {
  const labels: Record<string, { en: string; ar: string }> = {
    high_pain: { en: "High Pain Reported", ar: "ألم مرتفع" },
    moderate_pain: { en: "Moderate Pain Reported", ar: "ألم متوسط" },
    severe_soreness: { en: "Severe Muscle Soreness", ar: "إجهاد عضلي شديد" },
    sleep_deprivation: { en: "Sleep Deprived", ar: "نقص في النوم" },
    high_stress: { en: "High Stress Index", ar: "مستوى توتر مرتفع" },
    dehydration: { en: "Low Hydration", ar: "جفاف / سوائل منخفضة" },
    low_energy: { en: "Low Energy Levels", ar: "طاقة منخفضة" },
    multiple_fatigue_factors: { en: "Multiple Fatigue Signals", ar: "عوامل إجهاد متعددة" },
  };
  return labels[code]?.[locale] || code;
}
