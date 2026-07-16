const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";
let accessToken: string | null = null;
let refreshHandler: (() => Promise<boolean>) | null = null;
let refreshing: Promise<boolean> | null = null;
export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly code = "request_failed",
    public readonly details: Array<Record<string, unknown>> = [],
  ) {
    super(message);
  }
}
export const setAccessToken = (token: string | null) => {
  accessToken = token;
};
export const setRefreshHandler = (handler: (() => Promise<boolean>) | null) => {
  refreshHandler = handler;
};
async function refreshOnce() {
  refreshing ??= (refreshHandler?.() ?? Promise.resolve(false)).finally(() => {
    refreshing = null;
  });
  return refreshing;
}
type ApiRequestOptions = Omit<RequestInit, "body"> & { body?: unknown; skipRefresh?: boolean };

export async function apiRequest<T>(path: string, options: ApiRequestOptions = {}): Promise<T> {
  const { body, headers, skipRefresh = false, ...init } = options;
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 12000);
  try {
    const response = await fetch(`${baseUrl}${path}`, {
      ...init,
      body: body === undefined ? undefined : JSON.stringify(body),
      credentials: "include",
      signal: controller.signal,
      headers: {
        Accept: "application/json",
        ...(body === undefined ? {} : { "Content-Type": "application/json" }),
        ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
        ...headers,
      },
    });
    if (response.status === 401 && accessToken && !skipRefresh && (await refreshOnce()))
      return apiRequest<T>(path, { ...options, skipRefresh: true });
    if (response.status === 204) return undefined as T;
    const payload: unknown = await response.json().catch(() => null);
    if (!response.ok) {
      const data = payload as {
        code?: string;
        message?: string;
        details?: Array<Record<string, unknown>>;
        detail?:
          string | { code?: string; message?: string; details?: Array<Record<string, unknown>> };
      } | null;
      const nested = typeof data?.detail === "object" ? data.detail : null;
      throw new ApiError(
        data?.message ??
          nested?.message ??
          (typeof data?.detail === "string" ? data.detail : null) ??
          "The request could not be completed.",
        response.status,
        data?.code ?? nested?.code,
        data?.details ?? nested?.details,
      );
    }
    return payload as T;
  } finally {
    window.clearTimeout(timeout);
  }
}
