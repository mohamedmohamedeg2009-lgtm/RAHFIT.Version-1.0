import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import "@testing-library/jest-dom/vitest";
import type { ReactNode } from "react";

import { AuthContext } from "../contexts/AuthContext";
import { LocaleProvider } from "../contexts/LocaleContext";
import { ThemeProvider } from "../theme";
import { DiscoveryPage } from "../pages/discovery/DiscoveryPage";
import { LandingPage } from "../pages/public/LandingPage";
import { ProtectedRoute } from "../components/ProtectedRoute";
import type { AuthContextValue } from "../types/auth";

function mockAuthContext(overrides: Partial<AuthContextValue> = {}): AuthContextValue {
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

function TestProviders({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider>
      <LocaleProvider>{children}</LocaleProvider>
    </ThemeProvider>
  );
}

describe("Public Discovery & Landing Page Journey", () => {
  beforeEach(() => {
    window.localStorage.setItem("rahfit.locale", "ar");
  });

  it("renders /discover without authentication", async () => {
    render(
      <TestProviders>
        <AuthContext.Provider value={mockAuthContext()}>
          <MemoryRouter initialEntries={["/discover"]}>
            <Routes>
              <Route path="/discover" element={<DiscoveryPage />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      </TestProviders>,
    );

    expect(await screen.findByText("ابدأ رحلتك مع Rahfit")).toBeInTheDocument();
    expect(screen.getAllByText("أنشئ حسابك")[0]).toBeInTheDocument();
    expect(screen.getByText("استكشف المميزات")).toBeInTheDocument();
    expect(screen.getByText("كيف تعمل منصة Rahfit")).toBeInTheDocument();
    expect(screen.getByText("المناطق والخصائص الأساسية")).toBeInTheDocument();
    expect(screen.getByText("الأمان والتخصيص الذكي")).toBeInTheDocument();
    expect(screen.getByText("جاهز تبدأ خطوتك الأولى؟")).toBeInTheDocument();
  });

  it("navigates from Landing Page CTA to /discover", async () => {
    const userActions = userEvent.setup();
    render(
      <TestProviders>
        <AuthContext.Provider value={mockAuthContext()}>
          <MemoryRouter initialEntries={["/"]}>
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/discover" element={<p>Discovery Page Content</p>} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      </TestProviders>,
    );

    const exploreButton = screen.getAllByRole("link", { name: /استكشف/i })[0];
    expect(exploreButton).toBeInTheDocument();
    await userActions.click(exploreButton);

    expect(await screen.findByText("Discovery Page Content")).toBeInTheDocument();
  });

  it("navigates to Login directly from Landing Page Sign in button", async () => {
    const userActions = userEvent.setup();
    render(
      <TestProviders>
        <AuthContext.Provider value={mockAuthContext()}>
          <MemoryRouter initialEntries={["/"]}>
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/login" element={<p>Login Page View</p>} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      </TestProviders>,
    );

    const loginLink = screen.getAllByRole("link", { name: "تسجيل الدخول" })[0];
    await userActions.click(loginLink);

    expect(await screen.findByText("Login Page View")).toBeInTheDocument();
  });

  it("navigates from Discovery Page Register CTA to /register", async () => {
    const userActions = userEvent.setup();
    render(
      <TestProviders>
        <AuthContext.Provider value={mockAuthContext()}>
          <MemoryRouter initialEntries={["/discover"]}>
            <Routes>
              <Route path="/discover" element={<DiscoveryPage />} />
              <Route path="/register" element={<p>Register Screen</p>} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      </TestProviders>,
    );

    const registerCta = screen.getAllByRole("link", { name: /أنشئ حسابك/i })[0];
    await userActions.click(registerCta);

    expect(await screen.findByText("Register Screen")).toBeInTheDocument();
  });

  it("navigates from Discovery Page Login CTA ('لدي حساب بالفعل') to /login", async () => {
    const userActions = userEvent.setup();
    render(
      <TestProviders>
        <AuthContext.Provider value={mockAuthContext()}>
          <MemoryRouter initialEntries={["/discover"]}>
            <Routes>
              <Route path="/discover" element={<DiscoveryPage />} />
              <Route path="/login" element={<p>Login Screen</p>} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      </TestProviders>,
    );

    const loginCta = screen.getByRole("link", { name: /لدي حساب بالفعل/i });
    await userActions.click(loginCta);

    expect(await screen.findByText("Login Screen")).toBeInTheDocument();
  });

  it("keeps protected routes (/app) protected for unauthenticated users", async () => {
    render(
      <TestProviders>
        <AuthContext.Provider value={mockAuthContext({ user: null })}>
          <MemoryRouter initialEntries={["/app"]}>
            <Routes>
              <Route element={<ProtectedRoute />}>
                <Route path="/app" element={<p>Protected App Content</p>} />
              </Route>
              <Route path="/login" element={<p>Login Required Screen</p>} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      </TestProviders>,
    );

    await waitFor(() => {
      expect(screen.getByText("Login Required Screen")).toBeInTheDocument();
      expect(screen.queryByText("Protected App Content")).not.toBeInTheDocument();
    });
  });

  it("renders Arabic RTL correctly when Arabic locale is selected", async () => {
    render(
      <TestProviders>
        <AuthContext.Provider value={mockAuthContext()}>
          <MemoryRouter initialEntries={["/discover"]}>
            <Routes>
              <Route path="/discover" element={<DiscoveryPage />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      </TestProviders>,
    );

    const mainShell = screen.getByRole("banner").closest(".public-shell");
    expect(mainShell).toHaveAttribute("dir", "rtl");
  });
});
