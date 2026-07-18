import { lazy, Suspense } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { ProtectedRoute } from "../components/ProtectedRoute";
import { FullPageLoader } from "../components/ui";
import { AssessmentProvider } from "../contexts/AssessmentContext";
import { AuthProvider } from "../contexts/AuthContext";
import { LoginPage } from "../pages/auth/LoginPage";
import { RegisterPage } from "../pages/auth/RegisterPage";
import { AuthLayout } from "../layouts/AuthLayout";
import { AssessmentLayout } from "../layouts/AssessmentLayout";
import { useAuth } from "../hooks/useAuth";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { useLocale } from "../contexts/LocaleContext";

const AssessmentWelcomePage = lazy(() => import("../pages/assessment/AssessmentWelcomePage"));
const AssessmentResumePage = lazy(() => import("../pages/assessment/AssessmentResumePage"));
const AssessmentWizardPage = lazy(() => import("../pages/assessment/AssessmentWizardPage"));
const AssessmentReviewPage = lazy(() => import("../pages/assessment/AssessmentReviewPage"));
const AssessmentCompletedPage = lazy(() => import("../pages/assessment/AssessmentCompletedPage"));
const DashboardPage = lazy(() => import("../pages/dashboard/DashboardPage"));
const WorkoutPage = lazy(() => import("../pages/workout/WorkoutPage"));
const WorkoutPlanPage = lazy(() => import("../pages/workout/WorkoutPlanPage"));
const WorkoutSessionPage = lazy(() => import("../pages/workout/WorkoutSessionPage"));
const WorkoutHistoryPage = lazy(() => import("../pages/workout/WorkoutHistoryPage"));
const NutritionPage = lazy(() => import("../pages/nutrition/NutritionPage"));
const NutritionHistoryPage = lazy(() => import("../pages/nutrition/NutritionHistoryPage"));
const IntelligentWorkoutOverviewPage = lazy(
  () => import("../pages/intelligentWorkout/WorkoutOverviewPage"),
);
const WorkoutProfileSetupPage = lazy(
  () => import("../pages/intelligentWorkout/WorkoutProfileSetupPage"),
);
const WorkoutHealthSetupPage = lazy(
  () => import("../pages/intelligentWorkout/WorkoutHealthSetupPage"),
);
const WorkoutGenerationPage = lazy(
  () => import("../pages/intelligentWorkout/WorkoutGenerationPage"),
);
const IntelligentWorkoutPlanPage = lazy(
  () => import("../pages/intelligentWorkout/WorkoutPlanDetailPage"),
);
const IntelligentWorkoutSessionPage = lazy(
  () => import("../pages/intelligentWorkout/WorkoutSessionPage"),
);
const WorkoutAdaptationPage = lazy(
  () => import("../pages/intelligentWorkout/WorkoutAdaptationPage"),
);
const WorkoutPlanHistoryPage = lazy(
  () => import("../pages/intelligentWorkout/WorkoutPlanHistoryPage"),
);
const WorkoutSessionHistoryPage = lazy(
  () => import("../pages/intelligentWorkout/WorkoutSessionHistoryPage"),
);
const ForgotPasswordPage = lazy(() => import("../pages/auth/ForgotPasswordPage"));
const ResetPasswordPage = lazy(() => import("../pages/auth/ResetPasswordPage"));
const AICoachPage = lazy(() => import("../pages/aiCoach/AICoachPage"));

/** Sets document.title while a route is active. */
function RouteTitle({ en, ar }: { en: string; ar: string }) {
  const { locale } = useLocale();
  useDocumentTitle(locale === "ar" ? ar : en);
  return null;
}

function AssessmentExperience() {
  return (
    <AssessmentProvider>
      <AssessmentLayout />
    </AssessmentProvider>
  );
}

function AuthOnlyRedirect() {
  const { user, isLoading } = useAuth();
  if (isLoading) {
    return (
      <main className="auth-shell" aria-busy="true" aria-live="polite">
        <div className="loading-card">
          <span className="spinner" aria-hidden="true" />
          <p>Restoring your session…</p>
        </div>
      </main>
    );
  }
  return user ? <Navigate to="/app" replace /> : <Navigate to="/login" replace />;
}

function NotFoundPage() {
  useDocumentTitle("Page not found");
  return (
    <main className="protected-shell">
      <section className="protected-card" aria-labelledby="not-found-title">
        <p className="eyebrow">RAHFIT AI</p>
        <h1 id="not-found-title">Page not found</h1>
        <p className="muted-text">The page you requested does not exist.</p>
        <a className="button button-primary button-link" href="/">
          Return home
        </a>
      </section>
    </main>
  );
}

