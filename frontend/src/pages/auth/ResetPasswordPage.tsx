import { useState, type FormEvent } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useLocale } from "../../contexts/LocaleContext";
import { authCopy } from "../../i18n/auth";
import { authService } from "../../services/authService";
import { ApiError } from "../../services/apiClient";

export default function ResetPasswordPage() {
  const { locale } = useLocale();
  const copy = authCopy[locale];
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!token) {
    return (
      <section
        className="auth-card"
        aria-labelledby="reset-error-title"
        style={{ maxWidth: "420px", margin: "2rem auto", textAlign: "center" }}
      >
        <h1 id="reset-error-title" className="auth-title" style={{ color: "var(--color-danger)" }}>
          {locale === "ar" ? "رابط غير صالح" : "Invalid Reset Link"}
        </h1>
        <p className="auth-subtitle" style={{ marginBottom: "2rem" }}>
          {copy.invalidToken}
        </p>
        <Link to="/login" className="ds-button ds-button-secondary" style={{ width: "100%" }}>
          {copy.returnToLogin}
        </Link>
      </section>
    );
  }

  const isPasswordValid = password.length >= 12;
  const isMatch = password === confirmPassword;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!isPasswordValid || !isMatch) return;

    setLoading(true);
    setError(null);
    try {
      await authService.resetPassword(token, password, confirmPassword);
      setSuccess(true);
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        setError(
          err.message === "The password reset link is invalid or expired."
            ? copy.invalidToken
            : err.message,
        );
      } else {
        setError("Connection error. Could not reset password.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <section
      className="auth-card"
      aria-labelledby="reset-title"
      style={{ maxWidth: "420px", margin: "2rem auto" }}
    >
      <div className="mobile-brand">
        <p className="eyebrow">RAHFIT AI</p>
      </div>

      <h1 id="reset-title" className="auth-title">
        {copy.resetPasswordTitle}
      </h1>

      {success ? (
        <div style={{ textAlign: "center" }}>
          <div className="ds-alert ds-alert-success" style={{ marginBottom: "2rem" }}>
            {copy.successReset}
          </div>
          <Link to="/login" className="ds-button ds-button-secondary" style={{ width: "100%" }}>
            {copy.returnToLogin}
          </Link>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="auth-form" noValidate>
          {error ? <div className="ds-alert ds-alert-danger">{error}</div> : null}

          <div className="ds-field-group">
            <label htmlFor="password" className="ds-label">
              {copy.newPasswordLabel}
            </label>
            <div style={{ position: "relative" }}>
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="ds-input"
                required
                disabled={loading}
                style={{
                  paddingLeft: locale === "ar" ? "12px" : "3rem",
                  paddingRight: locale === "ar" ? "3rem" : "12px",
                }}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: "absolute",
                  top: "50%",
                  transform: "translateY(-50%)",
                  right: locale === "ar" ? "auto" : "12px",
                  left: locale === "ar" ? "12px" : "auto",
                  background: "none",
                  border: "none",
                  color: "var(--color-text-muted)",
                  cursor: "pointer",
                  fontSize: "0.875rem",
                }}
                tabIndex={-1}
              >
                {showPassword
                  ? locale === "ar"
                    ? "إخفاء"
                    : "Hide"
                  : locale === "ar"
                    ? "إظهار"
                    : "Show"}
              </button>
            </div>
            <p
              style={{
                fontSize: "0.75rem",
                marginTop: "0.25rem",
                color: isPasswordValid ? "var(--color-success)" : "var(--color-text-muted)",
              }}
            >
              {copy.passwordRequirements}
            </p>
          </div>

          <div className="ds-field-group" style={{ marginTop: "1rem" }}>
            <label htmlFor="confirmPassword" className="ds-label">
              {copy.confirmPasswordLabel}
            </label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="ds-input"
              required
              disabled={loading}
            />
            {confirmPassword && !isMatch ? (
              <p
                style={{ fontSize: "0.75rem", marginTop: "0.25rem", color: "var(--color-danger)" }}
              >
                {copy.passwordsDoNotMatch}
              </p>
            ) : null}
          </div>

          <button
            type="submit"
            className="ds-button ds-button-primary"
            style={{ width: "100%", marginTop: "2rem" }}
            disabled={loading || !isPasswordValid || !isMatch}
          >
            {loading ? <span className="spinner spinner-light" /> : copy.resetButton}
          </button>
        </form>
      )}
    </section>
  );
}
