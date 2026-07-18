import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import "@testing-library/jest-dom/vitest";
import * as React from "react";

import { ProtectedRoute } from "../components/ProtectedRoute";

vi.mock("../contexts/LocaleContext", () => {
  return {
    useLocale: () => ({
      locale: "en",
      setLocale: vi.fn(),
    }),
    LocaleProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  };
});

import { AuthContext, AuthProvider } from "../contexts/AuthContext";
import { AuthLayout } from "../layouts/AuthLayout";
import { LoginPage } from "../pages/auth/LoginPage";
import { RegisterPage } from "../pages/auth/RegisterPage";
import {
  apiRequest,
  buildApiRequestUrl,
  normalizeApiBaseUrl,
  setAccessToken,
  setRefreshHandler,
} from "../services/apiClient";
import { authService } from "../services/authService";
import { tokenStore } from "../services/tokenStore";
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
    loginWithGoogle: vi.fn(),
    logout: vi.fn(),
    clearError: vi.fn(),
    ...overrides,
  };
}

async function submitRegistration(): Promise<void> {
  const actions = userEvent.setup();
  const button = screen.getByRole("button", { name: "Create account" });
  await waitFor(() => expect(button).not.toBeDisabled());
  await actions.type(screen.getByLabelText("Email address"), "new@example.com");
  await actions.type(screen.getByLabelText("Password"), "secure-password-123");
  await actions.type(screen.getByLabelText("Confirm password"), "secure-password-123");
  await actions.click(button);
}

