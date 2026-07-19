import { useEffect, useRef, useState } from "react";
import { useAuth } from "../../hooks/useAuth";
import { useLocale } from "../../contexts/LocaleContext";

interface GoogleCredentialResponse {
  credential: string;
}

interface GoogleSignInOptions {
  client_id: string;
  callback: (response: GoogleCredentialResponse) => void;
}

interface GoogleButtonOptions {
  type: "standard";
  theme: "filled_dark";
  size: "large";
  text: "continue_with";
  shape: "rectangular";
  width: number;
  locale: "ar" | "en";
}

interface GoogleIdentityServices {
  accounts: {
    id: {
      initialize: (options: GoogleSignInOptions) => void;
      renderButton: (parent: HTMLElement, options: GoogleButtonOptions) => void;
    };
  };
}

declare global {
  interface Window {
    google?: GoogleIdentityServices;
  }
}

export function GoogleSignInButton() {
  const { loginWithGoogle } = useAuth();
  const { locale } = useLocale();
  const containerRef = useRef<HTMLDivElement>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

  useEffect(() => {
    if (!clientId) return;

    const initializeGoogle = () => {
      if (typeof window === "undefined" || !window.google) return;

      try {
        window.google.accounts.id.initialize({
          client_id: clientId,
          callback: async (response) => {
            setLoading(true);
            setError(null);
            try {
              await loginWithGoogle(response.credential);
            } catch {
              setError("Google sign-in is temporarily unavailable. Please use email and password.");
            } finally {
              setLoading(false);
            }
          },
        });

        if (containerRef.current) {
          window.google.accounts.id.renderButton(containerRef.current, {
            type: "standard",
            theme: "filled_dark",
            size: "large",
            text: "continue_with",
            shape: "rectangular",
            width: containerRef.current.clientWidth || 320,
            locale: locale === "ar" ? "ar" : "en",
          });
        }
      } catch {
        setError("Google sign-in is temporarily unavailable. Please use email and password.");
      }
    };

    if (window.google) {
      initializeGoogle();
    } else {
      const interval = setInterval(() => {
        if (window.google) {
          clearInterval(interval);
          initializeGoogle();
        }
      }, 500);
      return () => clearInterval(interval);
    }
  }, [clientId, loginWithGoogle, locale]);

  if (!clientId) return null;

  return (
    <div className="google-signin-wrapper" style={{ margin: "1rem 0" }}>
      {error ? (
        <div className="ds-alert ds-alert-danger" style={{ marginBottom: "1rem" }}>
          {error}
        </div>
      ) : null}
      <div
        ref={containerRef}
        className={`google-btn-container ${loading ? "google-btn-loading" : ""}`}
        style={{ minHeight: "44px", width: "100%", display: "flex", justifyContent: "center" }}
      />
      {loading ? (
        <div style={{ display: "flex", justifyContent: "center", marginTop: "0.5rem" }}>
          <span className="spinner spinner-light" />
        </div>
      ) : null}
    </div>
  );
}
