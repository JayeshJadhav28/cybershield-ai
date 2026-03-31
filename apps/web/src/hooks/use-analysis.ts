"use client";

import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type {
  AnalysisResponse,
  EmailAnalysisRequest,
  QrAnalysisResponse,
} from "@/lib/types";

/** Hook for email analysis */
export function useEmailAnalysis() {
  return useMutation<AnalysisResponse, Error, EmailAnalysisRequest>({
    mutationFn: (data) => api.analyzeEmail(data),
  });
}

/** Hook for URL analysis */
export function useUrlAnalysis() {
  return useMutation<AnalysisResponse, Error, string>({
    mutationFn: (url) => api.analyzeUrl(url),
  });
}

/** Hook for QR analysis */
export function useQrAnalysis() {
  return useMutation<QrAnalysisResponse, Error, File>({
    mutationFn: (file) => api.analyzeQr(file),
  });
}

/** Hook for audio analysis */
export function useAudioAnalysis() {
  return useMutation<AnalysisResponse, Error, File>({
    mutationFn: (file) => api.analyzeAudio(file),
  });
}

/** Hook for video analysis */
export function useVideoAnalysis() {
  return useMutation<AnalysisResponse, Error, File>({
    mutationFn: (file) => api.analyzeVideo(file),
  });
}