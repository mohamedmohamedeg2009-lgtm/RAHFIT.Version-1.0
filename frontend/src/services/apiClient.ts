const localApiBaseUrl = "http://127.0.0.1:8000/api/v1";

export function normalizeApiBaseUrl(value: string | undefined): string {
  const candidate = value?.trim() || localApiBaseUrl;
  if (candidate.startsWith("/")) {
    const normalizedPath = candidate.replace(/\/+$/, "");
    if (!normalizedPath.endsWith("/api/v1")) {
      throw new Error("VITE_API_BASE_URL must include the /api/v1 prefix.");
    }
    return normalizedPath;
  }
  let parsed: URL;
  try {
    parsed = new URL(candidate);
  } catch {
    throw new Error("VITE_API_BASE_URL must be a valid absolute URL.");
  }
  if (!(["http:", "https:"] as string[]).includes(parsed.protocol)) {
    throw new Error("VITE_API_BASE_URL must use HTTP or HTTPS.");
  }
  const normalizedPath = parsed.pathname.replace(/\/+$/, "");
  if (!normalizedPath.endsWith("/api/v1")) {
    throw new Error("VITE_API_BASE_URL must include the /api/v1 prefix.");
  }
  parsed.pathname = normalizedPath;
  return parsed.toString().replace(/\/$/, "");
}

const baseUrl = normalizeApiBaseUrl(import.meta.env.VITE_API_BASE_URL);
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
export class ApiConnectionError extends Error {
  constructor(
    message: string,
    public readonly code: "network_or_cors_error" | "request_timeout",
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
type ApiRequestOptions = Omit<RequestInit, "body"> & {
  body?: unknown;
  skipRefresh?: boolean;
  retries?: number;
  retryDelay?: number;
};

export async function apiRequest<T>(path: string, options: ApiRequestOptions = {}): Promise<T> {
  const {
    body,
    headers,
    skipRefresh = false,
    retries = import.meta.env.MODE === "test" ? 0 : 2,
    retryDelay = 500,
    ...init
  } = options;
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 12000);

  if (options.signal) {
    if (options.signal.aborted) {
      window.clearTimeout(timeout);
      throw new ApiConnectionError("The request was cancelled.", "network_or_cors_error");
    }
    options.signal.addEventListener("abort", () => controller.abort());
  }

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
      const errorObj = new ApiError(
        data?.message ??
          nested?.message ??
          (typeof data?.detail === "string" ? data.detail : null) ??
          "The request could not be completed.",
        response.status,
        data?.code ?? nested?.code,
        data?.details ?? nested?.details,
      );

      // Retry on transient server-side errors (>= 500)
      if (response.status >= 500 && retries > 0 && !options.signal?.aborted) {
        await new Promise((resolve) => setTimeout(resolve, retryDelay));
        return apiRequest<T>(path, {
          ...options,
          retries: retries - 1,
          retryDelay: retryDelay * 2,
        });
      }

      throw errorObj;
    }
    return payload as T;
  } catch (cause) {
    if (cause instanceof ApiError) throw cause;

    let connError: ApiConnectionError;
    if (options.signal?.aborted) {
      connError = new ApiConnectionError("The request was cancelled.", "network_or_cors_error");
    } else if (cause instanceof DOMException && cause.name === "AbortError") {
      connError = new ApiConnectionError("The request timed out.", "request_timeout");
    } else if (cause instanceof ApiConnectionError) {
      connError = cause;
    } else {
      connError = new ApiConnectionError("The API could not be reached.", "network_or_cors_error");
    }

    if (retries > 0 && !options.signal?.aborted) {
      await new Promise((resolve) => setTimeout(resolve, retryDelay));
      return apiRequest<T>(path, { ...options, retries: retries - 1, retryDelay: retryDelay * 2 });
    }

    throw connError;
  } finally {
    window.clearTimeout(timeout);
  }
}
