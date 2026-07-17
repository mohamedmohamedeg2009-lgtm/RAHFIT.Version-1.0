import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";

import { FormAlert } from "../../components/auth/FormAlert";
import { PasswordField } from "../../components/auth/PasswordField";
import { useAuth } from "../../hooks/useAuth";
import { GoogleSignInButton } from "../../components/auth/GoogleSignInButton";
import { useLocale } from "../../contexts/LocaleContext";

const passwordHint = "Use 12–128 characters. A longer, memorable phrase is best.";

export function RegisterPage() {
  const { register, error, clearError, isLoading } = useAuth();
  const { locale } = useLocale();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
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
    if (password.length < 12) {
      setFieldError("Your password must be at least 12 characters.");
      return;
    }
    if (password !== confirmation) {
      setFieldError("Passwords do not match.");
      return;
    }
    setFieldError(null);
    setPending(true);
    try {
      await register({ email: normalizedEmail, password });
      navigate("/app", { replace: true });
    } catch {
      // AuthContext provides a safe user-facing error without exposing server details.
    } finally {
      setPending(false);
    }
  };

  const hasGoogle = Boolean(import.meta.env.VITE_GOOGLE_CLIENT_ID);

  return (
    <section className="auth-card" aria-labelledby="register-title">
      <div className="mobile-brand">
        <p className="eyebrow">RAHFIT AI</p>
      </div>
      <p className="eyebrow">YOUR NEXT CHAPTER</p>
      <h2 id="register-title">Build a stronger routine.</h2>
      <p className="muted-text">Create your account. We’ll tailor the next steps later.</p>
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
          <label htmlFor="register-email">Email address</label>
          <input
            id="register-email"
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
          autoComplete="new-password"
          error={password ? undefined : undefined}
        />
        <p className="field-hint">{passwordHint}</p>
        <PasswordField
          label="Confirm password"
          value={confirmation}
          onChange={setConfirmation}
          autoComplete="new-password"
        />
        <button
          className="button button-primary button-full"
          type="submit"
          disabled={pending || isLoading}
        >
          {pending ? (
            <>
              <span className="spinner spinner-light" aria-hidden="true" /> Creating account…
            </>
          ) : (
            "Create account"
          )}
        </button>
      </form>
      <p className="auth-switch">
        Already have an account? <Link to="/login">Sign in</Link>
      </p>
    </section>
  );
}
