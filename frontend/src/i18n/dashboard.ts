import type { Locale } from "../contexts/LocaleContext";
import type {
  DashboardActionType,
  DashboardAssessmentStatus,
  FeatureStatus,
} from "../types/dashboard";

export const dashboardCopy = {
  en: {
    brand: "RAHFIT AI",
    dashboard: "Today",
    greeting: "Good to see you",
    context: "One clear next step, grounded in your real account data.",
    theme: "Toggle color theme",
    language: "العربية",
    signOut: "Sign out",
    todayPriority: "Today’s priority",
    whyThis: "Why this is first",
    assessment: "Assessment overview",
    completion: "Assessment completion",
    readiness: "Readiness score",
    risk: "Risk level",
    missing: "Missing categories",
    noMissing: "No required categories are missing.",
    modules: "Your RAHFIT modules",
    modulesBody: "Availability reflects your current state and this release’s real capabilities.",
    progress: "Progress snapshot",
    profile: "Profile completeness",
    lastActivity: "Last assessment activity",
    noActivity: "No assessment activity yet",
    quickActions: "Quick actions",
    partialTitle: "Some dashboard data is temporarily unavailable",
    partialBody:
      "Available account actions remain safe to use. Refresh to try the missing source again.",
    retry: "Refresh dashboard",
    loading: "Preparing your dashboard",
    errorTitle: "Your dashboard could not load",
    errorBody: "Your account is safe. Check the backend connection and try again.",
    sessionExpired: "Your session has expired. Sign in again to continue.",
    safetyBlocked: "Plan generation blocked",
    reassessment:
      "A fresh assessment is recommended because your latest result is over 90 days old.",
    profileMissing: "Missing profile preferences",
    defaultUnits: "Current units",
    open: "Open",
    notAvailable: "Not available",
    notCalculated: "Not calculated",
  },
  ar: {
    brand: "RAHFIT AI",
    dashboard: "اليوم",
    greeting: "سعداء بعودتك",
    context: "خطوة واحدة واضحة مبنية على بيانات حسابك الحقيقية.",
    theme: "تبديل مظهر الألوان",
    language: "English",
    signOut: "تسجيل الخروج",
    todayPriority: "أولوية اليوم",
    whyThis: "لماذا هذه الخطوة أولًا",
    assessment: "نظرة عامة على التقييم",
    completion: "اكتمال التقييم",
    readiness: "درجة الجاهزية",
    risk: "مستوى الخطورة",
    missing: "الفئات الناقصة",
    noMissing: "لا توجد فئات مطلوبة ناقصة.",
    modules: "وحدات RAHFIT الخاصة بك",
    modulesBody: "يعكس التوفر حالتك الحالية والإمكانات الحقيقية لهذا الإصدار.",
    progress: "ملخص التقدم",
    profile: "اكتمال الملف الشخصي",
    lastActivity: "آخر نشاط للتقييم",
    noActivity: "لا يوجد نشاط تقييم بعد",
    quickActions: "إجراءات سريعة",
    partialTitle: "بعض بيانات لوحة التحكم غير متاحة مؤقتًا",
    partialBody: "تظل إجراءات الحساب المتاحة آمنة. أعد المحاولة لتحميل المصدر الناقص.",
    retry: "تحديث لوحة التحكم",
    loading: "جارٍ إعداد لوحة التحكم",
    errorTitle: "تعذر تحميل لوحة التحكم",
    errorBody: "حسابك آمن. تحقق من اتصال الخادم وحاول مرة أخرى.",
    sessionExpired: "انتهت جلستك. سجّل الدخول مرة أخرى للمتابعة.",
    safetyBlocked: "إنشاء الخطط متوقف",
    reassessment: "يوصى بإجراء تقييم جديد لأن أحدث نتيجة تجاوزت 90 يومًا.",
    profileMissing: "تفضيلات الملف الشخصي الناقصة",
    defaultUnits: "الوحدات الحالية",
    open: "فتح",
    notAvailable: "غير متاح",
    notCalculated: "لم تُحسب",
  },
} as const;

const actionLabels: Record<Locale, Record<DashboardActionType, string>> = {
  en: {
    start_assessment: "Start assessment",
    resume_assessment: "Resume assessment",
    review_safety_warning: "Review safety notice",
    complete_missing_profile_information: "Review profile setup",
    view_assessment_summary: "View assessment summary",
    continue_available_feature: "Refresh dashboard",
    log_out: "Log out",
  },
  ar: {
    start_assessment: "ابدأ التقييم",
    resume_assessment: "استكمل التقييم",
    review_safety_warning: "راجع تنبيه السلامة",
    complete_missing_profile_information: "راجع إعداد الملف الشخصي",
    view_assessment_summary: "اعرض ملخص التقييم",
    continue_available_feature: "حدّث لوحة التحكم",
    log_out: "تسجيل الخروج",
  },
};

const statusLabels: Record<Locale, Record<DashboardAssessmentStatus, string>> = {
  en: {
    not_started: "Not started",
    in_progress: "In progress",
    completed: "Completed",
    unavailable: "Temporarily unavailable",
  },
  ar: {
    not_started: "لم يبدأ",
    in_progress: "قيد التنفيذ",
    completed: "مكتمل",
    unavailable: "غير متاح مؤقتًا",
  },
};

const featureLabels: Record<Locale, Record<FeatureStatus, string>> = {
  en: {
    available: "Available",
    locked: "Locked",
    coming_soon: "Coming soon",
    action_required: "Action required",
  },
  ar: {
    available: "متاح",
    locked: "مغلق",
    coming_soon: "قريبًا",
    action_required: "يتطلب إجراء",
  },
};

export const actionLabel = (type: DashboardActionType, locale: Locale) =>
  actionLabels[locale][type];
export const dashboardStatusLabel = (status: DashboardAssessmentStatus, locale: Locale) =>
  statusLabels[locale][status];
export const featureStatusLabel = (status: FeatureStatus, locale: Locale) =>
  featureLabels[locale][status];
