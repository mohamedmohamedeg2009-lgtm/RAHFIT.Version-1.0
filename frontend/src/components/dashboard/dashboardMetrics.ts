import type { DashboardData } from "../../types/dashboard";

export type HealthStatus = "excellent" | "good" | "attention" | "critical" | "neutral";

export type DashboardInsight = {
  id: string;
  title: string;
  description: string;
  priority: "high" | "medium" | "low";
  category: "training" | "nutrition" | "recovery" | "sleep" | "hydration" | "general";
  actionLabel?: string;
  actionHref?: string;
  whyExplanation: string;
};

export function clampPercentage(value: number): number {
  if (typeof value !== "number" || isNaN(value)) return 0;
  return Math.min(Math.max(Math.round(value), 0), 100);
}

export function calculateTrend(current: number, previous: number): number {
  if (typeof current !== "number" || typeof previous !== "number" || previous <= 0) return 0;
  return Math.round(((current - previous) / previous) * 100);
}

export function getHealthStatus(score: number): HealthStatus {
  if (typeof score !== "number" || isNaN(score) || score <= 0) return "neutral";
  if (score >= 85) return "excellent";
  if (score >= 70) return "good";
  if (score >= 50) return "attention";
  return "critical";
}

// Translations map for deterministic insights
const insightsTranslation = {
  en: {
    hydrationTitle: "Hydration Intake Check",
    hydrationDesc:
      "Your water intake is below 60% of your daily target. Hydrate now to maintain metabolic and athletic performance.",
    hydrationWhy:
      "Water regulates body temperature, lubricates joints, and transports nutrients. Maintaining hydration supports cardiovascular health and physical performance.",

    sleepTitle: "Slight Deficit in Sleep Rest",
    sleepDesc:
      "Your latest sleep duration was under your recommended 8-hour target. Consider a lighter exercise load today.",
    sleepWhy:
      "Deep sleep cycles trigger tissue growth, muscle recovery, and growth hormone release. Lighter sessions allow the nervous system to adapt safely.",

    recoveryTitle: "Optimal Active Readiness",
    recoveryDesc:
      "Excellent recovery state and workout completion. You are well positioned for an intense training day.",
    recoveryWhy:
      "Your sleep readiness and readiness markers align perfectly, suggesting high autonomic nervous system balance and muscle recovery.",

    workoutMissTitle: "Workout Rescheduling",
    workoutMissDesc:
      "You missed a planned session recently. Let's adjust your weekly target to remain consistent.",
    workoutMissKey:
      "Consistency builds muscle and cardiovascular stamina over time. Shorter sessions are always better than skipping completely.",

    nutritionTitle: "Daily Fueling Snapshot",
    nutritionDesc:
      "You have consumed over 70% of your target calories. Evaluate remaining meals to align with macros.",
    nutritionWhy:
      "Aligning protein, fat, and carbohydrate intake with targets stabilizes blood glucose levels and ensures sustained muscle glycogen synthesis.",

    onboardTitle: "Welcome to Rahafit platform",
    onboardDesc:
      "Complete your wellness assessments to receive personalized coaching insights and adaptations.",
    onboardWhy:
      "Our Safety Engine requires baseline biometrics to construct personalized training gates and nutritional plans.",

    ctaAction: "Review Plan",
    ctaHydration: "Log Water",
    ctaOnboard: "Start Assessment",
  },
  ar: {
    hydrationTitle: "مستوى ترطيب الجسم",
    hydrationDesc:
      "معدل شرب الماء لديك أقل من ٦٠٪ من الهدف اليومي. اشرب الماء الآن للحفاظ على الأداء الأيضي والبدني.",
    hydrationWhy:
      "ينظم الماء درجة حرارة الجسم ويرطب المفاصل وينقل العناصر الغذائية. الحفاظ على الترطيب يدعم صحة القلب والأوعية الدموية والقدرة البدنية.",

    sleepTitle: "عجز طفيف في ساعات النوم",
    sleepDesc:
      "ساعات نومك الأخيرة أقل من الهدف الموصى به (٨ ساعات). يوصى بتخفيف شدة التمرين اليوم.",
    sleepWhy:
      "تطلق دورات النوم العميق هرمونات النمو وتساعد على استشفاء الأنسجة والعضلات. التدريبات الخفيفة تدعم تكيف الجهاز العصبي بأمان.",

    recoveryTitle: "جاهزية بدنية مثالية",
    recoveryDesc:
      "مؤشرات الاستشفاء ممتازة وتم إكمال التمرين الأخير. جسمك مستعد لجلسة تدريبية مكثفة اليوم.",
    recoveryWhy:
      "تتطابق جودة النوم ومؤشرات الجاهزية بشكل مثالي، مما يشير إلى توازن رائع في الجهاز العصبي اللاإرادي واستشفاء العضلات.",

    workoutMissTitle: "جدولة التمارين الرياضية",
    workoutMissDesc:
      "لقد فاتك تمرين مخطط له مؤخرًا. دعنا نعدل أهدافك الأسبوعية للحفاظ على استمرارية نشاطك.",
    workoutMissKey:
      "تبني الاستمرارية القوة البدنية والقدرة على التحمل بمرور الوقت. الجلسات القصيرة دائمًا أفضل من تخطي التمرين تمامًا.",

    nutritionTitle: "مخطط التغذية اليومي",
    nutritionDesc:
      "لقد استهلكت أكثر من ٧٠٪ من السعرات الحرارية المستهدفة. راجع وجباتك المتبقية لتتوافق مع المغذيات.",
    nutritionWhy:
      "يؤدي ضبط تناول البروتين والدهون والكربوهيدرات مع الأهداف إلى استقرار مستويات الجلوكوز وضمان بناء الجليكوجين العضلي.",

    onboardTitle: "مرحبًا بك في منصة Rahafit",
    onboardDesc: "أكمل تقييماتك الصحية البدنية والطبية للحصول على توصيات وخطط مخصصة وآمنة.",
    onboardWhy:
      "يتطلب محرك السلامة الخاص بنا مؤشرات حيوية أساسية لبناء بوابات تدريب مخصصة وخطط تغذية دقيقة.",

    ctaAction: "راجع الخطة",
    ctaHydration: "تسجيل المياه",
    ctaOnboard: "ابدأ التقييم",
  },
};

