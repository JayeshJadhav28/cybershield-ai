'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  CheckCircle2,
  XCircle,
  RotateCcw,
  ArrowRight,
  Trophy,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';
import { BadgeDisplay } from './badge-display';
import type { QuizSessionResult } from '@/hooks/use-quiz';
import Link from 'next/link';

/* ------------------------------------------------------------------ */
/*  Score ring                                                         */
/* ------------------------------------------------------------------ */
function ScoreRing({ score }: { score: number }) {
  const radius = 55;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  const color =
    score >= 90
      ? '#f59e0b'
      : score >= 70
        ? '#a1a1aa'
        : score >= 50
          ? '#c2410c'
          : '#ef4444';

  return (
    <div className="relative flex h-36 w-36 items-center justify-center">
      <svg viewBox="0 0 140 140" className="absolute inset-0 -rotate-90">
        <circle
          cx="70"
          cy="70"
          r={radius}
          fill="none"
          stroke="#27272a"
          strokeWidth="8"
        />
        <motion.circle
          cx="70"
          cy="70"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.2, ease: 'easeOut' }}
        />
      </svg>
      <div className="relative flex flex-col items-center">
        <span
          className="font-mono text-3xl font-bold"
          style={{ color }}
        >
          {score}%
        </span>
        <span className="text-[10px] uppercase tracking-widest text-zinc-500">
          Score
        </span>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Props                                                              */
/* ------------------------------------------------------------------ */
interface QuizResultProps {
  result: QuizSessionResult;
  onRetry: () => void;
}

/* ------------------------------------------------------------------ */
/*  Component                                                          */
/* ------------------------------------------------------------------ */
export function QuizResult({ result, onRetry }: QuizResultProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Score card */}
      <Card className="border-zinc-800/60 bg-zinc-900/70 backdrop-blur-sm">
        <CardContent className="flex flex-col items-center gap-6 p-8 text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-cyan-500/10">
            <Trophy className="h-6 w-6 text-cyan-400" />
          </div>

          <div>
            <h2 className="text-xl font-bold text-zinc-100">Quiz Complete!</h2>
            <p className="mt-1 text-sm text-zinc-400">
              You answered{' '}
              <span className="font-mono font-semibold text-zinc-200">
                {result.correct_count}
              </span>{' '}
              out of{' '}
              <span className="font-mono font-semibold text-zinc-200">
                {result.total_questions}
              </span>{' '}
              correctly
            </p>
          </div>

          <ScoreRing score={result.score_pct} />

          {/* Badge */}
          {result.badge_earned && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.5, type: 'spring', stiffness: 200 }}
            >
              <div className="text-center space-y-2">
                <p className="text-xs uppercase tracking-wider text-zinc-500">
                  Badge Earned
                </p>
                <BadgeDisplay badge={result.badge_earned} size="lg" />
              </div>
            </motion.div>
          )}

          {/* Actions */}
          <div className="flex flex-wrap justify-center gap-3">
            <Button
              variant="outline"
              onClick={onRetry}
              className="gap-1.5 border-zinc-700 text-zinc-300 hover:bg-zinc-800"
            >
              <RotateCcw className="h-4 w-4" />
              Try Again
            </Button>
            <Link href="/awareness/quizzes">
              <Button className="gap-1.5 bg-cyan-600 text-white hover:bg-cyan-500">
                More Quizzes
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>

      {/* Answer review */}
      <Card className="border-zinc-800/60 bg-zinc-900/70 backdrop-blur-sm">
        <CardContent className="p-5 space-y-4">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-zinc-400">
            Answer Review
          </h3>

          <div className="space-y-3">
            {result.results.map((r, i) => (
              <div
                key={r.question_id}
                className={cn(
                  'rounded-lg border p-4 space-y-2',
                  r.is_correct
                    ? 'border-emerald-500/20 bg-emerald-500/5'
                    : 'border-red-500/20 bg-red-500/5',
                )}
              >
                <div className="flex items-start gap-2">
                  {r.is_correct ? (
                    <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-400" />
                  ) : (
                    <XCircle className="mt-0.5 h-4 w-4 shrink-0 text-red-400" />
                  )}
                  <div className="flex-1 space-y-1">
                    <p className="text-xs font-medium text-zinc-300">
                      Question {i + 1}
                    </p>
                    <p className="text-xs leading-relaxed text-zinc-400">
                      {r.explanation}
                    </p>
                    {!r.is_correct && (
                      <p className="text-[11px] text-zinc-500">
                        Your answer:{' '}
                        <span className="text-red-400">
                          Option {String.fromCharCode(65 + r.selected_option_index)}
                        </span>{' '}
                        · Correct:{' '}
                        <span className="text-emerald-400">
                          Option {String.fromCharCode(65 + r.correct_option_index)}
                        </span>
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}