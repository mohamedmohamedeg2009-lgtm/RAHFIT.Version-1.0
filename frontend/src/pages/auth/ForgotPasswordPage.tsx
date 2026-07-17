import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { useLocale } from "../../contexts/LocaleContext";
import { authCopy } from "../../i18n/auth";
import { authService } from "../../services/authService";
import { ApiError } from "../../services/apiClient";

export default function ForgotPasswordPage() {
  const { locale } = useLocale();
  const copy = authCopy[locale];

  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;

    setLoading(true);
    setError(null);
    try {
      await authService.forgotPassword(email);
      setSuccess(true);
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Failed to send reset link. Please check your internet connection.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <section
      className="auth-card"
      aria-labelledby="forgot-title"
      style={{ maxWidth: "420px", margin: "2rem auto" }}
    >
      <div className="mobile-brand">
        <p className="eyebrow">RAHFIT AI</p>
      </div>

      <h1 id="forgot-title" className="auth-title">
        {copy.forgotPasswordTitle}
      </h1>

      {success ? (
        <div style={{ textAlign: "center" }}>
          <div className="ds-alert ds-alert-success" style={{ marginBottom: "2rem" }}>
            {copy.successSent}
          </div>
          <Link to="/login" className="ds-button ds-button-secondary" style={{ width: "100%" }}>
            {copy.returnToLogin}
          </Link>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="auth-form" noValidate>
          {error ? <div className="ds-alert ds-alert-danger">{error}</div> : null}

          <p
            className="auth-subtitle"
            style={{ marginBottom: "1.5rem", color: "var(--color-text-muted)" }}
          >
            {copy.forgotPasswordInstructions}
          </p>

          <div className="ds-field-group">
            <label htmlFor="email" className="ds-label">
              {locale === "ar" ? "البريد الإلكتروني" : "Email Address"}
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="ds-input"
              required
              disabled={loading}
              placeholder="name@example.com"
            />
          </div>

          <button
            type="submit"
            className="ds-button ds-button-primary"
            style={{ width: "100%", marginTop: "1.5rem" }}
            disabled={loading || !email.trim()}
          >
            {loading ? <span className="spinner spinner-light" /> : copy.sendResetLink}
          </button>

          <div style={{ marginTop: "1.5rem", textAlign: "center" }}>
            <Link to="/login" className="ds-link" style={{ fontSize: "0.875rem" }}>
              {copy.returnToLogin}
            </Link>
          </div>
        </form>
      )}
    </section>
  );
}
