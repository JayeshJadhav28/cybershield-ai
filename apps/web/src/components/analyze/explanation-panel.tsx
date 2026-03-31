'use client';

import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  ChevronDown,
  ChevronUp,
  AlertCircle,
  Link2,
  User,
  BarChart2,
  Globe,
  Info,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Separator } from '@/components/ui/separator';
import { motion, AnimatePresence } from 'framer-motion';
import type { AnalysisResult } from './result-card';

/* ------------------------------------------------------------------ */
/*  Section wrapper                                                    */
/* ------------------------------------------------------------------ */
function Section({
  icon: Icon,
  title,
  children,
}: {
  icon: React.ElementType;
  title: string;
  children?: React.ReactNode;
}) {
  if (!children) return null;
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2 text-[11px] font-semibold uppercase tracking-wider text-zinc-500">
        <Icon className="h-3.5 w-3.5" />
        {title}
      </div>
      {children}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Risk signal bar                                                    */
/* ------------------------------------------------------------------ */
function SignalBar({
  label,
  value,
  maxValue = 1,
  description,
  color,
}: {
  label: string;
  value: number;
  maxValue?: number;
  description?: string;
  color: string;
}) {
  const pct = Math.min(100, (value / maxValue) * 100);
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-zinc-300">
          {label}
        </span>
        <span className="text-[10px] font-mono text-zinc-500">
          {(value * 100).toFixed(1)}%
        </span>
      </div>
      <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className="h-full rounded-full"
          style={{ backgroundColor: color }}
        />
      </div>
      {description && (
        <p className="text-[10px] text-zinc-600 leading-relaxed">
          {description}
        </p>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Exported component                                                 */
/* ------------------------------------------------------------------ */
export function ExplanationPanel({
  explanation,
}: {
  explanation: AnalysisResult['explanation'];
}) {
  const [expanded, setExpanded] = useState(false);

  const phrases = explanation.highlights?.phrases ?? [];
  const urls = explanation.highlights?.urls ?? [];
  const sender = explanation.highlights?.sender;
  const senderFlags = sender?.flags ?? [];
  const domainAnalysis = explanation.highlights?.domain_analysis;
  const domainFlags = domainAnalysis?.flags ?? [];
  const factors = explanation.contributing_factors ?? [];
  const scoring = explanation.scoring_breakdown;

  const hasHighlights =
    phrases.length > 0 ||
    urls.length > 0 ||
    senderFlags.length > 0 ||
    domainFlags.length > 0;
  const hasFactors = factors.length > 0;
  const hasScoring = !!scoring;

  if (!hasHighlights && !hasFactors && !hasScoring) return null;

  return (
    <Card className="border border-zinc-800/60 bg-zinc-950/50 overflow-hidden">
      <CardContent className="p-0">
        {/* Toggle header */}
        <button
          onClick={() => setExpanded(!expanded)}
          className={cn(
            'flex w-full items-center justify-between px-5 py-3.5 text-left transition-colors',
            'hover:bg-zinc-800/20',
            expanded && 'border-b border-zinc-800/60',
          )}
        >
          <span className="text-xs font-semibold text-zinc-400 tracking-wider uppercase">
            Why this rating?
          </span>
          <div className="flex items-center gap-1.5 text-[11px] text-zinc-500">
            {expanded ? 'Collapse' : 'Expand'}
            {expanded ? (
              <ChevronUp className="h-3.5 w-3.5" />
            ) : (
              <ChevronDown className="h-3.5 w-3.5" />
            )}
          </div>
        </button>

        <AnimatePresence>
          {expanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="overflow-hidden"
            >
              <div className="px-5 py-4 space-y-5">
                {/* ── Risk Signals / Contributing Factors ── */}
                {hasFactors && (
                  <Section icon={BarChart2} title="Risk Signals">
                    <div className="space-y-3">
                      {factors
                        .filter(
                          (f) =>
                            f.description &&
                            !f.factor.includes('_weight') &&
                            !f.description.includes('heuristic fallback')
                        )
                        .map((f, i) => {
                          const isAI =
                            f.factor.includes('ai') ||
                            f.factor.includes('model');
                          const barColor = isAI ? '#06b6d4' : '#f59e0b';
                          const score =
                            f.raw_score ?? f.weight ?? 0;
                          return (
                            <SignalBar
                              key={i}
                              label={f.description}
                              value={score}
                              color={barColor}
                            />
                          );
                        })}
                    </div>
                  </Section>
                )}

                {/* ── Scoring Breakdown ── */}
                {hasScoring && scoring && (
                  <>
                    <Separator className="bg-zinc-800/60" />
                    <Section icon={BarChart2} title="Score Breakdown">
                      <div className="space-y-2.5">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-zinc-400">AI Model</span>
                          <span className="font-mono text-cyan-400">
                            {scoring.ai_contribution.toFixed(1)} / {Math.round(scoring.ai_weight * 100)}
                          </span>
                        </div>
                        <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{
                              width: `${Math.min(100, (scoring.ai_contribution / (scoring.ai_weight * 100)) * 100)}%`,
                            }}
                            transition={{ duration: 0.8 }}
                            className="h-full rounded-full bg-cyan-500"
                          />
                        </div>

                        <div className="flex items-center justify-between text-xs">
                          <span className="text-zinc-400">Heuristic Rules</span>
                          <span className="font-mono text-amber-400">
                            {scoring.rule_contribution.toFixed(1)} / {Math.round(scoring.rule_weight * 100)}
                          </span>
                        </div>
                        <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{
                              width: `${Math.min(100, (scoring.rule_contribution / (scoring.rule_weight * 100)) * 100)}%`,
                            }}
                            transition={{ duration: 0.8, delay: 0.1 }}
                            className="h-full rounded-full bg-amber-500"
                          />
                        </div>

                        {scoring.formula && (
                          <p className="text-[9px] font-mono text-zinc-700 pt-1">
                            {scoring.formula}
                          </p>
                        )}
                      </div>
                    </Section>
                  </>
                )}

                {/* ── Suspicious Phrases ── */}
                {phrases.length > 0 && (
                  <>
                    <Separator className="bg-zinc-800/60" />
                    <Section icon={AlertCircle} title="Suspicious Phrases">
                      <div className="space-y-1.5">
                        {phrases.map((p, i) => (
                          <div
                            key={i}
                            className="flex items-start gap-2.5 rounded-lg bg-zinc-800/30 border border-zinc-800/40 px-3 py-2"
                          >
                            <AlertCircle className="h-3.5 w-3.5 text-amber-400 mt-0.5 shrink-0" />
                            <div className="min-w-0">
                              <span className="text-xs font-medium text-amber-300">
                                &ldquo;{p.text}&rdquo;
                              </span>
                              <p className="text-[10px] text-zinc-500 mt-0.5">
                                {p.reason}
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </Section>
                  </>
                )}

                {/* ── Flagged URLs ── */}
                {urls.length > 0 && (
                  <>
                    <Separator className="bg-zinc-800/60" />
                    <Section icon={Link2} title="Flagged URLs">
                      <div className="space-y-2">
                        {urls.map((u, i) => (
                          <div
                            key={i}
                            className="rounded-lg bg-zinc-800/30 border border-zinc-800/40 px-3 py-2"
                          >
                            <p className="font-mono text-[11px] text-red-400 break-all">
                              {u.url}
                            </p>
                            {u.flags?.length > 0 && (
                              <div className="mt-1.5 flex flex-wrap gap-1">
                                {u.flags.map((f, fi) => (
                                  <Badge
                                    key={fi}
                                    variant="outline"
                                    className="text-[9px] border-red-500/30 text-red-400 px-1.5 py-0"
                                  >
                                    {f}
                                  </Badge>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </Section>
                  </>
                )}

                {/* ── Sender Analysis ── */}
                {sender && senderFlags.length > 0 && (
                  <>
                    <Separator className="bg-zinc-800/60" />
                    <Section icon={User} title="Sender Analysis">
                      <div className="rounded-lg bg-zinc-800/30 border border-zinc-800/40 px-3 py-2">
                        <p className="font-mono text-[11px] text-zinc-300">
                          {sender.email}
                        </p>
                        <div className="mt-1.5 flex flex-wrap gap-1">
                          {senderFlags.map((f, i) => (
                            <Badge
                              key={i}
                              variant="outline"
                              className="text-[9px] border-amber-500/30 text-amber-400 px-1.5 py-0"
                            >
                              {f}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </Section>
                  </>
                )}

                {/* ── Domain Analysis ── */}
                {domainAnalysis && domainFlags.length > 0 && (
                  <>
                    <Separator className="bg-zinc-800/60" />
                    <Section icon={Globe} title="Domain Analysis">
                      <div className="rounded-lg bg-zinc-800/30 border border-zinc-800/40 px-3 py-2">
                        <p className="font-mono text-[11px] text-zinc-300">
                          {domainAnalysis.domain}
                        </p>
                        <div className="mt-1.5 flex flex-wrap gap-1">
                          {domainFlags.map((f, i) => (
                            <Badge
                              key={i}
                              variant="outline"
                              className="text-[9px] border-red-500/30 text-red-400 px-1.5 py-0"
                            >
                              {f}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </Section>
                  </>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </CardContent>
    </Card>
  );
}