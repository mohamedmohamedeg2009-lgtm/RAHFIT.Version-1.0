import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ProtectedRoute } from "../components/ProtectedRoute";
import { AuthContext } from "../contexts/AuthContext";
import { AuthLayout } from "../layouts/AuthLayout";
import { LoginPage } from "../pages/auth/LoginPage";
import { RegisterPage } from "../pages/auth/RegisterPage";
import { apiRequest, setAccessToken, setRefreshHandler } from "../services/apiClient";
import type { AuthContextValue, AuthUser } from "../types/auth";

const user: AuthUser = {
  id: "user-1",
  email: "user@example.com",
  is_active: true,
  created_at: "2026-01-01T00:00:00Z",
};

function context(overrides: Partial<AuthContextValue> = {}): AuthContextValue {
  return {
    user: null,
    isLoading: false,
    error: null,
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
    clearError: vi.fn(),
    ...overrides,
  };
}

describe("authentication pages", () => {
  it("shows login validation without making a request", async () => {
    const login = vi.fn();
    const userActions = userEvent.setup();
    render(
      <AuthContext.Provider value={context({ login })}>
        <MemoryRouter>
          <LoginPage />
        </MemoryRouter>
      </AuthContext.Provider>,
    );

    await userActions.click(screen.getByRole("button", { name: "Sign in" }));
    expect(screen.getByRole("alert")).toHaveTextContent("valid email address");
    expect(login).not.toHaveBeenCalled();
  });

  it("validates password confirmation during registration", async () => {
    const register = vi.fn();
    const userActions = userEvent.setup();
    render(
      <AuthContext.Provider value={context({ register })}>
        <MemoryRouter>
          <RegisterPage />
        </MemoryRouter>
      </AuthContext.Provider>,
    );

    await userActions.type(screen.getByLabelText("Email address"), "user@example.com");
    await userActions.type(screen.getByLabelText("Password"), "a-strong-password");
    await userActions.type(screen.getByLabelText("Confirm password"), "different-password");
    await userActions.click(screen.getByRole("button", { name: "Create account" }));
    expect(screen.getByRole("alert")).toHaveTextContent("Passwords do not match");
    expect(register).not.toHaveBeenCalled();
  });
});

describe("authentication routing", () => {
  it("redirects an unauthenticated user from protected routes", () => {
    render(
      <AuthContext.Provider value={context()}>
        <MemoryRouter initialEntries={["/app"]}>
          <Routes>
            <Route element={<ProtectedRoute />}>
              <Route path="/app" element={<p>Protected content</p>} />
            </Route>
            <Route path="/login" element={<p>Login destination</p>} />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>,
    );

    expect(screen.getByText("Login destination")).toBeInTheDocument();
    expect(screen.queryByText("Protected content")).not.toBeInTheDocument();
  });

  it("redirects an authenticated user away from authentication pages", () => {
    render(
      <AuthContext.Provider value={context({ user })}>
        <MemoryRouter initialEntries={["/login"]}>
          <Routes>
            <Route element={<AuthLayout />}>
              <Route path="/login" element={<p>Login page</p>} />
            </Route>
            <Route path="/app" element={<p>Protected destination</p>} />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>,
    );

    expect(screen.getByText("Protected destination")).toBeInTheDocument();
    expect(screen.queryByText("Login page")).not.toBeInTheDocument();
  });

  it("shows the session-restoration state while loading", () => {
    render(
      <AuthContext.Provider value={context({ isLoading: true })}>
        <MemoryRouter initialEntries={["/app"]}>
          <Routes>
            <Route element={<ProtectedRoute />}>
              <Route path="/app" element={<p>Protected content</p>} />
            </Route>
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>,
    );

    expect(screen.getByText("Restoring your session…")).toBeInTheDocument();
  });
});

describe("api refresh boundary", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    setAccessToken(null);
    setRefreshHandler(null);
  });

  it("refreshes once and retries an expired access token", async () => {
    setAccessToken("expired-access");
    const refresh = vi.fn(async () => {
      setAccessToken("fresh-access");
      return true;
    });
    setRefreshHandler(refresh);
    const fetchMock = vi
      .spyOn(window, "fetch")
      .mockResolvedValueOnce(new Response(JSON.stringify({ message: "expired" }), { status: 401 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ ok: true }), { status: 200 }));

    await expect(apiRequest<{ ok: boolean }>("/auth/me")).resolves.toEqual({ ok: true });
    expect(refresh).toHaveBeenCalledTimes(1);
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("does not retry when refresh fails", async () => {
    setAccessToken("expired-access");
    setRefreshHandler(vi.fn(async () => false));
    const fetchMock = vi
      .spyOn(window, "fetch")
      .mockResolvedValue(new Response(JSON.stringify({ message: "expired" }), { status: 401 }));

    await expect(apiRequest("/auth/me")).rejects.toMatchObject({ status: 401 });
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
});
