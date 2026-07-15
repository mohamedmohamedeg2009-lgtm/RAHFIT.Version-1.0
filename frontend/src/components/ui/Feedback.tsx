import type { ReactNode } from "react";

export type AlertVariant = "success" | "warning" | "danger" | "info";
interface AlertProps {
  variant?: AlertVariant;
  title?: string;
  children: ReactNode;
  onClose?: () => void;
}
export function Alert({ variant = "info", title, children, onClose }: AlertProps) {
  return (
    <div
      className={`ds-alert ds-alert-${variant}`}
      role={variant === "danger" ? "alert" : "status"}
    >
      <span className="ds-alert-icon" aria-hidden="true">
        {variant === "success"
          ? "✓"
          : variant === "warning"
            ? "!"
            : variant === "danger"
              ? "×"
              : "i"}
      </span>
      <div>
        {title ? <strong>{title}</strong> : null}
        <div>{children}</div>
      </div>
      {onClose ? (
        <button
          type="button"
          className="ds-alert-close"
          onClick={onClose}
          aria-label="Dismiss notification"
        >
          ×
        </button>
      ) : null}
    </div>
  );
}

export type EmptyStateKind = "generic" | "workout" | "nutrition" | "assessment" | "ai";
const emptyCopy: Record<EmptyStateKind, { title: string; message: string }> = {
  generic: {
    title: "Nothing here yet",
    message: "Your next step will appear here when it is ready.",
  },
  workout: { title: "No workout yet", message: "Your training plan will appear here after setup." },
  nutrition: {
    title: "No nutrition entries",
    message: "Log your first meal or glass of water to get started.",
  },
  assessment: {
    title: "Assessment not started",
    message: "A short assessment helps tailor your experience.",
  },
  ai: { title: "No coach messages", message: "Ask a thoughtful question when you are ready." },
};
export function EmptyState({
  kind = "generic",
  action,
}: {
  kind?: EmptyStateKind;
  action?: ReactNode;
}) {
  const copy = emptyCopy[kind];
  return (
    <section className="ds-empty" aria-live="polite">
      <span className="ds-empty-mark" aria-hidden="true">
        ◌
      </span>
      <h3>{copy.title}</h3>
      <p>{copy.message}</p>
      {action}
    </section>
  );
}

export type ErrorStateKind = "404" | "500" | "offline";
const errorCopy: Record<ErrorStateKind, { title: string; message: string }> = {
  "404": { title: "Page not found", message: "The page you requested is not available." },
  "500": {
    title: "Something went wrong",
    message: "Please try again. If this continues, contact support.",
  },
  offline: { title: "You are offline", message: "Check your connection and try again." },
};
export function ErrorState({
  kind = "500",
  action,
}: {
  kind?: ErrorStateKind;
  action?: ReactNode;
}) {
  const copy = errorCopy[kind];
  return (
    <section className="ds-error" role="alert">
      <h3>{copy.title}</h3>
      <p>{copy.message}</p>
      {action}
    </section>
  );
}
