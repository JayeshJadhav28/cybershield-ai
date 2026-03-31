import { z } from "zod";

/* ── Auth Schemas ── */
export const emailSchema = z
  .string()
  .email("Please enter a valid email address")
  .min(1, "Email is required");

export const otpSchema = z
  .string()
  .length(6, "OTP must be 6 digits")
  .regex(/^\d{6}$/, "OTP must contain only digits");

export const requestOtpSchema = z.object({
  email: emailSchema,
  purpose: z.enum(["login", "signup"]).default("login"),
});

export const verifyOtpSchema = z.object({
  email: emailSchema,
  otp: otpSchema,
  purpose: z.enum(["login", "signup"]).default("login"),
});

/* ── Analysis Schemas ── */
export const emailAnalysisSchema = z.object({
  subject: z
    .string()
    .min(1, "Subject is required")
    .max(500, "Subject must be 500 characters or less"),
  body: z
    .string()
    .min(1, "Email body is required")
    .max(50000, "Body must be 50,000 characters or less"),
  sender: z
    .string()
    .min(1, "Sender email is required")
    .email("Please enter a valid sender email"),
  urls: z
    .string()
    .optional()
    .transform((val) => {
      if (!val || val.trim() === "") return [];
      return val
        .split(/[\n,]+/)
        .map((u) => u.trim())
        .filter(Boolean);
    }),
});

export type EmailAnalysisFormData = z.infer<typeof emailAnalysisSchema>;

export const urlAnalysisSchema = z.object({
  url: z
    .string()
    .min(1, "URL is required")
    .max(2048, "URL must be 2048 characters or less")
    .refine(
      (val) => {
        try {
          new URL(val.startsWith("http") ? val : `https://${val}`);
          return true;
        } catch {
          return false;
        }
      },
      { message: "Please enter a valid URL" }
    ),
});

export type UrlAnalysisFormData = z.infer<typeof urlAnalysisSchema>;

/* ── File Validation Helpers ── */
export function validateAudioFile(file: File): string | null {
  const maxSize = 10 * 1024 * 1024; // 10MB
  const validTypes = [
    "audio/wav",
    "audio/mpeg",
    "audio/ogg",
    "audio/mp4",
    "audio/flac",
    "audio/x-wav",
    "audio/wave",
  ];

  if (!validTypes.includes(file.type) && !file.name.match(/\.(wav|mp3|ogg|m4a|flac)$/i)) {
    return "Unsupported format. Accepted: WAV, MP3, OGG, M4A, FLAC";
  }
  if (file.size > maxSize) {
    return `File too large. Maximum size is 10MB (yours: ${(file.size / 1024 / 1024).toFixed(1)}MB)`;
  }
  return null;
}

export function validateVideoFile(file: File): string | null {
  const maxSize = 50 * 1024 * 1024; // 50MB
  const validTypes = [
    "video/mp4",
    "video/x-msvideo",
    "video/quicktime",
    "video/webm",
  ];

  if (!validTypes.includes(file.type) && !file.name.match(/\.(mp4|avi|mov|webm)$/i)) {
    return "Unsupported format. Accepted: MP4, AVI, MOV, WEBM";
  }
  if (file.size > maxSize) {
    return `File too large. Maximum size is 50MB (yours: ${(file.size / 1024 / 1024).toFixed(1)}MB)`;
  }
  return null;
}

export function validateImageFile(file: File): string | null {
  const maxSize = 5 * 1024 * 1024; // 5MB
  const validTypes = ["image/png", "image/jpeg", "image/webp"];

  if (!validTypes.includes(file.type) && !file.name.match(/\.(png|jpg|jpeg|webp)$/i)) {
    return "Unsupported format. Accepted: PNG, JPG, JPEG, WEBP";
  }
  if (file.size > maxSize) {
    return `File too large. Maximum size is 5MB (yours: ${(file.size / 1024 / 1024).toFixed(1)}MB)`;
  }
  return null;
}

/* ── Quiz Schema ── */
export const quizAnswerSchema = z.object({
  question_id: z.string().uuid(),
  selected_option_index: z.number().min(0).max(3),
});

export const quizSubmitSchema = z.object({
  answers: z.array(quizAnswerSchema).min(1),
});

/* ── Profile Schema ── */
export const profileSchema = z.object({
  display_name: z
    .string()
    .min(2, "Name must be at least 2 characters")
    .max(100, "Name must be 100 characters or less"),
});