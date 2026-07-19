import { ApiError } from "./apiClient";
import type { Locale } from "../contexts/LocaleContext";

export interface WorkoutClientError {
  code: string;
  title: string;
  message: string;
  actionLabel?: string;
  actionPath?: string;
  retryable: boolean;
}

const known: Record<string, Omit<WorkoutClientError, "code">> = {
  workout_profile_incomplete: {
    title: "Complete your profile",
    message: "Your training profile is required before a plan can be generated.",
    actionLabel: "Complete profile",
    actionPath: "/intelligent-workouts/setup/profile",
    retryable: false,
  },
  workout_health_profile_incomplete: {
    title: "Health declaration required",
    message: "Confirm your health history before generating a safe plan.",
    actionLabel: "Review health declaration",
    actionPath: "/intelligent-workouts/setup/health",
    retryable: false,
  },
  workout_readiness_blocked: {
    title: "Training is paused",
    message:
      "Your readiness result does not currently allow plan generation. Follow the professional guidance provided by Rahafit.",
    retryable: false,
  },
  workout_medical_clearance_required: {
    title: "Medical clearance required",
    message: "Please obtain professional medical clearance before continuing with training.",
    retryable: false,
  },
  workout_plan_not_found: {
    title: "Plan unavailable",
    message: "This plan does not exist or is not available to your account.",
    actionLabel: "View workouts",
    actionPath: "/intelligent-workouts",
    retryable: false,
  },
  workout_session_not_found: {
    title: "Session unavailable",
    message: "This session does not exist or is not available to your account.",
    actionLabel: "View session history",
    actionPath: "/intelligent-workouts/history/sessions",
    retryable: false,
  },
  workout_plan_archived: {
    title: "Plan is archived",
    message: "Archived plans cannot accept new workout sessions. Activate an eligible plan first.",
    actionLabel: "View plan history",
    actionPath: "/intelligent-workouts/history/plans",
    retryable: false,
  },
  workout_session_state_invalid: {
    title: "Session already closed",
    message: "Completed or abandoned sessions cannot be changed. Refresh to view the latest state.",
    retryable: false,
  },
  workout_active_plan_conflict: {
    title: "Active plan changed",
    message: "Another plan is already active. Refresh your workout state before continuing.",
    retryable: true,
  },
  workout_exercise_unavailable: {
    title: "Exercise unavailable",
    message:
      "One or more submitted exercises are not part of this plan day. Refresh and try again.",
    retryable: true,
  },
  workout_validation_failed: {
    title: "Check your workout details",
    message: "Some workout values were rejected. Review the highlighted entries and try again.",
    retryable: false,
  },
  validation_error: {
    title: "Check your entries",
    message: "Some values are missing or outside their allowed range.",
    retryable: false,
  },
  workout_generation_failed: {
    title: "Plan generation unavailable",
    message: "A safe plan could not be generated right now. Try again later.",
    retryable: true,
  },
  workout_persistence_failed: {
    title: "Workout not saved",
    message: "The server could not confirm the save. Refresh before trying again.",
    retryable: true,
  },
};

const knownArabic: Record<
  string,
  Pick<WorkoutClientError, "title" | "message"> & { actionLabel?: string }
