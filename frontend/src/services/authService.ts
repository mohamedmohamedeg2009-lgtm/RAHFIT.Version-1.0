import { apiRequest, setAccessToken } from "./apiClient";
import { tokenStore } from "./tokenStore";
import type { AuthCredentials, AuthTokens, AuthUser } from "../types/auth";
interface ApiTokens {
  access_token: string;
  refresh_token: string;
  access_token_expires_in: number;
}
function save(tokens: ApiTokens): AuthTokens {
  setAccessToken(tokens.access_token);
  tokenStore.set(tokens.refresh_token);
  return {
    accessToken: tokens.access_token,
    refreshToken: tokens.refresh_token,
    accessTokenExpiresIn: tokens.access_token_expires_in,
  };
}
export const authService = {
  register: async (credentials: AuthCredentials) =>
    save(await apiRequest<ApiTokens>("/auth/register", { method: "POST", body: credentials })),
  login: async (credentials: AuthCredentials) =>
    save(await apiRequest<ApiTokens>("/auth/login", { method: "POST", body: credentials })),
  loginWithGoogle: async (credential: string) =>
    save(await apiRequest<ApiTokens>("/auth/google", { method: "POST", body: { credential } })),
  forgotPassword: (email: string) =>
    apiRequest<{ message: string }>("/auth/forgot-password", { method: "POST", body: { email } }),
  resetPassword: (token: string, password: string, passwordConfirmation: string) =>
    apiRequest<{ message: string }>("/auth/reset-password", {
      method: "POST",
      body: { token, password, password_confirmation: passwordConfirmation },
    }),
  async refreshSession() {
    const refreshToken = tokenStore.get();
    if (!refreshToken) return false;
    try {
      save(
        await apiRequest<ApiTokens>("/auth/refresh", {
          method: "POST",
          body: { refresh_token: refreshToken },
          skipRefresh: true,
        }),
      );
      return true;
    } catch {
      this.clearSession();
      return false;
    }
  },
  getCurrentUser: () => apiRequest<AuthUser>("/auth/me"),
  async logout() {
    try {
      await apiRequest("/auth/logout", { method: "POST", skipRefresh: true });
    } finally {
      this.clearSession();
    }
  },
  clearSession() {
    setAccessToken(null);
    tokenStore.clear();
  },
};
