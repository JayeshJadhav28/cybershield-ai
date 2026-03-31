/**
 * @file api.ts — CyberShield AI Frontend API Client
 */

import { API_BASE_URL } from "./constants";
import type {
  AuthResponse,
  OtpRequestResponse,
  RefreshResponse,
  AnalysisResponse,
  QrAnalysisResponse,
  QuizResponse,
  QuizSessionResponse,
  QuizResultResponse,
  QuizAnswer,
  DemoSamplesResponse,
  AnalysisSummary,
  AnalysisListResponse,
  PaginatedResponse,
  OrgMetrics,
  User,
} from "./types";

export interface EmailAnalysisRequest {
  subject: string;
  body: string;
  sender?: string;
  urls?: string[];
}

/* ── Local Storage Cache for guest users ── */
const LOCAL_ANALYSES_KEY = "cs-recent-analyses";
const MAX_LOCAL_ANALYSES = 20;

function getLocalAnalyses(): AnalysisSummary[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(LOCAL_ANALYSES_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveLocalAnalysis(analysis: AnalysisSummary) {
  if (typeof window === "undefined") return;
  try {
    const existing = getLocalAnalyses();
    // Prepend new, deduplicate, limit
    const updated = [
      analysis,
      ...existing.filter((a) => a.id !== analysis.id),
    ].slice(0, MAX_LOCAL_ANALYSES);
    localStorage.setItem(LOCAL_ANALYSES_KEY, JSON.stringify(updated));
  } catch {
    // Quota exceeded — silently ignore
  }
}

/** Convert an AnalysisResponse to a storable AnalysisSummary */
function responseToSummary(
  res: AnalysisResponse,
  type: AnalysisSummary["type"]
): AnalysisSummary {
  return {
    id: res.analysis_id,
    type,
    risk_score: res.risk_score,
    risk_label: res.risk_label,
    explanation_summary:
      res.explanation?.summary || `${type} analysis completed`,
    processing_time_ms: res.processing_time_ms,
    created_at: new Date().toISOString(),
  };
}

/* ── API Error Class ── */
export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public details?: Record<string, unknown>
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/* ── API Client ── */
class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private getToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("access_token");
  }

  private isAuthenticated(): boolean {
    return !!this.getToken();
  }

  async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = this.getToken();

    const headers: Record<string, string> = {};

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    // Don't set Content-Type for FormData
    if (!(options.body instanceof FormData)) {
      headers["Content-Type"] = "application/json";
    }

    let response: Response;
    try {
      response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        headers: {
          ...headers,
          ...(options.headers as Record<string, string>),
        },
      });
    } catch {
      throw new ApiError(
        0,
        "network_error",
        `Cannot reach API at ${this.baseUrl}. Start backend and verify NEXT_PUBLIC_API_URL.`
      );
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        error: "unknown_error",
        message: `Request failed with status ${response.status}`,
      }));

      const detailMessage =
        typeof errorData?.detail === "string"
          ? errorData.detail
          : Array.isArray(errorData?.detail)
            ? errorData.detail
                .map((d: any) => d?.msg || JSON.stringify(d))
                .join(", ")
            : undefined;

      throw new ApiError(
        response.status,
        errorData.error || "unknown_error",
        errorData.message ||
          detailMessage ||
          "An unexpected error occurred",
        errorData.details || errorData.detail
      );
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  /* ── Auth ── */
  requestOtp(email: string, purpose: "login" | "signup" = "login") {
    return this.request<OtpRequestResponse>("/auth/request-otp", {
      method: "POST",
      body: JSON.stringify({ email, purpose }),
    });
  }

  verifyOtp(
    email: string,
    otp: string,
    purpose: "login" | "signup" = "login"
  ) {
    return this.request<AuthResponse>("/auth/verify-otp", {
      method: "POST",
      body: JSON.stringify({ email, otp, purpose }),
    });
  }

  refreshToken(refreshToken: string) {
    return this.request<RefreshResponse>("/auth/refresh", {
      method: "POST",
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  }

  logout() {
    return this.request<{ status: string }>("/auth/logout", {
      method: "POST",
    });
  }

  getMe() {
    return this.request<User>("/auth/me");
  }

  /* ── Analysis (with local caching) ── */
  async analyzeEmail(data: EmailAnalysisRequest) {
    const result = await this.request<AnalysisResponse>("/analyze/email", {
      method: "POST",
      body: JSON.stringify(data),
    });
    saveLocalAnalysis(responseToSummary(result, "email"));
    return result;
  }

  async analyzeUrl(url: string) {
    const result = await this.request<AnalysisResponse>("/analyze/url", {
      method: "POST",
      body: JSON.stringify({ url }),
    });
    saveLocalAnalysis(responseToSummary(result, "url"));
    return result;
  }

  async analyzeQr(file: File) {
    const form = new FormData();
    form.append("file", file);
    const result = await this.request<QrAnalysisResponse>("/analyze/qr", {
      method: "POST",
      body: form,
    });
    saveLocalAnalysis(responseToSummary(result, "qr"));
    return result;
  }

  async analyzeAudio(file: File) {
    const form = new FormData();
    form.append("file", file);
    const result = await this.request<AnalysisResponse>("/analyze/audio", {
      method: "POST",
      body: form,
    });
    saveLocalAnalysis(responseToSummary(result, "audio"));
    return result;
  }

  async analyzeVideo(file: File) {
    const form = new FormData();
    form.append("file", file);
    const result = await this.request<AnalysisResponse>("/analyze/video", {
      method: "POST",
      body: form,
    });
    saveLocalAnalysis(responseToSummary(result, "video"));
    return result;
  }

  async analyzeImage(file: File) {
    const form = new FormData();
    form.append("file", file);
    const result = await this.request<AnalysisResponse>("/analyze/image", {
      method: "POST",
      body: form,
    });
    saveLocalAnalysis(responseToSummary(result, "image"));
    return result;
  }

  /* ── Reports ── */

  /**
   * Get analysis history.
   * - Authenticated users → fetches from backend API
   * - Guest users → returns from localStorage cache
   *
   * Backend returns { analyses: [...] } so we map to { items: [...] }
   */
  async getAnalysisHistory(
    page = 1,
    limit = 20
  ): Promise<PaginatedResponse<AnalysisSummary>> {
    if (!this.isAuthenticated()) {
      // Guest mode: return cached local analyses
      const local = getLocalAnalyses();
      const start = (page - 1) * limit;
      const slice = local.slice(start, start + limit);
      return {
        total: local.length,
        page,
        limit,
        items: slice,
      };
    }

    try {
      // Backend returns { total, page, limit, analyses: [...] }
      const raw = await this.request<AnalysisListResponse>(
        `/reports/analyses?page=${page}&limit=${limit}`
      );
      return {
        total: raw.total,
        page: raw.page,
        limit: raw.limit,
        items: raw.analyses ?? [],
      };
    } catch (err) {
      // If 401 (token expired), fall back to local cache
      if (err instanceof ApiError && err.status === 401) {
        const local = getLocalAnalyses();
        const start = (page - 1) * limit;
        return {
          total: local.length,
          page,
          limit,
          items: local.slice(start, start + limit),
        };
      }
      throw err;
    }
  }

  getAnalysisDetail(id: string) {
    return this.request<AnalysisResponse>(`/reports/analyses/${id}`);
  }

  /** Get local (client-side cached) analyses for immediate display */
  getLocalAnalyses(): AnalysisSummary[] {
    return getLocalAnalyses();
  }

  /* ── Awareness ── */
  getQuizzes(category: string, language = "en") {
    return this.request<QuizResponse>(
      `/awareness/quizzes?category=${category}&language=${language}`
    );
  }

  startQuizSession(category: string, language = "en") {
    return this.request<QuizSessionResponse>("/awareness/quiz-sessions", {
      method: "POST",
      body: JSON.stringify({ category, language }),
    });
  }

  submitQuizAnswers(sessionId: string, answers: QuizAnswer[]) {
    return this.request<QuizResultResponse>(
      `/awareness/quiz-sessions/${sessionId}/answers`,
      {
        method: "POST",
        body: JSON.stringify({ answers }),
      }
    );
  }

  getScenarios() {
    return this.request<{ scenarios: any[] }>("/awareness/scenarios");
  }

  getScenario(id: string) {
    return this.request<any>(`/awareness/scenarios/${id}`);
  }

  getAwarenessSummary() {
    return this.request<any>("/awareness/summary");
  }

  /* ── Demo ── */
  getDemoSamples() {
    return this.request<DemoSamplesResponse>("/demo/samples");
  }

  /* ── Admin ── */
  getOrgMetrics(period = "last_30_days") {
    return this.request<OrgMetrics>(`/admin/metrics?period=${period}`);
  }
}

/** Singleton API client instance */
export const api = new ApiClient();