import { createContext, useCallback, useEffect, useState, type ReactNode } from "react";

import {
  ApiConfigurationError,
  ApiConnectionError,
  ApiError,
  setRefreshHandler,
} from "../services/apiClient";
import { authService } from "../services/authService";
import type { AuthContextValue, AuthCredentials, AuthUser } from "../types/auth";

// eslint-disable-next-line react-refresh/only-export-components
export const AuthContext = createContext<AuthContextValue | null>(null);

function userMessage(error: unknown): string {
  if (error instanceof ApiConfigurationError) {
    return "The application service is not configured. Please contact the administrator.";
  }
  if (error instanceof ApiConnectionError) {
    return error.code === "request_timeout"
      ? "The service took too long to respond. Please try again."
      : "We could not reach the service. Please try again.";
  }
  if (error instanceof ApiError) {
    if (error.status === 409) return "An account already exists for this email.";
    if (error.status === 422 || error.code === "validation_error") {
      return "Please check your email and password and try again.";
    }
    if (error.status === 429) return "Too many attempts. Please try again shortly.";
    if (error.status >= 500) return "The service is temporarily unavailable. Please try again.";
    return error.message;
  }
  return "Something went wrong while processing your request. Please try again.";
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const restore = useCallback(async () => {
    if (!(await authService.refreshSession())) return false;
    try {
      // A second refresh from this restoration path would recurse through this callback.
      setUser(await authService.getCurrentUser(true));
      return true;
    } catch {
      authService.clearSession();
      setUser(null);
      return false;
    }
  }, []);

  useEffect(() => {
    setRefreshHandler(restore);
    // The restoration callback updates auth state after the external session check completes.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void restore().finally(() => {
      // Session restoration is an asynchronous external synchronization step.
      setIsLoading(false);
    });
    return () => setRefreshHandler(null);
  }, [restore]);

  const authenticate = useCallback(
    async (action: (value: AuthCredentials) => Promise<unknown>, credentials: AuthCredentials) => {
      setError(null);
      await action(credentials);
      setUser(await authService.getCurrentUser());
    },
    [],
  );

  const login = useCallback(
    async (credentials: AuthCredentials) => {
      try {
        await authenticate(authService.login, credentials);
      } catch (cause) {
        authService.clearSession();
        const text = userMessage(cause);
        setError(text);
        throw new Error(text, { cause });
      }
    },
    [authenticate],
  );

  const register = useCallback(
    async (credentials: AuthCredentials) => {
      try {
        await authenticate(authService.register, credentials);
      } catch (cause) {
        authService.clearSession();
        const text = userMessage(cause);
        setError(text);
        throw new Error(text, { cause });
      }
    },
    [authenticate],
  );

  const loginWithGoogle = useCallback(async (credential: string) => {
    setError(null);
    try {
      await authService.loginWithGoogle(credential);
      setUser(await authService.getCurrentUser());
    } catch (cause) {
      authService.clearSession();
      const text = userMessage(cause);
      setError(text);
      throw new Error(text, { cause });
    }
  }, []);

  const logout = useCallback(async () => {
    setError(null);
    try {
      await authService.logout();
    } finally {
      setUser(null);
    }
  }, []);

  const clearError = useCallback(() => setError(null), []);
  const value: AuthContextValue = {
    user,
    isLoading,
    error,
    login,
    register,
    loginWithGoogle,
    logout,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
