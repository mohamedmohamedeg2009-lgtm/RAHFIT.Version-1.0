import { Component, type ErrorInfo, type ReactNode } from "react";

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
}

const copy = {
  en: {
    title: "Something went wrong",
    message:
      "An unexpected problem occurred. No personal data has been lost. You can reload the page or return to the dashboard.",
    reload: "Reload page",
    home: "Return to dashboard",
  },
  ar: {
    title: "حدث خطأ غير متوقع",
    message:
      "واجه التطبيق مشكلة غير متوقعة. لم تُفقد أي بيانات شخصية. يمكنك إعادة تحميل الصفحة أو العودة إلى لوحة التحكم.",
    reload: "إعادة تحميل الصفحة",
    home: "العودة إلى لوحة التحكم",
  },
} as const;

function getLocale(): "ar" | "en" {
  try {
    const stored = window.localStorage.getItem("rahfit.locale");
    if (stored === "ar") return "ar";
  } catch {
    // localStorage may be unavailable in some environments.
  }
  return "en";
}

/** Prevents an uncaught render error from taking down the entire browser document. */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  public state: ErrorBoundaryState = { hasError: false };

  public static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Replace with an observability adapter when a provider is selected.
    console.error("Unhandled UI error", error, errorInfo);
  }

  public render(): ReactNode {
    if (!this.state.hasError) return this.props.children;

    const locale = getLocale();
    const t = copy[locale];
    const dir = locale === "ar" ? "rtl" : "ltr";

    return (
      <main
        role="alert"
        aria-live="assertive"
        dir={dir}
        lang={locale}
        style={{
          display: "grid",
          minHeight: "100vh",
          placeItems: "center",
          padding: "1.5rem",
          background: "var(--color-background, #f4f7f9)",
        }}
      >
        <section
          className="ds-card"
          style={{ maxWidth: "36rem", width: "100%", textAlign: "center" }}
          aria-labelledby="eb-title"
        >
          <span
            aria-hidden="true"
            style={{ fontSize: "2.5rem", display: "block", marginBottom: "1rem" }}
          >
            ⚠
          </span>
          <h1
            id="eb-title"
            style={{
              margin: "0 0 0.75rem",
              fontSize: "1.5rem",
              color: "var(--color-danger, #b24646)",
            }}
          >
            {t.title}
          </h1>
          <p style={{ margin: "0 0 1.5rem", color: "var(--color-text-secondary, #687984)" }}>
            {t.message}
          </p>
          <div
            style={{ display: "flex", gap: "0.75rem", justifyContent: "center", flexWrap: "wrap" }}
          >
            <button
              type="button"
              className="ds-button ds-button-primary ds-button-md"
              onClick={() => window.location.reload()}
              autoFocus
            >
              {t.reload}
            </button>
            <a className="ds-button ds-button-outline ds-button-md" href="/app">
              {t.home}
            </a>
          </div>
        </section>
      </main>
    );
  }
}
