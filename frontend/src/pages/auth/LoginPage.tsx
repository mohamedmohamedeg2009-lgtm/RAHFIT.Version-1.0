import { useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { FormAlert } from "../../components/auth/FormAlert";
import { PasswordField } from "../../components/auth/PasswordField";
import { useAuth } from "../../hooks/useAuth";
import { GoogleSignInButton } from "../../components/auth/GoogleSignInButton";
import { useLocale } from "../../contexts/LocaleContext";

export function LoginPage() {
  const { login, error, clearError, isLoading } = useAuth();
  const { locale } = useLocale();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fieldError, setFieldError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    clearError();
    const normalizedEmail = email.trim().toLowerCase();
    if (!normalizedEmail || !normalizedEmail.includes("@")) {
      setFieldError("Enter a valid email address.");
      return;
    }
    if (!password) {
      setFieldError("Enter your password.");
      return;
    }
    setFieldError(null);
    setPending(true);
    try {
      await login({ email: normalizedEmail, password });
      const destination =
        typeof location.state === "object" && location.state && "from" in location.state
          ? String(location.state.from)
          : "/app";
      navigate(destination.startsWith("/") ? destination : "/app", { replace: true });
    } catch {
      // AuthContext provides a safe user-facing error without exposing tokens or server details.
    } finally {
      setPending(false);
    }
  };

  const hasGoogle = Boolean(import.meta.env.VITE_GOOGLE_CLIENT_ID);

  return (
    <section className="auth-card" aria-labelledby="login-title">
      <div className="mobile-brand">
        <p className="eyebrow">RAHFIT AI</p>
      </div>
      <p className="eyebrow">WELCOME BACK</p>
      <h2 id="login-title">Let’s keep your momentum.</h2>
      <p className="muted-text">Sign in to continue your coaching journey.</p>
      <GoogleSignInButton />
      {hasGoogle ? (
        <div className="auth-divider">
          {locale === "ar" ? "أو المتابعة بالبريد الإلكتروني" : "or continue with email"}
        </div>
      ) : null}
      <FormAlert message={error} />
      {fieldError ? <FormAlert message={fieldError} /> : null}
      <form onSubmit={(event) => void submit(event)} noValidate>
        <div className="field-group">
          <label htmlFor="login-email">Email address</label>
          <input
            id="login-email"
            type="email"
            value={email}
            autoComplete="email"
            onChange={(event) => setEmail(event.target.value)}
            aria-invalid={Boolean(fieldError && (!email || !email.includes("@")))}
          />
        </div>
        <PasswordField
          label="Password"
          value={password}
          onChange={setPassword}
          autoComplete="current-password"
        />
        <div
          style={{
            display: "flex",
            justifyContent: "flex-end",
            marginBottom: "1.5rem",
            marginTop: "-0.5rem",
          }}
        >
          <Link
            to="/forgot-password"
            style={{
              fontSize: "0.875rem",
              color: "var(--color-primary)",
              textDecoration: "none",
            }}
          >
            {locale === "ar" ? "هل نسيت كلمة المرور؟" : "Forgot password?"}
          </Link>
        </div>
        <button
          className="button button-primary button-full"
          type="submit"
          disabled={pending || isLoading}
        >
          {pending ? (
            <>
              <span className="spinner spinner-light" aria-hidden="true" /> Signing in…
            </>
          ) : (
            "Sign in"
          )}
        </button>
      </form>
      <p className="auth-switch">
        New to RAHFIT AI? <Link to="/register">Create an account</Link>
      </p>
    </section>
  );
}
