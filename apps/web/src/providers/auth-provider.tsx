"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import {
  getAccessToken,
  getRefreshToken,
  setTokens,
  clearTokens,
  setStoredUser,
  getStoredUser,
  isTokenExpired,
} from "@/lib/auth";
import type { User } from "@/lib/types";
import type { OtpRequestResponse } from "@/lib/types";

/* ── Context Shape ── */
interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, otp: string) => Promise<void>;
  signup: (email: string, otp: string) => Promise<void>;
  requestOtp: (
    email: string,
    purpose?: "login" | "signup"
  ) => Promise<OtpRequestResponse>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

/* ── Provider ── */
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  /** Bootstrap: check stored token on mount */
  useEffect(() => {
    async function bootstrap() {
      const token = getAccessToken();
      if (!token) {
        // Try loading cached user for offline display
        const cached = getStoredUser<User>();
        if (cached) setUser(cached);
        setIsLoading(false);
        return;
      }

      if (isTokenExpired(token)) {
        // Try refresh
        const refreshToken = getRefreshToken();
        if (refreshToken) {
          try {
            const res = await api.refreshToken(refreshToken);
            setTokens(res.access_token, refreshToken);
          } catch {
            clearTokens();
            setIsLoading(false);
            return;
          }
        } else {
          clearTokens();
          setIsLoading(false);
          return;
        }
      }

      // Fetch current user
      try {
        const me = await api.getMe();
        setUser(me);
        setStoredUser(me as unknown as Record<string, unknown>);
      } catch {
        clearTokens();
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    }

    bootstrap();
  }, []);

  const requestOtp = useCallback(
    async (email: string, purpose: "login" | "signup" = "login") => {
      return api.requestOtp(email, purpose);
    },
    []
  );

  const login = useCallback(
    async (email: string, otp: string) => {
      const res = await api.verifyOtp(email, otp, "login");
      setTokens(res.access_token, res.refresh_token);
      setUser(res.user);
      setStoredUser(res.user as unknown as Record<string, unknown>);
      router.push("/dashboard");
    },
    [router]
  );

  const signup = useCallback(
    async (email: string, otp: string) => {
      const res = await api.verifyOtp(email, otp, "signup");
      setTokens(res.access_token, res.refresh_token);
      setUser(res.user);
      setStoredUser(res.user as unknown as Record<string, unknown>);
      router.push("/dashboard");
    },
    [router]
  );

  const logout = useCallback(async () => {
    try {
      await api.logout();
    } catch {
      // Ignore logout API errors
    } finally {
      clearTokens();
      setUser(null);
      router.push("/");
    }
  }, [router]);

  const refreshUser = useCallback(async () => {
    try {
      const me = await api.getMe();
      setUser(me);
      setStoredUser(me as unknown as Record<string, unknown>);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        clearTokens();
        setUser(null);
      }
    }
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isLoading,
      isAuthenticated: !!user,
      login,
      signup,
      requestOtp,
      logout,
      refreshUser,
    }),
    [user, isLoading, login, signup, requestOtp, logout, refreshUser]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/* ── Hook ── */
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}