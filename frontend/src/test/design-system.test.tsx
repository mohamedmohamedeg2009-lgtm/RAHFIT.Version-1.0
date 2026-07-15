import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom/vitest";

import { Button } from "../components/ui/Button";
import { LinearProgress } from "../components/ui/Progress";
import { ThemeProvider, useTheme } from "../theme";

function ThemeProbe() {
  const { theme, toggleTheme } = useTheme();
  return <button onClick={toggleTheme}>{theme}</button>;
}

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

  it("provides controlled theme switching", async () => {
    const { userEvent } = await import("@testing-library/user-event");
    const user = userEvent.setup();
    render(
      <ThemeProvider>
        <ThemeProbe />
      </ThemeProvider>,
    );
    const toggle = screen.getByRole("button");
    expect(toggle).toHaveTextContent(/light|dark/);
    await user.click(toggle);
    expect(toggle).not.toHaveTextContent("light");
  });
});
