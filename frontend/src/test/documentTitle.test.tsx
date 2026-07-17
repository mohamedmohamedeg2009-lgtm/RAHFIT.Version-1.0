import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it } from "vitest";

import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { LocaleProvider, useLocale } from "../contexts/LocaleContext";

function TestPage({ title }: { title: string }) {
  useDocumentTitle(title);
  return <p>Page Content: {title}</p>;
}

function LocaleSwitcherAndTitle({ en, ar }: { en: string; ar: string }) {
  const { locale, toggleLocale } = useLocale();
  useDocumentTitle(locale === "ar" ? ar : en);
  return <button onClick={toggleLocale}>Toggle Locale</button>;
}

describe("document title hook and router integration", () => {
  beforeEach(() => {
    document.title = "RAHFIT AI";
    window.localStorage.removeItem("rahfit.locale");
  });

  it("sets the document title on mount and restores default on unmount", () => {
    const { unmount } = render(<TestPage title="Dashboard" />);
    expect(document.title).toBe("Dashboard — RAHFIT AI");
    unmount();
    expect(document.title).toBe("RAHFIT AI");
  });

  it("updates title dynamically when language changes", async () => {
    render(
      <LocaleProvider>
        <LocaleSwitcherAndTitle en="Dashboard" ar="لوحة التحكم" />
      </LocaleProvider>,
    );

    // Default locale (en) is loaded first
    expect(document.title).toBe("Dashboard — RAHFIT AI");

    // Click the toggle button to switch to ar
    await userEvent.click(screen.getByRole("button", { name: "Toggle Locale" }));

    // The title should update to Arabic
    await waitFor(() => {
      expect(document.title).toBe("لوحة التحكم — RAHFIT AI");
    });

    // Toggle back to en
    await userEvent.click(screen.getByRole("button", { name: "Toggle Locale" }));
    await waitFor(() => {
      expect(document.title).toBe("Dashboard — RAHFIT AI");
    });
  });
});
