const refreshTokenKey = "rahfit.refresh-token";
/**
 * Competition compatibility only. TODO(backend-auth): move refresh-token delivery to a
 * Secure, HttpOnly, SameSite cookie and remove client-side persistence before production.
 */
export const tokenStore = {
  get: () => window.sessionStorage.getItem(refreshTokenKey),
  set: (token: string) => window.sessionStorage.setItem(refreshTokenKey, token),
  clear: () => window.sessionStorage.removeItem(refreshTokenKey),
};
