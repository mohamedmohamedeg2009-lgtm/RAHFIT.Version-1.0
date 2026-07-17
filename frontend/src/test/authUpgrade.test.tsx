import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import "@testing-library/jest-dom/vitest";
import * as React from "react";

import { AuthContext } from "../contexts/AuthContext";
import ForgotPasswordPage from "../pages/auth/ForgotPasswordPage";
import ResetPasswordPage from "../pages/auth/ResetPasswordPage";
import { GoogleSignInButton } from "../components/auth/GoogleSignInButton";
import type { AuthContextValue } from "../types/auth";

// Mock authService api calls
vi.mock("../services/authService", () => {
  return {
    authService: {
      forgotPassword: vi.fn().mockResolvedValue({ message: "Success" }),
      resetPassword: vi.fn().mockResolvedValue({ message: "Success" }),
    },
  };
});

vi.mock("../contexts/LocaleContext", () => {
  return {
    useLocale: () => ({
      locale: "en",
      setLocale: vi.fn(),
    }),
    LocaleProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  };
});

function context(overrides: Partial<AuthContextValue> = {}): AuthContextValue {
  return {
    user: null,
    isLoading: false,
    error: null,
    login: vi.fn(),
    register: vi.fn(),
    loginWithGoogle: vi.fn(),
    logout: vi.fn(),
    clearError: vi.fn(),
    ...overrides,
  };
}

describe("auth upgrade client components", () => {
  it("renders Google Sign-in button when configuration is present", () => {
    // Inject VITE_GOOGLE_CLIENT_ID mock
    import.meta.env.VITE_GOOGLE_CLIENT_ID = "test-client-id";

    render(
      <AuthContext.Provider value={context()}>
        <MemoryRouter>
          <GoogleSignInButton />
        </MemoryRouter>
      </AuthContext.Provider>,
    );

    // GIS button container should be rendered
    expect(document.querySelector(".google-btn-container")).toBeInTheDocument();
  });

  it("forgot password screen renders instructions and displays generic success message upon submission", async () => {
    const userActions = userEvent.setup();
    render(
      <AuthContext.Provider value={context()}>
        <MemoryRouter>
          <ForgotPasswordPage />
        </MemoryRouter>
      </AuthContext.Provider>,
    );

    expect(screen.getByText(/forgot password/i)).toBeInTheDocument();

    const emailInput = screen.getByLabelText(/email address/i);
    await userActions.type(emailInput, "user@example.com");
    await userActions.click(screen.getByRole("button", { name: /send reset link/i }));

    await waitFor(() => {
      expect(screen.getByText(/link has been sent/i)).toBeInTheDocument();
    });
  });

  it("reset password screen validates matching and password strength", async () => {
    const userActions = userEvent.setup();
    render(
      <AuthContext.Provider value={context()}>
        <MemoryRouter initialEntries={["/reset-password?token=valid-token"]}>
          <Routes>
            <Route path="/reset-password" element={<ResetPasswordPage />} />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>,
    );

    expect(screen.getByRole("heading", { name: /reset password/i })).toBeInTheDocument();

    const passInput = screen.getByLabelText(/^new password$/i);
    const confirmInput = screen.getByLabelText(/^confirm new password$/i);

    // Password < 12 characters is invalid
    await userActions.type(passInput, "short");
    await userActions.type(confirmInput, "short");
    expect(screen.getByRole("button", { name: /reset password/i })).toBeDisabled();

    // Mismatched confirmation is invalid
    await userActions.clear(passInput);
    await userActions.clear(confirmInput);
    await userActions.type(passInput, "long-enough-password-123");
    await userActions.type(confirmInput, "mismatching-password-456");
    expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /reset password/i })).toBeDisabled();
  });
});