export function buildDashboardInsights(
  dashboard: Partial<DashboardData> | null,
  locale: string,
): DashboardInsight[] {
  const isRtl = locale === "ar";
  const text = isRtl ? insightsTranslation.ar : insightsTranslation.en;
  const list: DashboardInsight[] = [];

  if (!dashboard) {
    list.push({
      id: "onboard",
      title: text.onboardTitle,
      description: text.onboardDesc,
      priority: "high",
      category: "general",
      actionLabel: text.ctaOnboard,
      actionHref: "/assessment",
      whyExplanation: text.onboardWhy,
    });
    return list;
  }

  const { nutrition, workout, assessment } = dashboard;

  // Rule 1: Low hydration
  if (nutrition && nutrition.waterTargetMl > 0) {
    const hydrRatio = nutrition.waterConsumedMl / nutrition.waterTargetMl;
    if (hydrRatio < 0.6) {
      list.push({
        id: "hydration",
        title: text.hydrationTitle,
        description: text.hydrationDesc,
        priority: "high",
        category: "hydration",
        actionLabel: text.ctaHydration,
        actionHref: "/nutrition",
        whyExplanation: text.hydrationWhy,
      });
    }
  }

  // Rule 2: Poor sleep
  const readiness = assessment?.readinessScore ?? 80;
  if (readiness < 75) {
    list.push({
      id: "sleep",
      title: text.sleepTitle,
      description: text.sleepDesc,
      priority: "medium",
      category: "sleep",
      actionLabel: text.ctaAction,
      actionHref: "/intelligent-workouts",
      whyExplanation: text.sleepWhy,
    });
  }

  // Rule 3: Workout + Recovery success
  if (workout?.status === "completed" && readiness >= 80) {
    list.push({
      id: "recovery",
      title: text.recoveryTitle,
      description: text.recoveryDesc,
      priority: "low",
      category: "recovery",
      whyExplanation: text.recoveryWhy,
    });
  }

  // Rule 4: Missed workout
  if (workout && workout.status !== "completed" && workout.lastActivityAt === null) {
    list.push({
      id: "workout_miss",
      title: text.workoutMissTitle,
      description: text.workoutMissDesc,
      priority: "medium",
      category: "training",
      actionLabel: text.ctaAction,
      actionHref: "/intelligent-workouts",
      whyExplanation: text.workoutMissKey,
    });
  }

  // Rule 5: Nutrition high calorie target progress
  if (nutrition && nutrition.targetCalories > 0) {
    const calRatio = nutrition.caloriesConsumed / nutrition.targetCalories;
    if (calRatio > 0.7 && calRatio < 1.0) {
      list.push({
        id: "nutrition",
        title: text.nutritionTitle,
        description: text.nutritionDesc,
        priority: "medium",
        category: "nutrition",
        actionLabel: text.ctaAction,
        actionHref: "/nutrition",
        whyExplanation: text.nutritionWhy,
      });
    }
  }

  // Onboarding fallback if no conditions matched
  if (list.length === 0) {
    list.push({
      id: "general_status",
      title: text.onboardTitle,
      description: text.onboardDesc,
      priority: "low",
      category: "general",
      whyExplanation: text.onboardWhy,
    });
  }

  return list;
}
