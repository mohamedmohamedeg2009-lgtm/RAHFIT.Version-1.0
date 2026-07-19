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

    expect(await screen.findByText("ابدأ رحلتك مع Rahafit")).toBeInTheDocument();
    expect(screen.getAllByText("أنشئ حسابك")[0]).toBeInTheDocument();
    expect(screen.getAllByText("استكشف المميزات")[0]).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "رحلتك مع Rahafit في أربع خطوات" }),
    ).toBeInTheDocument();
    expect(screen.getAllByText("أنشئ حسابك")[0]).toBeInTheDocument();
    expect(screen.getByText("حدّد أهدافك وحالتك")).toBeInTheDocument();
    expect(screen.getByText("احصل على تجربة مخصصة")).toBeInTheDocument();
    expect(screen.getByText("تابع تقدمك يوميًا")).toBeInTheDocument();
    expect(screen.getByText("كل ما تحتاجه لتدريب أذكى وأكثر أمانًا")).toBeInTheDocument();
    expect(screen.getByText("التمرين الذكي والتوجيه التدريبي")).toBeInTheDocument();
    expect(screen.getAllByText("التقييم الذكي والإقرار الصحي")[0]).toBeInTheDocument();
    expect(screen.getByText("المدرب الذكي والتوجيه الآمن")).toBeInTheDocument();
    expect(screen.getByText("الأمان والتخصيص الذكي")).toBeInTheDocument();
    expect(screen.getByText("جاهز تبدأ رحلتك؟")).toBeInTheDocument();
  });

  it("renders redesigned Landing Page hero headline, copy, CTAs, and smartphone mockup without authentication", async () => {
    render(
      <TestProviders>
        <AuthContext.Provider value={mockAuthContext()}>
          <MemoryRouter initialEntries={["/"]}>
            <Routes>
              <Route path="/" element={<LandingPage />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      </TestProviders>,
    );

    expect(screen.getByText("تدريب رياضي آمن، ذكي، وبناءً على خصوصيتك")).toBeInTheDocument();
    expect(screen.getByText("ابدأ رحلتك مع Rahafit")).toBeInTheDocument();
    expect(
      screen.getByText(
        "تربط منصة Rahafit بين التخطيط الرياضي، متابعة التغذية، مؤشرات الاستشفاء، والتوجيه الذكي الذي يراعي أهدافك وحالتك في تجربة متكاملة واحدة.",
      ),
    ).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: /أنشئ حسابك/i })[0]).toBeInTheDocument();
    expect(screen.getAllByText("استكشف المميزات")[0]).toBeInTheDocument();
    expect(screen.getByText("تخطي إلى تسجيل الدخول")).toBeInTheDocument();
    expect(screen.getByLabelText("Rahafit App Demo Interface")).toBeInTheDocument();
    expect(screen.getByText("أمان وخصوصية")).toBeInTheDocument();
    expect(screen.getByText("ذكاء اصطناعي محلي")).toBeInTheDocument();
    expect(screen.getByText("متابعة شاملة")).toBeInTheDocument();
    expect(screen.getByText("دعم مستمر")).toBeInTheDocument();
  });

  it("navigates from Landing Page primary CTA ('أنشئ حسابك') to /register", async () => {
    const userActions = userEvent.setup();
    render(
      <TestProviders>
        <AuthContext.Provider value={mockAuthContext()}>
          <MemoryRouter initialEntries={["/"]}>
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/register" element={<p>Register Screen Content</p>} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      </TestProviders>,
    );

    const registerButton = screen.getAllByRole("link", { name: /أنشئ حسابك/i })[0];
    expect(registerButton).toBeInTheDocument();
    await userActions.click(registerButton);

    expect(await screen.findByText("Register Screen Content")).toBeInTheDocument();
  });

  it("navigates to Login directly from Landing Page Sign in link", async () => {
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

    const loginLink = screen.getByRole("link", { name: "تخطي إلى تسجيل الدخول" });
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

  it("renders PublicFooter with honest contact notice and no invented email or phone placeholders", async () => {
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

    expect(screen.getByText("معلومات التواصل قريباً.")).toBeInTheDocument();
    expect(screen.queryByText("support@rahafit.ai")).not.toBeInTheDocument();
    expect(screen.queryByText("+966 800 123 4567")).not.toBeInTheDocument();
  });

  it("renders the landing page in permanent dark mode", async () => {
    render(
      <TestProviders>
        <AuthContext.Provider value={mockAuthContext()}>
          <MemoryRouter initialEntries={["/"]}>
            <Routes>
              <Route path="/" element={<LandingPage />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      </TestProviders>,
    );

    expect(document.documentElement).toHaveAttribute("data-theme", "dark");
    expect(screen.queryByRole("button", { name: /theme|thème|ثيم/i })).not.toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "ابدأ رحلتك مع Rahafit" })).toBeInTheDocument();
    expect(screen.getByText("تدريب رياضي آمن، ذكي، وبناءً على خصوصيتك")).toBeInTheDocument();
  });
});
