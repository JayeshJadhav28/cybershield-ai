/* ================================================================
   CyberShield AI — TypeScript Type Definitions
   Mirrors API contracts from TDD §11
   ================================================================ */

/* ── Common ── */
export interface ApiError {
  error: string;
  message: string;
  details?: Record<string, unknown>;
  timestamp?: string;
  request_id?: string;
}

export interface PaginatedResponse<T> {
  total: number;
  page: number;
  limit: number;
  items: T[];
}

/* ── Auth ── */
export interface User {
  id: string;
  email: string;
  display_name: string | null;
  role: "user" | "admin" | "org_admin";
  organizations?: OrgMembership[];
  stats?: UserStats;
}

export interface OrgMembership {
  id: string;
  name: string;
  role: "member" | "coordinator" | "admin";
}

export interface UserStats {
  total_analyses: number;
  quizzes_completed: number;
  badges_earned: string[];
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
  expires_in: number;
  user: User;
}

export interface OtpRequestResponse {
  status: string;
  message: string;
  expires_in_seconds: number;
  dev_otp?: string;
}

export interface RefreshResponse {
  access_token: string;
  expires_in: number;
}

/* ── Analysis — Requests ── */
export interface EmailAnalysisRequest {
  subject: string;
  body: string;
  sender: string;
  urls?: string[];
}

export interface UrlAnalysisRequest {
  url: string;
}

/* ── Analysis — Responses ── */
export interface ContributingFactor {
  factor: string;
  weight?: number;
  raw_score?: number;
  contribution?: number;
  description?: string;
}

export interface HighlightPhrase {
  text: string;
  reason: string;
}

export interface HighlightUrl {
  url: string;
  flags: string[];
}

export interface HighlightSender {
  email: string;
  flags: string[];
}

export interface DomainAnalysis {
  domain: string;
  flags: string[];
}

export interface ExplanationHighlights {
  phrases?: HighlightPhrase[];
  urls?: HighlightUrl[];
  sender?: HighlightSender;
  domain_analysis?: DomainAnalysis;
}

export interface Explanation {
  summary: string;
  highlights?: ExplanationHighlights;
  contributing_factors: ContributingFactor[];
  frame_analysis?: {
    total_frames: number;
    suspicious_frames: number;
    anomaly_distribution: string;
  };
}

export interface AnalysisResponse {
  analysis_id: string;
  risk_score: number;
  risk_label: "safe" | "suspicious" | "dangerous";
  processing_time_ms: number;
  explanation: Explanation;
  tip: string;
  audio_metadata?: AudioMetadata;
  video_metadata?: VideoMetadata;
}

export interface QrDecodedContent {
  raw: string;
  type: "upi" | "url" | "text" | "unknown";
  parsed?: {
    upi_id?: string;
    payee_name?: string;
    amount?: string;
    currency?: string;
    note?: string;
  };
}

export interface QrAnalysisResponse extends AnalysisResponse {
  decoded: QrDecodedContent;
}

export interface AudioMetadata {
  duration_seconds: number;
  sample_rate: number;
  format: string;
}

export interface VideoMetadata {
  duration_seconds: number;
  resolution: string;
  fps: number;
  frames_analyzed: number;
}

/* ── Analysis History ── */
export interface AnalysisSummary {
  id: string;
  type: "email" | "url" | "qr" | "audio" | "video" | "image";
  risk_score: number;
  risk_label: "safe" | "suspicious" | "dangerous";
  explanation_summary: string;
  processing_time_ms?: number;
  is_demo?: boolean;
  created_at: string;
}

/** Backend returns { analyses: [...] } not { items: [...] } */
export interface AnalysisListResponse {
  total: number;
  page: number;
  limit: number;
  analyses: AnalysisSummary[];
}

/* ── Quiz / Awareness ── */
export interface QuizQuestion {
  id: string;
  question_text: string;
  options: string[];
  difficulty: number;
}

export interface QuizQuestionWithAnswer extends QuizQuestion {
  correct_option_index: number;
  explanation: string;
}

export interface QuizResponse {
  category: string;
  language: string;
  total_questions: number;
  questions: QuizQuestion[];
}

export interface QuizSessionResponse {
  session_id: string;
  category: string;
  total_questions: number;
  questions: QuizQuestion[];
}

export interface QuizAnswer {
  question_id: string;
  selected_option_index: number;
}

export interface QuizAnswerResult {
  question_id: string;
  selected_option_index: number;
  correct_option_index: number;
  is_correct: boolean;
  explanation: string;
}

export interface QuizResultResponse {
  session_id: string;
  category: string;
  total_questions: number;
  correct_count: number;
  score_pct: number;
  badge_earned: string | null;
  results: QuizAnswerResult[];
}

export interface AwarenessSummary {
  user_id: string;
  total_quizzes_completed: number;
  average_score_pct: number;
  badges: Array<{
    category: string;
    badge: string;
    earned_at: string;
  }>;
  category_scores: Record<
    string,
    { attempts: number; best_score: number; average_score: number }
  >;
  weakest_category: string;
  scenarios_completed: number;
}

/* ── Scenarios ── */
export interface ScenarioSummary {
  id: string;
  title: string;
  description: string;
  category: string;
  scenario_type: "chat" | "email" | "call";
  estimated_time_minutes: number;
}

export interface ScenarioStep {
  step: number;
  type: "message" | "choice";
  role?: string;
  message?: string;
  prompt?: string;
  options?: string[];
  correct_index?: number;
  feedback?: Record<string, string>;
}

export interface ScenarioDetail {
  id: string;
  title: string;
  steps: ScenarioStep[];
}

/* ── Demo ── */
export interface DemoSample {
  id: string;
  type: "email" | "url" | "qr" | "audio" | "video";
  title: string;
  expected_label: "safe" | "suspicious" | "dangerous";
  data?: Record<string, unknown>;
  file_url?: string;
}

export interface DemoSamplesResponse {
  samples: DemoSample[];
}

/* ── Admin ── */
export interface OrgMetrics {
  org_id: string;
  period: string;
  total_users: number;
  total_analyses: number;
  analyses_by_type: Record<string, number>;
  risk_distribution: Record<string, number>;
  quiz_metrics: {
    total_sessions: number;
    average_score: number;
    weakest_category: string;
    completion_rate: number;
  };
}