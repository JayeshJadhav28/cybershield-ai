"use client";

import { useState, useCallback, useRef } from "react";
import {
  Image as ImageIcon,
  Shield,
  AlertTriangle,
  X,
  Loader2,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  RotateCcw,
  Sparkles,
  Eye,
  Scan,
  Info,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

const ACCEPTED_FORMATS = ["image/png", "image/jpeg", "image/webp", "image/bmp"];
const ACCEPTED_EXT = ".png,.jpg,.jpeg,.webp,.bmp";
const MAX_SIZE_MB = 5;
const FORMAT_BADGES = ["PNG", "JPG", "WebP", "BMP"];

interface ContributingFactor {
  factor: string;
  description?: string;
  raw_score?: number;
  weight?: number;
  contribution?: number;
  flags?: string[];
}

interface ScoringBreakdown {
  ai_weight: number;
  rule_weight: number;
  ai_score: number;
  rule_score: number;
  ai_contribution: number;
  rule_contribution: number;
  adjustment: number;
  formula: string;
}

interface AnalysisResult {
  analysis_id: string;
  risk_score: number;
  risk_label: "safe" | "suspicious" | "dangerous";
  processing_time_ms: number;
  image_metadata: {
    image_width?: number;
    image_height?: number;
    faces_found?: number;
    faces_analyzed?: number;
    method?: string;
    mean_score?: number;
    max_score?: number;
    per_face_scores?: number[];
    face_locations?: Array<{ x: number; y: number; w: number; h: number }>;
    [key: string]: unknown;
  };
  per_face_scores: number[];
  explanation: {
    summary: string;
    contributing_factors: ContributingFactor[];
    scoring_breakdown: ScoringBreakdown;
    highlights?: unknown[];
  };
  tip: string;
}

export function ImageUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showExplanation, setShowExplanation] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = useCallback((selectedFile: File) => {
    setError(null);
    setResult(null);
    if (!ACCEPTED_FORMATS.includes(selectedFile.type)) {
      setError("Unsupported format. Accepted: PNG, JPG, JPEG, WEBP, BMP");
      return;
    }
    const sizeMB = selectedFile.size / (1024 * 1024);
    if (sizeMB > MAX_SIZE_MB) {
      setError(`File too large (${sizeMB.toFixed(1)}MB). Maximum: ${MAX_SIZE_MB}MB`);
      return;
    }
    setFile(selectedFile);
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target?.result as string);
    reader.readAsDataURL(selectedFile);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile) handleFileSelect(droppedFile);
    },
    [handleFileSelect]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) handleFileSelect(selectedFile);
  };

  const resetAll = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
    setShowExplanation(false);
    setIsDragOver(false);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const analyzeImage = async () => {
    if (!file) return;
    setIsAnalyzing(true);
    setError(null);
    setResult(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
      const response = await fetch(`${apiUrl}/analyze/image`, {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: "Analysis failed" }));
        throw new Error(err.detail || err.message || `HTTP ${response.status}`);
      }
      const data: AnalysisResult = await response.json();
      setResult(data);
      setShowExplanation(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const riskConfig = {
    safe: {
      color: "#22c55e",
      bg: "bg-green-500/10",
      border: "border-green-500/30",
      text: "text-green-500",
      icon: "✅",
      label: "Safe",
    },
    suspicious: {
      color: "#f59e0b",
      bg: "bg-amber-500/10",
      border: "border-amber-500/30",
      text: "text-amber-500",
      icon: "⚠️",
      label: "Suspicious",
    },
    dangerous: {
      color: "#ef4444",
      bg: "bg-red-500/10",
      border: "border-red-500/30",
      text: "text-red-500",
      icon: "🚨",
      label: "Dangerous",
    },
  };

  const fileSizeMB = file ? (file.size / (1024 * 1024)).toFixed(1) : "0";

  return (
    <div className="space-y-5">
      {/* ──────────── UPLOAD CARD ──────────── */}
      <Card className="border-zinc-800 bg-zinc-950/50 overflow-hidden">
        <CardContent className="p-5">
          {/* Card header */}
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-zinc-400">
              Upload Image
            </h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={resetAll}
              className="text-zinc-500 hover:text-zinc-300 gap-1.5 h-7 text-xs"
            >
              <RotateCcw className="h-3 w-3" />
              Reset
            </Button>
          </div>

          {/* Hidden input */}
          <input
            ref={fileInputRef}
            type="file"
            accept={ACCEPTED_EXT}
            onChange={handleInputChange}
            className="hidden"
            id="image-upload-input"
          />

          {/* ── Dropzone ── */}
          {!file ? (
            <label
              htmlFor="image-upload-input"
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              className={`
                relative block cursor-pointer rounded-xl border-2 border-dashed
                py-8 px-6 text-center transition-all duration-300 group
                ${
                  isDragOver
                    ? "border-cyan-500/60 bg-cyan-500/5"
                    : "border-zinc-700/80 hover:border-zinc-600"
                }
              `}
            >
              <div
                className={`
                  w-12 h-12 rounded-2xl border flex items-center justify-center
                  mx-auto mb-3 transition-all duration-300
                  ${
                    isDragOver
                      ? "border-cyan-500/40 bg-cyan-500/10"
                      : "border-zinc-700 bg-zinc-800/60 group-hover:border-cyan-500/30 group-hover:bg-cyan-500/5"
                  }
                `}
              >
                <ImageIcon
                  className={`h-5 w-5 transition-colors duration-300 ${
                    isDragOver
                      ? "text-cyan-400"
                      : "text-zinc-500 group-hover:text-cyan-400"
                  }`}
                />
              </div>
              <p className="text-sm font-medium text-zinc-300 mb-0.5">
                Drag &amp; drop a face image
              </p>
              <p className="text-xs text-zinc-500 mb-3">or click to browse</p>
              <div className="flex items-center justify-center gap-1.5 flex-wrap">
                {FORMAT_BADGES.map((fmt) => (
                  <span
                    key={fmt}
                    className="inline-flex items-center rounded-md border border-zinc-700
                               bg-zinc-800/50 px-1.5 py-0.5 text-[10px] font-medium
                               text-zinc-400 tracking-wide"
                  >
                    {fmt}
                  </span>
                ))}
                <span
                  className="inline-flex items-center rounded-md border border-zinc-700
                             bg-zinc-800/50 px-1.5 py-0.5 text-[10px] font-medium
                             text-zinc-400 tracking-wide"
                >
                  ≤ {MAX_SIZE_MB} MB
                </span>
              </div>
            </label>
          ) : (
            <div className="space-y-3">
              <div className="relative bg-zinc-900/50 rounded-xl border border-zinc-800
                              overflow-hidden flex items-center justify-center p-3">
                {preview && (
                  <img
                    src={preview}
                    alt="Preview"
                    className="max-h-56 rounded-lg object-contain"
                  />
                )}
                <button
                  onClick={resetAll}
                  className="absolute top-2 right-2 bg-black/60 hover:bg-black/80
                             rounded-full p-1.5 transition-colors"
                >
                  <X className="h-3.5 w-3.5 text-zinc-300" />
                </button>
              </div>
              <div className="flex items-center justify-between text-sm px-0.5">
                <div className="flex items-center gap-2 text-zinc-400 min-w-0">
                  <ImageIcon className="h-3.5 w-3.5 shrink-0 text-zinc-500" />
                  <span className="truncate text-xs">{file.name}</span>
                </div>
                <span className="text-zinc-500 shrink-0 ml-3 text-xs">
                  {fileSizeMB} MB
                </span>
              </div>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="mt-3 p-2.5 bg-red-500/10 border border-red-500/30 rounded-lg
                            flex items-start gap-2">
              <AlertTriangle className="h-3.5 w-3.5 text-red-400 mt-0.5 shrink-0" />
              <p className="text-xs text-red-400">{error}</p>
            </div>
          )}

          {/* Analyze button */}
          <Button
            onClick={file ? analyzeImage : () => fileInputRef.current?.click()}
            disabled={isAnalyzing}
            className={`
              w-full h-11 mt-4 font-semibold text-sm tracking-wide
              transition-all duration-300
              ${
                file
                  ? "bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white shadow-lg shadow-cyan-500/20"
                  : "bg-cyan-600/80 hover:bg-cyan-600 text-white/80"
              }
            `}
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Analyzing Image…
              </>
            ) : (
              <>
                <Scan className="h-4 w-4 mr-2" />
                Detect Deepfake
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* ──────────── RESULTS ──────────── */}
      {result && (
        <>
          {/* Risk Score */}
          <Card className={`${riskConfig[result.risk_label].border} border bg-zinc-950/50`}>
            <CardContent className="py-5 px-5">
              <div className="flex items-center gap-5">
                <div className="relative shrink-0">
                  <svg width="88" height="88" viewBox="0 0 100 100" className="transform -rotate-90">
                    <circle cx="50" cy="50" r="40" fill="none" stroke="#27272a" strokeWidth="6" />
                    <circle
                      cx="50" cy="50" r="40" fill="none"
                      stroke={riskConfig[result.risk_label].color}
                      strokeWidth="6" strokeLinecap="round"
                      strokeDasharray={`${2 * Math.PI * 40}`}
                      strokeDashoffset={`${2 * Math.PI * 40 * (1 - result.risk_score / 100)}`}
                      style={{ transition: "stroke-dashoffset 1s ease-out" }}
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-xl font-bold font-mono"
                      style={{ color: riskConfig[result.risk_label].color }}>
                      {result.risk_score}
                    </span>
                    <span className="text-[9px] font-semibold uppercase tracking-wider"
                      style={{ color: riskConfig[result.risk_label].color }}>
                      {result.risk_label}
                    </span>
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1.5">
                    <Badge className={`${riskConfig[result.risk_label].bg} ${riskConfig[result.risk_label].text}
                                      border ${riskConfig[result.risk_label].border} text-xs px-2 py-0.5`}>
                      {riskConfig[result.risk_label].icon} {riskConfig[result.risk_label].label}
                    </Badge>
                    <span className="text-xs text-zinc-600">⏱ {result.processing_time_ms}ms</span>
                  </div>
                  <p className="text-sm text-zinc-400 leading-relaxed">{result.explanation.summary}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Image Properties */}
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-2">
              Image Properties
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              <PropertyBox label="Resolution"
                value={result.image_metadata.image_width && result.image_metadata.image_height
                  ? `${result.image_metadata.image_width}×${result.image_metadata.image_height}` : "N/A"}
                icon={<Scan className="h-3 w-3" />} />
              <PropertyBox label="Faces Found"
                value={String(result.image_metadata.faces_found ?? result.image_metadata.faces_analyzed ?? 0)}
                icon={<Eye className="h-3 w-3" />} />
              <PropertyBox label="Detection"
                value={result.image_metadata.method === "face_detection" ? "Face Detected"
                  : result.image_metadata.method === "center_crop_fallback" ? "Center Crop" : "Auto"}
                icon={<ImageIcon className="h-3 w-3" />} />
              <PropertyBox label="Analyzed"
                value={String(result.per_face_scores?.length ?? result.image_metadata.faces_analyzed ?? 0)}
                icon={<Shield className="h-3 w-3" />} />
            </div>
          </div>

          {/* Per-Face Scores */}
          {result.per_face_scores && result.per_face_scores.length > 0 && (
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-2">
                Per-Face Analysis
              </h3>
              <Card className="border-zinc-800 bg-zinc-950/50">
                <CardContent className="py-3 px-4 space-y-2.5">
                  {result.per_face_scores.map((score, i) => {
                    const pct = Math.round(score * 100);
                    const color = pct >= 70 ? "#ef4444" : pct >= 40 ? "#f59e0b" : "#22c55e";
                    return (
                      <div key={i} className="space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-zinc-400 font-medium">Face {i + 1}</span>
                          <span className="text-xs font-mono font-semibold" style={{ color }}>
                            {pct.toFixed(1)}%
                          </span>
                        </div>
                        <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                          <div className="h-full rounded-full transition-all duration-1000 ease-out"
                            style={{ width: `${pct}%`, backgroundColor: color }} />
                        </div>
                      </div>
                    );
                  })}
                </CardContent>
              </Card>
            </div>
          )}

          {/* Detailed Explanation */}
          <div>
            <button onClick={() => setShowExplanation(!showExplanation)}
              className="flex items-center justify-between w-full mb-2">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
                Detailed Explanation
              </h3>
              <div className="flex items-center gap-1 text-xs text-zinc-500">
                {showExplanation ? "Collapse" : "Expand"}
                {showExplanation ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
              </div>
            </button>
            {showExplanation && (
              <Card className="border-zinc-800 bg-zinc-950/50">
                <CardContent className="py-3 px-4 space-y-3">
                  {result.explanation.contributing_factors
                    .filter((f) => f.factor !== "rule_adjustment")
                    .map((factor, i) => {
                      const isAI = factor.factor.includes("ai") || factor.factor.includes("model");
                      const barColor = isAI ? "#06b6d4" : "#f59e0b";
                      const barValue = factor.contribution
                        ? Math.min(100, factor.contribution)
                        : factor.raw_score ? factor.raw_score * 100 : 0;
                      const weight = factor.weight ? Math.round(factor.weight * 100) : 0;
                      return (
                        <div key={i} className="space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-medium text-zinc-300">
                              {factor.factor.replace(/_/g, " ")}
                            </span>
                            <span className="text-[10px] text-zinc-500 font-mono">{weight}%</span>
                          </div>
                          <div className="h-1 bg-zinc-800 rounded-full overflow-hidden">
                            <div className="h-full rounded-full transition-all duration-700"
                              style={{ width: `${barValue}%`, backgroundColor: barColor }} />
                          </div>
                          {factor.description && (
                            <p className="text-[10px] text-zinc-600">{factor.description}</p>
                          )}
                        </div>
                      );
                    })}
                  {result.explanation.contributing_factors
                    .filter((f) => f.factor === "rule_adjustment")
                    .map((factor, i) => (
                      <div key={`adj-${i}`} className="flex items-start gap-2 text-[10px]">
                        <Info className="h-3 w-3 text-amber-500 mt-0.5 shrink-0" />
                        <span className="text-zinc-500">{factor.description}</span>
                      </div>
                    ))}
                  <Separator className="bg-zinc-800" />
                  <div className="space-y-1.5">
                    <div className="flex justify-between text-[10px]">
                      <span className="text-zinc-500">AI Model Contribution</span>
                      <span className="font-mono text-cyan-400">
                        {result.explanation.scoring_breakdown.ai_contribution.toFixed(1)} / 75
                      </span>
                    </div>
                    <div className="flex justify-between text-[10px]">
                      <span className="text-zinc-500">Heuristic Rules</span>
                      <span className="font-mono text-amber-400">
                        {result.explanation.scoring_breakdown.rule_contribution.toFixed(1)} / 25
                      </span>
                    </div>
                    <p className="text-[9px] text-zinc-700 font-mono pt-0.5">
                      {result.explanation.scoring_breakdown.formula}
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Safety Tip */}
          <Card className="border-cyan-500/20 bg-cyan-500/5">
            <CardContent className="py-4 px-5">
              <div className="flex items-start gap-3 mb-3">
                <div className="w-7 h-7 rounded-lg bg-cyan-500/10 border border-cyan-500/20
                                flex items-center justify-center shrink-0">
                  <span className="text-sm">💡</span>
                </div>
                <div>
                  <h4 className="text-xs font-semibold text-zinc-300 mb-0.5">Safety Tip</h4>
                  <p className="text-xs text-zinc-400 leading-relaxed">{result.tip}</p>
                </div>
              </div>
              <div className="flex items-center gap-2 pl-10">
                <Button variant="outline" size="sm"
                  className="h-7 text-[10px] border-zinc-700 text-zinc-400 hover:text-zinc-200 hover:border-zinc-600"
                  asChild>
                  <a href="/awareness/resources">
                    Learn More <ExternalLink className="h-2.5 w-2.5 ml-1" />
                  </a>
                </Button>
                <Button variant="outline" size="sm"
                  className="h-7 text-[10px] border-zinc-700 text-zinc-400 hover:text-zinc-200 hover:border-zinc-600"
                  asChild>
                  <a href="https://cybercrime.gov.in" target="_blank" rel="noopener noreferrer">
                    Report to Cyber Crime Portal <ExternalLink className="h-2.5 w-2.5 ml-1" />
                  </a>
                </Button>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}

/* ── Helper ─────────────────────────────────────────── */

function PropertyBox({ label, value, icon }: { label: string; value: string; icon: React.ReactNode }) {
  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-2.5 text-center space-y-0.5">
      <div className="flex items-center justify-center gap-1 text-zinc-500">
        {icon}
        <span className="text-[9px] uppercase tracking-wider font-medium">{label}</span>
      </div>
      <p className="text-xs font-semibold text-cyan-400 font-mono">{value}</p>
    </div>
  );
}