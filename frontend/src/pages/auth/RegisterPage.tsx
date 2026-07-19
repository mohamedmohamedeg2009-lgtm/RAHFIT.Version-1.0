import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";

import { FormAlert } from "../../components/auth/FormAlert";
import { PasswordField } from "../../components/auth/PasswordField";
import { useAuth } from "../../hooks/useAuth";
import { GoogleSignInButton } from "../../components/auth/GoogleSignInButton";
import { useLocale } from "../../contexts/LocaleContext";
import { useDocumentTitle } from "../../hooks/useDocumentTitle";
import { FormErrorSummary } from "../../components/ui";
import {
  normalizeEmail,
  validateEmail,
  validatePasswordForRegistration,
} from "../../utils/formValidation";

const passwordHint = "Use 12–128 characters. A longer, memorable phrase is best.";

export function RegisterPage() {
  const { register, error, clearError, isLoading } = useAuth();
  const { locale } = useLocale();
  useDocumentTitle("Rahafit");
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [fieldError, setFieldError] = useState<{
    email?: string;
    password?: string;
    confirmation?: string;
  } | null>(null);
  const [pending, setPending] = useState(false);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    clearError();
    const nextErrors = {
      email: validateEmail(email),
      password: validatePasswordForRegistration(password),
      confirmation: confirmation
        ? password === confirmation
          ? undefined
          : "Passwords do not match."
        : "Confirm your password.",
    };
    if (nextErrors.email || nextErrors.password || nextErrors.confirmation) {
      setFieldError(nextErrors);
      return;
    }
    setFieldError(null);
    setPending(true);
    try {
      await register({ email: normalizeEmail(email), password });
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
      <form onSubmit={(event) => void submit(event)} noValidate>
        <FormErrorSummary
          errors={Object.entries(fieldError ?? {}).flatMap(([field, message]) =>
            message ? [{ field: `register-${field === "confirmation" ? "confirmation" : field}`, message }] : [],
          )}
        />
        <div className="field-group">
          <label htmlFor="register-email">Email address</label>
          <input
            id="register-email"
            type="email"
            value={email}
            autoComplete="email"
            onChange={(event) => {
              setEmail(event.target.value);
              setFieldError((current) => (current ? { ...current, email: undefined } : current));
            }}
            aria-invalid={Boolean(fieldError?.email)}
            aria-describedby={fieldError?.email ? "register-email-error" : undefined}
          />
          {fieldError?.email ? <p id="register-email-error" className="field-error">{fieldError.email}</p> : null}
        </div>
        <PasswordField
          id="register-password"
          label="Password"
          value={password}
          onChange={(value) => {
            setPassword(value);
            setFieldError((current) => ({
              ...current,
              password: undefined,
              confirmation:
                confirmation && value !== confirmation ? "Passwords do not match." : undefined,
            }));
          }}
          autoComplete="new-password"
          error={password ? undefined : undefined}
        />
        <p className="field-hint">{passwordHint}</p>
        <PasswordField
          id="register-confirmation"
          label="Confirm password"
          value={confirmation}
          onChange={(value) => {
            setConfirmation(value);
            setFieldError((current) => ({
              ...current,
              confirmation: value && value === password ? undefined : current?.confirmation,
            }));
          }}
          autoComplete="new-password"
          error={fieldError?.confirmation}
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
