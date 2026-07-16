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
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
            </Route>
            <Route element={<ProtectedRoute />}>
              <Route path="/app" element={<DashboardPage />} />
              <Route path="/workouts" element={<WorkoutPage />} />
              <Route path="/workouts/history" element={<WorkoutHistoryPage />} />
              <Route path="/workouts/:planId" element={<WorkoutPlanPage />} />
              <Route path="/workouts/:planId/session/:dayId" element={<WorkoutSessionPage />} />
              <Route path="/nutrition" element={<NutritionPage />} />
              <Route path="/nutrition/history" element={<NutritionHistoryPage />} />
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