> = {
  workout_profile_incomplete: {
    title: "أكمل ملفك",
    message: "يلزم إكمال ملفك التدريبي قبل إنشاء الخطة.",
    actionLabel: "إكمال الملف",
  },
  workout_health_profile_incomplete: {
    title: "الإقرار الصحي مطلوب",
    message: "أكّد تاريخك الصحي قبل إنشاء خطة آمنة.",
    actionLabel: "مراجعة الإقرار الصحي",
  },
  workout_readiness_blocked: {
    title: "التدريب متوقف مؤقتًا",
    message: "نتيجة استعدادك لا تسمح بإنشاء خطة حاليًا. اتبع الإرشاد المتخصص الذي يقدمه Rahafit.",
  },
  workout_medical_clearance_required: {
    title: "يلزم تصريح طبي",
    message: "احصل على تصريح طبي متخصص قبل متابعة التدريب.",
  },
  workout_plan_not_found: {
    title: "الخطة غير متاحة",
    message: "هذه الخطة غير موجودة أو غير متاحة لحسابك.",
    actionLabel: "عرض التمارين",
  },
  workout_session_not_found: {
    title: "الجلسة غير متاحة",
    message: "هذه الجلسة غير موجودة أو غير متاحة لحسابك.",
    actionLabel: "عرض سجل الجلسات",
  },
  workout_plan_archived: {
    title: "الخطة مؤرشفة",
    message: "لا تقبل الخطط المؤرشفة جلسات جديدة. فعّل خطة مؤهلة أولًا.",
    actionLabel: "عرض سجل الخطط",
  },
  workout_session_state_invalid: {
    title: "الجلسة مغلقة",
    message: "لا يمكن تغيير الجلسات المكتملة أو المتروكة. حدّث الصفحة لعرض أحدث حالة.",
  },
  workout_active_plan_conflict: {
    title: "تغيّرت الخطة النشطة",
    message: "هناك خطة أخرى نشطة. حدّث حالة التمرين قبل المتابعة.",
  },
  workout_exercise_unavailable: {
    title: "التمرين غير متاح",
    message: "تمرين واحد أو أكثر ليس ضمن يوم الخطة. حدّث الصفحة وحاول مجددًا.",
  },
  workout_validation_failed: {
    title: "راجع تفاصيل التمرين",
    message: "رُفضت بعض قيم التمرين. راجع المدخلات وحاول مرة أخرى.",
  },
  validation_error: {
    title: "راجع مدخلاتك",
    message: "بعض القيم مفقودة أو خارج النطاق المسموح.",
  },
  workout_generation_failed: {
    title: "تعذّر إنشاء الخطة",
    message: "تعذّر إنشاء خطة آمنة الآن. حاول لاحقًا.",
  },
  workout_persistence_failed: {
    title: "لم يُحفظ التمرين",
    message: "لم يتمكن الخادم من تأكيد الحفظ. حدّث الصفحة قبل المحاولة مجددًا.",
  },
};

export function mapWorkoutError(cause: unknown, locale: Locale = "en"): WorkoutClientError {
  if (cause instanceof ApiError) {
    const item = known[cause.code];
    if (item) {
      const translated = locale === "ar" ? knownArabic[cause.code] : undefined;
      return { code: cause.code, ...item, ...translated };
    }
    if (cause.status === 401)
      return {
        code: cause.code,
        title: locale === "ar" ? "انتهت الجلسة" : "Session expired",
        message: locale === "ar" ? "سجّل الدخول مرة أخرى للمتابعة." : "Sign in again to continue.",
        actionLabel: locale === "ar" ? "تسجيل الدخول" : "Sign in",
        actionPath: "/login",
        retryable: false,
      };
    if (cause.status >= 500)
      return {
        code: cause.code,
        title: locale === "ar" ? "خدمة التمرين غير متاحة" : "Workout service unavailable",
        message:
          locale === "ar"
            ? "تعذّر إكمال الطلب. لم تتغير بيانات تمرينك الحالية."
            : "We could not complete this request. Your existing workout data has not been changed.",
        retryable: true,
      };
    return {
      code: cause.code,
      title: locale === "ar" ? "الطلب غير متاح" : "Request unavailable",
      message: locale === "ar" ? "تعذّر إكمال الطلب. راجع المدخلات وحاول مجددًا." : cause.message,
      retryable: false,
    };
  }
  return {
    code: "network_error",
    title: locale === "ar" ? "مشكلة في الاتصال" : "Connection problem",
    message:
      locale === "ar"
        ? "تحقق من اتصالك بالإنترنت وحاول مرة أخرى."
        : "Check your internet connection and try again.",
    retryable: true,
  };
}
