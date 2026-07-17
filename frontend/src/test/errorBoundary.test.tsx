import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ErrorBoundary } from "../app/ErrorBoundary";

function Bomb({ shouldThrow }: { shouldThrow: boolean }): React.ReactElement {
  if (shouldThrow) throw new Error("Deliberate test error");
  return <p>App is working</p>;
}

// Suppress the expected console.error from componentDidCatch in test output.
const suppressError = vi.spyOn(console, "error").mockImplementation(() => undefined);

describe("ErrorBoundary fallback", () => {
  it("renders children when there is no error", () => {
    render(
      <ErrorBoundary>
        <Bomb shouldThrow={false} />
      </ErrorBoundary>,
    );
    expect(screen.getByText("App is working")).toBeInTheDocument();
  });

  it("renders the styled fallback when a child throws", () => {
    render(
      <ErrorBoundary>
        <Bomb shouldThrow={true} />
      </ErrorBoundary>,
    );
    expect(screen.getByRole("alert")).toBeInTheDocument();
    expect(screen.getByText("Something went wrong")).toBeInTheDocument();
  });

  it("does not render any stack trace or technical detail", () => {
    render(
      <ErrorBoundary>
        <Bomb shouldThrow={true} />
      </ErrorBoundary>,
    );
    expect(screen.queryByText(/Deliberate test error/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/at Bomb/i)).not.toBeInTheDocument();
  });

  it("renders a keyboard-accessible reload button", () => {
    render(
      <ErrorBoundary>
        <Bomb shouldThrow={true} />
      </ErrorBoundary>,
    );
    const reload = screen.getByRole("button", { name: "Reload page" });
    expect(reload).toBeInTheDocument();
    expect(reload).not.toBeDisabled();
  });

  it("renders a link to the dashboard", () => {
    render(
      <ErrorBoundary>
        <Bomb shouldThrow={true} />
      </ErrorBoundary>,
    );
    const homeLink = screen.getByRole("link", { name: "Return to dashboard" });
    expect(homeLink).toHaveAttribute("href", "/app");
  });

  it("calls window.location.reload when the reload button is clicked", async () => {
    const reloadMock = vi.fn();
    Object.defineProperty(window, "location", {
      value: { ...window.location, reload: reloadMock },
      writable: true,
    });
    render(
      <ErrorBoundary>
        <Bomb shouldThrow={true} />
      </ErrorBoundary>,
    );
    await userEvent.click(screen.getByRole("button", { name: "Reload page" }));
    expect(reloadMock).toHaveBeenCalledTimes(1);
  });

  it("shows Arabic copy when the locale is set to ar", () => {
    window.localStorage.setItem("rahfit.locale", "ar");
    render(
      <ErrorBoundary>
        <Bomb shouldThrow={true} />
      </ErrorBoundary>,
    );
    expect(screen.getByText("حدث خطأ غير متوقع")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "إعادة تحميل الصفحة" })).toBeInTheDocument();
    window.localStorage.removeItem("rahfit.locale");
  });

  it("falls back to English when locale is unknown", () => {
    window.localStorage.setItem("rahfit.locale", "fr");
    render(
      <ErrorBoundary>
        <Bomb shouldThrow={true} />
      </ErrorBoundary>,
    );
    expect(screen.getByText("Something went wrong")).toBeInTheDocument();
    window.localStorage.removeItem("rahfit.locale");
  });

  it("sets dir=rtl on the fallback root when locale is ar", () => {
    window.localStorage.setItem("rahfit.locale", "ar");
    render(
      <ErrorBoundary>
        <Bomb shouldThrow={true} />
      </ErrorBoundary>,
    );
    const alertEl = screen.getByRole("alert");
    expect(alertEl).toHaveAttribute("dir", "rtl");
    window.localStorage.removeItem("rahfit.locale");
  });

  afterEach(() => {
    suppressError.mockClear();
  });
});