function renderRegistration(): void {
  render(
    <AuthProvider>
      <MemoryRouter initialEntries={["/register"]}>
        <Routes>
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/app" element={<p>Registration complete</p>} />
        </Routes>
      </MemoryRouter>
    </AuthProvider>,
  );
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

  it("prevents duplicate login submissions while a request is pending", async () => {
    let resolveLogin: (() => void) | undefined;
    const login = vi.fn(
      () =>
        new Promise<void>((resolve) => {
          resolveLogin = resolve;
        }),
    );
    const userActions = userEvent.setup();
    render(
      <AuthContext.Provider value={context({ login })}>
        <MemoryRouter>
          <LoginPage />
        </MemoryRouter>
      </AuthContext.Provider>,
    );

    await userActions.type(screen.getByLabelText("Email address"), "user@example.com");
    await userActions.type(screen.getByLabelText("Password"), "secure-password-123");
    const form = screen.getByRole("button", { name: "Sign in" }).closest("form");
    expect(form).not.toBeNull();

    fireEvent.submit(form!);
    fireEvent.submit(form!);

    await waitFor(() => expect(login).toHaveBeenCalledTimes(1));
    resolveLogin?.();
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

  it("does not start a nested refresh for a session-restoration request", async () => {
    setAccessToken("fresh-access");
    const refresh = vi.fn(async () => true);
    setRefreshHandler(refresh);
    const fetchMock = vi
      .spyOn(window, "fetch")
      .mockResolvedValue(new Response(JSON.stringify({ message: "expired" }), { status: 401 }));

    await expect(apiRequest("/auth/me", { skipRefresh: true })).rejects.toMatchObject({ status: 401 });
    expect(refresh).not.toHaveBeenCalled();
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
    expect(request?.method).toBe("POST");
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

  it("persists a successful login session and clears it when logout fails", async () => {
    const fetchMock = vi
      .spyOn(window, "fetch")
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            access_token: "access",
            refresh_token: "refresh",
            access_token_expires_in: 1800,
          }),
          { status: 200 },
        ),
      )
      .mockResolvedValueOnce(new Response(JSON.stringify({ message: "unavailable" }), { status: 503 }));

    await authService.login({ email: "user@example.com", password: "secure-password-123" });
    expect(tokenStore.get()).toBe("refresh");

    await expect(authService.logout()).rejects.toMatchObject({ status: 503 });
    expect(tokenStore.get()).toBeNull();
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("restores a session from its persisted refresh token after reload", async () => {
    tokenStore.set("persisted-refresh");
    const fetchMock = vi
      .spyOn(window, "fetch")
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            access_token: "restored-access",
            refresh_token: "rotated-refresh",
            access_token_expires_in: 1800,
          }),
          { status: 200 },
        ),
      )
      .mockResolvedValueOnce(new Response(JSON.stringify(user), { status: 200 }));

    function SessionHarness() {
      const auth = React.useContext(AuthContext);
      return <p>{auth?.user?.email ?? "No session"}</p>;
    }

    render(
      <AuthProvider>
        <SessionHarness />
      </AuthProvider>,
    );

    expect(await screen.findByText("user@example.com")).toBeInTheDocument();
    expect(tokenStore.get()).toBe("rotated-refresh");
    expect(String(fetchMock.mock.calls[0][0])).toContain("/auth/refresh");
    expect(String(fetchMock.mock.calls[1][0])).toContain("/auth/me");
  });

  it("clears persisted tokens when refresh fails", async () => {
    tokenStore.set("expired-refresh");
    vi.spyOn(window, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ message: "expired" }), { status: 401 }),
    );

    await expect(authService.refreshSession()).resolves.toBe(false);
    expect(tokenStore.get()).toBeNull();
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

  it("normalizes the documented API base URL without duplicating separators", () => {
    expect(normalizeApiBaseUrl(undefined)).toBe("http://127.0.0.1:8000/api/v1");
    expect(normalizeApiBaseUrl("http://localhost:8000/api/v1/")).toBe(
      "http://localhost:8000/api/v1",
    );
    expect(() => normalizeApiBaseUrl("http://localhost:8000")).toThrow("/api/v1");
    expect(() => normalizeApiBaseUrl("not-a-url")).toThrow("valid absolute URL");
  });

  it("requires an explicit HTTPS backend URL in production", () => {
    expect(() => normalizeApiBaseUrl(undefined, "production")).toThrow("must be set");
    expect(() => normalizeApiBaseUrl("/api/v1", "production")).toThrow("public HTTPS");
    expect(() => normalizeApiBaseUrl("http://api.example.com/api/v1", "production")).toThrow(
      "must use HTTPS",
    );
    expect(normalizeApiBaseUrl("https://api.example.com/api/v1/", "production")).toBe(
      "https://api.example.com/api/v1",
    );
  });

  it("builds an endpoint once without repeating the API version prefix", () => {
    expect(buildApiRequestUrl("https://api.example.com/api/v1", "/auth/register")).toBe(
      "https://api.example.com/api/v1/auth/register",
    );
    expect(() => buildApiRequestUrl("https://api.example.com/api/v1", "/api/v1/auth/register"))
      .toThrow("must not repeat");
  });

  it("completes registration and loads the created current user", async () => {
    vi.spyOn(window, "fetch")
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            access_token: "access",
            refresh_token: "refresh",
            access_token_expires_in: 1800,
          }),
          { status: 201, headers: { "Content-Type": "application/json" } },
        ),
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify(user), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      );
    renderRegistration();

    await submitRegistration();

    expect(await screen.findByText("Registration complete")).toBeInTheDocument();
  });

  it("displays the duplicate-email conflict safely", async () => {
    vi.spyOn(window, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          code: "http_error",
          message: "An account already exists for this email.",
        }),
        { status: 409, headers: { "Content-Type": "application/json" } },
      ),
    );
    renderRegistration();

    await submitRegistration();

    expect(
      await screen.findByText("An account already exists for this email."),
    ).toBeInTheDocument();
  });

  it("displays backend validation separately from connectivity failures", async () => {
    vi.spyOn(window, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({ code: "validation_error", message: "Invalid request input." }),
        { status: 422, headers: { "Content-Type": "application/json" } },
      ),
    );
    renderRegistration();

    await submitRegistration();

    expect(
      await screen.findByText("Please check your email and password and try again."),
    ).toBeInTheDocument();
    expect(screen.queryByText(/could not reach/i)).not.toBeInTheDocument();
  });

  it("does not classify a backend 500 response as a network failure", async () => {
    vi.spyOn(window, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ code: "internal_error", message: "Internal detail" }), {
        status: 500,
        headers: { "Content-Type": "application/json" },
      }),
    );
    renderRegistration();

    await submitRegistration();

    expect(
      await screen.findByText("The service is temporarily unavailable. Please try again."),
    ).toBeInTheDocument();
    expect(screen.queryByText(/could not reach/i)).not.toBeInTheDocument();
    expect(screen.queryByText("Internal detail")).not.toBeInTheDocument();
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
