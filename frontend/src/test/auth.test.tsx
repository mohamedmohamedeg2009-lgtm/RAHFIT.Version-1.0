import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import "@testing-library/jest-dom/vitest";
import * as React from "react";

import { ProtectedRoute } from "../components/ProtectedRoute";
import { AuthContext, AuthProvider } from "../contexts/AuthContext";
import { AuthLayout } from "../layouts/AuthLayout";
import { LoginPage } from "../pages/auth/LoginPage";
import { RegisterPage } from "../pages/auth/RegisterPage";
import { apiRequest, setAccessToken, setRefreshHandler } from "../services/apiClient";
import { authService } from "../services/authService";
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

describe("authentication integration boundary", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    window.localStorage.clear();
    authService.clearSession();
  });

  it("register sends the configured API URL and backend request schema", async () => {
    const fetchMock = vi.spyOn(window, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          access_token: "access",
          refresh_token: "refresh",
          access_token_expires_in: 1800,
        }),
        { status: 201 },
      ),
    );

    await authService.register({ email: "new@example.com", password: "secure-password-123" });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url, request] = fetchMock.mock.calls[0];
    expect(String(url)).toBe("http://127.0.0.1:8000/api/v1/auth/register");
    expect(JSON.parse(String(request?.body))).toEqual({
      email: "new@example.com",
      password: "secure-password-123",
    });
  });

  it("login uses the login endpoint without an auth refresh request", async () => {
    const fetchMock = vi.spyOn(window, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          access_token: "access",
          refresh_token: "refresh",
          access_token_expires_in: 1800,
        }),
        { status: 200 },
      ),
    );

    await authService.login({ email: "user@example.com", password: "secure-password-123" });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(String(fetchMock.mock.calls[0][0])).toBe("http://127.0.0.1:8000/api/v1/auth/login");
  });

  it("keeps an HTTP conflict as an API error instead of a network error", async () => {
    vi.spyOn(window, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ code: "http_error", message: "Account already exists." }), {
        status: 409,
      }),
    );

    await expect(
      apiRequest("/auth/register", {
        method: "POST",
        body: { email: "user@example.com", password: "secure-password-123" },
      }),
    ).rejects.toMatchObject({ status: 409, message: "Account already exists." });
  });

  it("shows the connectivity message only for an actual fetch failure", async () => {
    vi.spyOn(window, "fetch").mockRejectedValue(new TypeError("Failed to fetch"));

    function FailureHarness() {
      const auth = React.useContext(AuthContext);
      return (
        <div>
          <button
            onClick={() =>
              void auth
                ?.register({ email: "user@example.com", password: "secure-password-123" })
                .catch(() => undefined)
            }
          >
            Register now
          </button>
          <p>{auth?.error}</p>
        </div>
      );
    }

    render(
      <AuthProvider>
        <FailureHarness />
      </AuthProvider>,
    );
    await userEvent.click(screen.getByRole("button", { name: "Register now" }));

    expect(
      await screen.findByText("We could not reach the service. Please try again."),
    ).toBeTruthy();
  });
});
