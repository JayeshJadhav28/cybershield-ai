'use client';

import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import {
  ShieldCheck,
  AlertTriangle,
  ShieldAlert,
  Clock,
  Info,
  OctagonAlert,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */
export interface AnalysisResult {
  analysis_id: string;
  risk_score: number;
  risk_label: 'safe' | 'suspicious' | 'dangerous';
  processing_time_ms: number;
  confidence_level?: 'high' | 'medium' | 'low';
  calibration_note?: string;
  explanation: {
    summary: string;
    highlights?: {
      phrases?: { text: string; reason: string }[];
      urls?: { url: string; flags: string[] }[];
      sender?: { email: string; flags: string[] };
      domain_analysis?: { domain: string; flags: string[] };
    };
    contributing_factors?: {
      factor: string;
      weight: number;
      raw_score?: number;
      contribution?: number;
      description: string;
    }[];
    scoring_breakdown?: {
      ai_weight: number;
      rule_weight: number;
      ai_score: number;
      rule_score: number;
      ai_contribution: number;
      rule_contribution: number;
      adjustment: number;
      formula: string;
    };
  };
  tip: string;
  decoded?: {
    raw: string;
    type: string;
    parsed?: Record<string, string>;
  };
  audio_metadata?: {
    duration_seconds: number;
    sample_rate: number;
    format: string;
  };
  video_metadata?: {
    duration_seconds: number;
    resolution: string;
    fps: number;
    frames_analyzed: number;
  };
  image_metadata?: Record<string, unknown>;
  per_face_scores?: number[];
}

/* ------------------------------------------------------------------ */
/*  Risk config                                                        */
/* ------------------------------------------------------------------ */
const riskConfig = {
  safe: {
    Icon: ShieldCheck,
    color: '#22c55e',
    label: 'Safe',
    badgeClass: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400',
    borderClass: 'border-emerald-500/20',
    bgClass: 'bg-emerald-500/5',
  },
  suspicious: {
    Icon: AlertTriangle,
    color: '#f59e0b',
    label: 'Suspicious',
    badgeClass: 'border-amber-500/30 bg-amber-500/10 text-amber-400',
    borderClass: 'border-amber-500/20',
    bgClass: 'bg-amber-500/5',
  },
  dangerous: {
    Icon: ShieldAlert,
    color: '#ef4444',
    label: 'Dangerous',
    badgeClass: 'border-red-500/30 bg-red-500/10 text-red-400',
    borderClass: 'border-red-500/20',
    bgClass: 'bg-red-500/5',
  },
};

const confidenceConfig = {
  high: { label: 'High confidence', dotClass: 'bg-emerald-400', textClass: 'text-emerald-400' },
  medium: { label: 'Moderate confidence', dotClass: 'bg-amber-400', textClass: 'text-amber-400' },
  low: { label: 'Low confidence — verify independently', dotClass: 'bg-red-400', textClass: 'text-red-400' },
};

/* ------------------------------------------------------------------ */
/*  Circular Gauge                                                     */
/* ------------------------------------------------------------------ */
function RiskGauge({
  score,
  label,
  color,
  size = 110,
}: {
  score: number;
  label: string;
  color: string;
  size?: number;
}) {
  const r = 38;
  const circumference = 2 * Math.PI * r;
  const offset = circumference * (1 - score / 100);

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg
        width={size}
        height={size}
        viewBox="0 0 100 100"
        className="transform -rotate-90"
      >
        {/* Track */}
        <circle
          cx="50" cy="50" r={r}
          fill="none"
          stroke="#27272a"
          strokeWidth="5"
        />
        {/* Progress */}
        <circle
          cx="50" cy="50" r={r}
          fill="none"
          stroke={color}
          strokeWidth="5"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-all duration-1000 ease-out"
        />
        {/* Outer glow */}
        <circle
          cx="50" cy="50" r={r}
          fill="none"
          stroke={color}
          strokeWidth="5"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          opacity={0.15}
          filter="blur(4px)"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span
          className="text-2xl font-bold font-mono leading-none"
          style={{ color }}
        >
          {score}
        </span>
        <span
          className="text-[9px] font-bold uppercase tracking-widest mt-0.5"
          style={{ color }}
        >
          {label}
        </span>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Result Card                                                        */
/* ------------------------------------------------------------------ */
interface ResultCardProps {
  result: AnalysisResult;
}

export function ResultCard({ result }: ResultCardProps) {
  const cfg = riskConfig[result.risk_label];
  const { Icon } = cfg;
  const confCfg = result.confidence_level
    ? confidenceConfig[result.confidence_level]
    : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      data-testid="result-card"
    >
      <Card
        className={cn(
          'border bg-zinc-950/60 backdrop-blur-sm overflow-hidden',
          cfg.borderClass,
        )}
      >
        {/* Top accent line */}
        <div
          className="h-[2px] w-full"
          style={{
            background: `linear-gradient(90deg, transparent, ${cfg.color}40, ${cfg.color}, ${cfg.color}40, transparent)`,
          }}
        />

        <CardContent className="p-5">
          <div className="flex items-start gap-5">
            {/* Gauge */}
            <div className="shrink-0">
              <RiskGauge
                score={result.risk_score}
                label={result.risk_label}
                color={cfg.color}
              />
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0 space-y-2.5">
              {/* Badge row */}
              <div className="flex flex-wrap items-center gap-2">
                <Badge
                  variant="outline"
                  className={cn('gap-1.5 text-xs font-semibold px-2.5 py-0.5', cfg.badgeClass)}
                  data-testid="risk-label"
                >
                  <Icon className="h-3.5 w-3.5" />
                  {cfg.label}
                </Badge>

                <span className="text-[11px] text-zinc-500 flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {result.processing_time_ms}ms
                </span>

                {confCfg && (
                  <span className={cn('text-[11px] flex items-center gap-1', confCfg.textClass)}>
                    <span className={cn('h-1.5 w-1.5 rounded-full', confCfg.dotClass)} />
                    {confCfg.label}
                  </span>
                )}
              </div>

              {/* Summary */}
              <p
                className="text-sm leading-relaxed text-zinc-300"
                data-testid="explanation-summary"
              >
                {result.explanation.summary}
              </p>

              {/* Calibration note */}
              {result.calibration_note &&
                !result.calibration_note.includes('AI model') && (
                  <div className="flex items-start gap-2 rounded-lg border border-zinc-700/40 bg-zinc-800/30 px-3 py-2">
                    <Info className="h-3.5 w-3.5 text-zinc-500 flex-none mt-0.5" />
                    <p className="text-[11px] text-zinc-500 leading-relaxed">
                      {result.calibration_note}
                    </p>
                  </div>
                )}

              {/* Danger banner */}
              {result.risk_label === 'dangerous' && (
                <div className="flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/8 px-3 py-2">
                  <OctagonAlert className="h-4 w-4 text-red-400 shrink-0" />
                  <p className="text-xs font-semibold text-red-400">
                    DO NOT PROCEED — This content shows strong threat indicators.
                  </p>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}