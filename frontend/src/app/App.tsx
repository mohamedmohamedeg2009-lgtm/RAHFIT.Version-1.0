import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { ProtectedRoute } from "../components/ProtectedRoute";
import { AuthProvider } from "../contexts/AuthContext";
import { LoginPage } from "../pages/auth/LoginPage";
import { RegisterPage } from "../pages/auth/RegisterPage";
import { AuthLayout } from "../layouts/AuthLayout";
import { useAuth } from "../hooks/useAuth";

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

function AppHome() {
  const { user, logout } = useAuth();
  return (
    <main className="protected-shell">
      <section className="protected-card" aria-labelledby="welcome-title">
        <p className="eyebrow">RAHFIT AI</p>
        <h1 id="welcome-title">Your coaching journey starts here.</h1>
        <p className="muted-text">
          Signed in as <strong>{user?.email}</strong>. Assessment, workouts, nutrition, and coaching
          will be added in upcoming phases.
        </p>
        <button className="button button-primary" type="button" onClick={() => void logout()}>
          Sign out
        </button>
      </section>
    </main>
  );
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
        <Routes>
          <Route element={<AuthLayout />}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
          </Route>
          <Route element={<ProtectedRoute />}>
            <Route path="/app" element={<AppHome />} />
          </Route>
          <Route path="/" element={<AuthOnlyRedirect />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