export function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Suspense fallback={<FullPageLoader label="Loading experience" />}>
          <Routes>
            <Route element={<AuthLayout />}>
              <Route
                path="/login"
                element={
                  <>
                    <RouteTitle en="Sign in" ar="تسجيل الدخول" />
                    <LoginPage />
                  </>
                }
              />
              <Route
                path="/register"
                element={
                  <>
                    <RouteTitle en="Create account" ar="إنشاء حساب" />
                    <RegisterPage />
                  </>
                }
              />
              <Route
                path="/forgot-password"
                element={
                  <>
                    <RouteTitle en="Forgot password" ar="نسيت كلمة المرور" />
                    <ForgotPasswordPage />
                  </>
                }
              />
              <Route
                path="/reset-password"
                element={
                  <>
                    <RouteTitle en="Reset password" ar="إعادة تعيين كلمة المرور" />
                    <ResetPasswordPage />
                  </>
                }
              />
            </Route>
            <Route element={<ProtectedRoute />}>
              <Route
                path="/app"
                element={
                  <>
                    <RouteTitle en="Dashboard" ar="لوحة التحكم" />
                    <DashboardPage />
                  </>
                }
              />
              <Route path="/workouts" element={<WorkoutPage />} />
              <Route path="/workouts/history" element={<WorkoutHistoryPage />} />
              <Route path="/workouts/:planId" element={<WorkoutPlanPage />} />
              <Route path="/workouts/:planId/session/:dayId" element={<WorkoutSessionPage />} />
              <Route path="/nutrition" element={<NutritionPage />} />
              <Route path="/nutrition/history" element={<NutritionHistoryPage />} />
              <Route
                path="/ai-coach"
                element={
                  <>
                    <RouteTitle en="AI Coach" ar="المدرب الذكي" />
                    <AICoachPage />
                  </>
                }
              />
              <Route
                path="/intelligent-workouts"
                element={
                  <>
                    <RouteTitle en="My Workout" ar="تمريني الذكي" />
                    <IntelligentWorkoutOverviewPage />
                  </>
                }
              />
              <Route
                path="/intelligent-workouts/setup/profile"
                element={
                  <>
                    <RouteTitle en="Training Profile" ar="الملف التدريبي" />
                    <WorkoutProfileSetupPage />
                  </>
                }
              />
              <Route
                path="/intelligent-workouts/setup/health"
                element={
                  <>
                    <RouteTitle en="Health Declaration" ar="الإقرار الصحي" />
                    <WorkoutHealthSetupPage />
                  </>
                }
              />
              <Route
                path="/intelligent-workouts/generate"
                element={
                  <>
                    <RouteTitle en="Generate Plan" ar="إنشاء خطة" />
                    <WorkoutGenerationPage />
                  </>
                }
              />
              <Route
                path="/intelligent-workouts/plans/:planId"
                element={
                  <>
                    <RouteTitle en="Training Plan" ar="خطة التدريب" />
                    <IntelligentWorkoutPlanPage />
                  </>
                }
              />
              <Route
                path="/intelligent-workouts/plans/:planId/session/:dayNumber"
                element={
                  <>
                    <RouteTitle en="Workout Session" ar="جلسة التمرين" />
                    <IntelligentWorkoutSessionPage />
                  </>
                }
              />
              <Route
                path="/intelligent-workouts/sessions/:sessionId"
                element={
                  <>
                    <RouteTitle en="Workout Session" ar="جلسة التمرين" />
                    <IntelligentWorkoutSessionPage />
                  </>
                }
              />
              <Route
                path="/intelligent-workouts/plans/:planId/adaptation"
                element={
                  <>
                    <RouteTitle en="Adaptation Review" ar="مراجعة التكيف" />
                    <WorkoutAdaptationPage />
                  </>
                }
              />
              <Route
                path="/intelligent-workouts/history/plans"
                element={
                  <>
                    <RouteTitle en="Plan History" ar="سجل الخطط" />
                    <WorkoutPlanHistoryPage />
                  </>
                }
              />
              <Route
                path="/intelligent-workouts/history/sessions"
                element={
                  <>
                    <RouteTitle en="Session History" ar="سجل الجلسات" />
                    <WorkoutSessionHistoryPage />
                  </>
                }
              />
              <Route element={<AssessmentExperience />}>
                <Route path="/assessment" element={<AssessmentWelcomePage />} />
                <Route path="/assessment/resume/:sessionId" element={<AssessmentResumePage />} />
                <Route path="/assessment/session/:sessionId" element={<AssessmentWizardPage />} />
                <Route
                  path="/assessment/session/:sessionId/question/:questionId"
                  element={<AssessmentWizardPage />}
                />
                <Route
                  path="/assessment/session/:sessionId/review"
                  element={<AssessmentReviewPage />}
                />
                <Route
                  path="/assessment/completed/:sessionId"
                  element={<AssessmentCompletedPage />}
                />
              </Route>
            </Route>
            <Route path="/" element={<AuthOnlyRedirect />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </Suspense>
      </AuthProvider>
    </BrowserRouter>
  );
}
