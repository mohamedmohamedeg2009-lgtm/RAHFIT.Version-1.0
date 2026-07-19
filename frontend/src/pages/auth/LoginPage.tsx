import { useRef, useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { FormAlert } from "../../components/auth/FormAlert";
import { PasswordField } from "../../components/auth/PasswordField";
import { useAuth } from "../../hooks/useAuth";
import { GoogleSignInButton } from "../../components/auth/GoogleSignInButton";
import { useLocale } from "../../contexts/LocaleContext";
import { RahafitLogo } from "../../components/common/RahafitLogo";

export function LoginPage() {
  const { login, error, clearError, isLoading } = useAuth();
  const { locale } = useLocale();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fieldError, setFieldError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const submittingRef = useRef(false);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (pending || isLoading || submittingRef.current) return;
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
    submittingRef.current = true;
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
      submittingRef.current = false;
      setPending(false);
    }
  };

  const hasGoogle = Boolean(import.meta.env.VITE_GOOGLE_CLIENT_ID);

  return (
    <section className="auth-card" aria-labelledby="login-title">
      <div className="mobile-brand">
        <RahafitLogo size="md" />
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
        New to Rahafit? <Link to="/register">Create an account</Link>
      </p>
    </section>
  );
}
