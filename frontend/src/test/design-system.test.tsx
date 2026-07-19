import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom/vitest";

import { Button } from "../components/ui/Button";
import { LinearProgress } from "../components/ui/Progress";
import { ThemeProvider } from "../theme";

describe("design system primitives", () => {
  it("renders an accessible loading button", () => {
    render(<Button loading>Save</Button>);
    expect(screen.getByRole("button", { name: "Save" })).toBeDisabled();
    expect(screen.getByRole("button")).toHaveAttribute("aria-busy", "true");
  });

  it("exposes bounded progress semantics", () => {
    render(<LinearProgress value={120} max={100} label="Completion" />);
    expect(screen.getByRole("progressbar", { name: "Completion" })).toHaveAttribute(
      "aria-valuenow",
      "100",
    );
  });

  it("renders the app in permanent dark mode", () => {
    render(
      <ThemeProvider>
        <button type="button">Theme Probe</button>
      </ThemeProvider>,
    );

    expect(document.documentElement).toHaveAttribute("data-theme", "dark");
    expect(document.documentElement).toHaveStyle({ colorScheme: "dark" });
  });
});
