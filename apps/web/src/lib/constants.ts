/* ================================================================
   CyberShield AI — Application Constants
   ================================================================ */

/** API base URL */
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

/** Application name */
export const APP_NAME = "CyberShield AI";
export const APP_VERSION = "1.0.0";

/* ── Risk Thresholds ── */
export const RISK_THRESHOLDS = {
  SAFE_MAX: 30,
  DANGEROUS_MIN: 70,
} as const;

/* ── Risk Label Configuration ── */
export const RISK_CONFIG = {
  safe: {
    label: "Safe",
    text: "text-cs-safe",
    bg: "bg-cs-safe/10",
    border: "border-cs-safe/30",
    hex: "#22c55e",
    icon: "ShieldCheck" as const,
    message: "No significant threats detected.",
    glowClass: "border-glow-safe",
  },
  suspicious: {
    label: "Suspicious",
    text: "text-cs-suspicious",
    bg: "bg-cs-suspicious/10",
    border: "border-cs-suspicious/30",
    hex: "#f59e0b",
    icon: "AlertTriangle" as const,
    message: "Some concerning indicators found. Exercise caution.",
    glowClass: "border-glow-suspicious",
  },
  dangerous: {
    label: "Dangerous",
    text: "text-cs-dangerous",
    bg: "bg-cs-dangerous/10",
    border: "border-cs-dangerous/30",
    hex: "#ef4444",
    icon: "ShieldAlert" as const,
    message: "Strong threat indicators detected. Do not proceed.",
    glowClass: "border-glow-dangerous",
  },
} as const;

export type RiskLabel = keyof typeof RISK_CONFIG;

/* ── Analysis Types ── */
export const ANALYSIS_TYPES = {
  email: { label: "Email", icon: "Mail", path: "/analyze/email" },
  url: { label: "URL / QR", icon: "Link", path: "/analyze/url" },
  audio: { label: "Audio", icon: "Mic", path: "/analyze/audio" },
  video: { label: "Video", icon: "Video", path: "/analyze/video" },
} as const;

export type AnalysisType = keyof typeof ANALYSIS_TYPES;

/* ── Quiz Categories ── */
export const QUIZ_CATEGORIES = {
  deepfake: { label: "Deepfakes", icon: "Eye", color: "text-cs-purple" },
  phishing: { label: "Phishing", icon: "Mail", color: "text-cs-cyan" },
  upi_qr: { label: "UPI / QR Scams", icon: "QrCode", color: "text-cs-blue" },
  kyc_otp: { label: "KYC / OTP Fraud", icon: "ShieldAlert", color: "text-cs-dangerous" },
  general: { label: "General", icon: "BookOpen", color: "text-cs-suspicious" },
} as const;

export type QuizCategory = keyof typeof QUIZ_CATEGORIES;

/* ── Badge Thresholds ── */
export const BADGE_THRESHOLDS = {
  gold: { min: 90, label: "Gold", emoji: "🥇" },
  silver: { min: 70, label: "Silver", emoji: "🥈" },
  bronze: { min: 50, label: "Bronze", emoji: "🥉" },
} as const;

/* ── File Upload Constraints ── */
export const FILE_CONSTRAINTS = {
  audio: {
    maxSizeMB: 10,
    maxDurationS: 30,
    acceptedTypes: {
      "audio/wav": [".wav"],
      "audio/mpeg": [".mp3"],
      "audio/ogg": [".ogg"],
      "audio/mp4": [".m4a"],
      "audio/flac": [".flac"],
    },
    acceptString: ".wav,.mp3,.ogg,.m4a,.flac",
  },
  video: {
    maxSizeMB: 50,
    maxDurationS: 60,
    acceptedTypes: {
      "video/mp4": [".mp4"],
      "video/x-msvideo": [".avi"],
      "video/quicktime": [".mov"],
      "video/webm": [".webm"],
    },
    acceptString: ".mp4,.avi,.mov,.webm",
  },
  image: {
    maxSizeMB: 5,
    acceptedTypes: {
      "image/png": [".png"],
      "image/jpeg": [".jpg", ".jpeg"],
      "image/webp": [".webp"],
    },
    acceptString: ".png,.jpg,.jpeg,.webp",
  },
} as const;

/* ── External Resource Links ── */
export const EXTERNAL_LINKS = {
  cyberCrimePortal: "https://cybercrime.gov.in",
  cyberCrimeHelpline: "1930",
  certIn: "https://www.cert-in.org.in",
} as const;

/* ── Navigation Items ── */
export const NAV_ITEMS = {
  main: [
    { label: "Dashboard", href: "/dashboard", icon: "LayoutDashboard" },
  ],
  analyze: [
    { label: "Email", href: "/analyze/email", icon: "Mail" },
    { label: "URL / QR", href: "/analyze/url", icon: "Link" },
    { label: "Audio", href: "/analyze/audio", icon: "Mic" },
    { label: "Video", href: "/analyze/video", icon: "Video" },
  ],
  awareness: [
    { label: "Quizzes", href: "/awareness/quizzes", icon: "HelpCircle" },
    { label: "Scenarios", href: "/awareness/scenarios", icon: "MessageSquare" },
    { label: "Resources", href: "/awareness/resources", icon: "BookOpen" },
  ],
  reports: [
    { label: "Analyses", href: "/reports/analyses", icon: "FileText" },
    { label: "Quiz History", href: "/reports/quizzes", icon: "Trophy" },
  ],
  admin: [
    { label: "Metrics", href: "/admin/metrics", icon: "BarChart3" },
    { label: "Content", href: "/admin/content", icon: "Settings" },
  ],
} as const;