export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  accessTokenExpiresIn: number;
}
export interface AuthUser {
  id: string;
  email: string;
  is_active: boolean;
  created_at: string;
}
export interface AuthCredentials {
  email: string;
  password: string;
}
export interface AuthContextValue {
  user: AuthUser | null;
  isLoading: boolean;
  error: string | null;
  login: (credentials: AuthCredentials) => Promise<void>;
  register: (credentials: AuthCredentials) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
}
