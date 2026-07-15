import { Navigate, Outlet } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";

export function AuthLayout() {
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

  if (user) {
    return <Navigate to="/app" replace />;
  }

  return (
    <main className="auth-shell">
      <div className="auth-brand-panel">
        <p className="eyebrow">RAHFIT AI</p>
        <h1>Small steps. Stronger you.</h1>
        <p>
          A thoughtful personal coach for training, nutrition, recovery, and the habits that make
          progress sustainable.
        </p>
        <div className="trust-note">
          <span aria-hidden="true">✦</span>
          <span>Your data stays yours. We use it to make your next step more relevant.</span>
        </div>
      </div>
      <div className="auth-form-panel">
        <Outlet />
      </div>
    </main>
  );
}
