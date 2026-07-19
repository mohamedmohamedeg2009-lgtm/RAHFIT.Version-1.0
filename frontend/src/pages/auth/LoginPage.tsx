import { useRef, useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { FormAlert } from "../../components/auth/FormAlert";
import { PasswordField } from "../../components/auth/PasswordField";
import { useAuth } from "../../hooks/useAuth";
import { GoogleSignInButton } from "../../components/auth/GoogleSignInButton";
import { useLocale } from "../../contexts/LocaleContext";
import { FormErrorSummary } from "../../components/ui";
import { normalizeEmail, validateEmail, validatePasswordForLogin } from "../../utils/formValidation";

export function LoginPage() {
  const { login, error, clearError, isLoading } = useAuth();
  const { locale } = useLocale();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fieldError, setFieldError] = useState<{ email?: string; password?: string } | null>(null);
  const [pending, setPending] = useState(false);
  const submittingRef = useRef(false);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (pending || isLoading || submittingRef.current) return;
    clearError();
    const nextErrors = {
      email: validateEmail(email),
      password: validatePasswordForLogin(password),
    };
    if (nextErrors.email || nextErrors.password) {
      setFieldError(nextErrors);
      return;
    }
    setFieldError(null);
    submittingRef.current = true;
    setPending(true);
    try {
      await login({ email: normalizeEmail(email), password });
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
      <form onSubmit={(event) => void submit(event)} noValidate>
        <FormErrorSummary
          errors={Object.entries(fieldError ?? {}).flatMap(([field, message]) =>
            message ? [{ field: `login-${field}`, message }] : [],
          )}
        />
        <div className="field-group">
          <label htmlFor="login-email">Email address</label>
          <input
            id="login-email"
            type="email"
            value={email}
            autoComplete="email"
            onChange={(event) => {
              setEmail(event.target.value);
              setFieldError((current) => (current ? { ...current, email: undefined } : current));
            }}
            aria-invalid={Boolean(fieldError?.email)}
            aria-describedby={fieldError?.email ? "login-email-error" : undefined}
          />
          {fieldError?.email ? (
            <p id="login-email-error" className="field-error">
              {fieldError.email}
            </p>
          ) : null}
        </div>
        <PasswordField
          id="login-password"
          label="Password"
          value={password}
          onChange={(value) => {
            setPassword(value);
            setFieldError((current) => (current ? { ...current, password: undefined } : current));
          }}
          autoComplete="current-password"
          error={fieldError?.password}
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
