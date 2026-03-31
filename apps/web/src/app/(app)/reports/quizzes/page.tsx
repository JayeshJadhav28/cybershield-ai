'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { PageHeader } from '@/components/shared/page-header';
import { EmptyState } from '@/components/shared/empty-state';
import { LoadingSpinner } from '@/components/shared/loading-spinner';
import { BadgeDisplay } from '@/components/awareness/badge-display';
import {
  Trophy,
  Brain,
  Target,
  TrendingUp,
  Calendar,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { api } from '@/lib/api';
import { motion } from 'framer-motion';

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */
interface CategoryScore {
  attempts: number;
  best_score: number;
  average_score: number;
}

interface AwarenessSummary {
  total_quizzes_completed: number;
  average_score_pct: number;
  badges: { category: string; badge: string; earned_at: string }[];
  category_scores: Record<string, CategoryScore>;
  weakest_category: string;
  scenarios_completed: number;
}

/* ------------------------------------------------------------------ */
/*  Stat card                                                          */
/* ------------------------------------------------------------------ */
function StatItem({
  icon: Icon,
  label,
  value,
  color,
}: {
  icon: React.ElementType;
  label: string;
  value: string | number;
  color: string;
}) {
  return (
    <div className="rounded-xl border border-zinc-800/60 bg-zinc-800/30 p-4 text-center">
      <Icon className={cn('mx-auto h-5 w-5', color)} />
      <p className="mt-2 font-mono text-xl font-bold text-zinc-200">{value}</p>
      <p className="mt-0.5 text-[11px] text-zinc-500">{label}</p>
    </div>
  );
}

const CATEGORY_LABELS: Record<string, string> = {
  phishing: 'Phishing',
  upi_qr: 'UPI & QR',
  deepfake: 'Deepfake',
  kyc_otp: 'KYC & OTP',
  general: 'General',
};

/* ------------------------------------------------------------------ */
/*  Page                                                               */
/* ------------------------------------------------------------------ */
export default function QuizReportPage() {
  const [data, setData] = useState<AwarenessSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    api
      .getAwarenessSummary()
      .then((res: any) => {
        if (!cancelled) setData(res);
      })
      .catch(() => {
        if (!cancelled) setData(null);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <LoadingSpinner label="Loading quiz history…" />
      </div>
    );
  }

  if (!data || data.total_quizzes_completed === 0) {
    return (
      <div className="space-y-6">
        <PageHeader title="Quiz History & Badges" icon={Trophy} />
        <EmptyState
          title="No quizzes completed yet"
          description="Take your first quiz to track progress and earn badges."
          action={{ label: 'Start a Quiz', href: '/awareness/quizzes' }}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Quiz History & Badges"
        description="Track your cyber-awareness progress and earned badges."
        icon={Trophy}
      />

      {/* Overview stats */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatItem icon={Brain} label="Quizzes Completed" value={data.total_quizzes_completed} color="text-cyan-400" />
        <StatItem icon={Target} label="Average Score" value={`${data.average_score_pct}%`} color="text-purple-400" />
        <StatItem icon={TrendingUp} label="Weakest Area" value={CATEGORY_LABELS[data.weakest_category] ?? data.weakest_category} color="text-amber-400" />
        <StatItem icon={Calendar} label="Scenarios Done" value={data.scenarios_completed} color="text-emerald-400" />
      </div>

      {/* Badges */}
      <Card className="border-zinc-800/60 bg-zinc-900/70 backdrop-blur-sm">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-semibold uppercase tracking-wider text-zinc-400">
            Earned Badges
          </CardTitle>
        </CardHeader>
        <CardContent>
          {data.badges.length === 0 ? (
            <p className="py-4 text-center text-xs text-zinc-600">
              Score ≥ 50% to earn your first badge.
            </p>
          ) : (
            <div className="flex flex-wrap gap-3">
              {data.badges.map((b, i) => (
                <motion.div
                  key={`${b.category}-${b.badge}`}
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: i * 0.1, type: 'spring', stiffness: 200 }}
                  className="flex flex-col items-center gap-1.5 rounded-xl border border-zinc-800 bg-zinc-800/30 p-3"
                >
                  <BadgeDisplay badge={b.badge} size="md" showLabel={false} />
                  <span className="text-[10px] font-medium text-zinc-400">
                    {CATEGORY_LABELS[b.category] ?? b.category}
                  </span>
                </motion.div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Category breakdown */}
      <Card className="border-zinc-800/60 bg-zinc-900/70 backdrop-blur-sm">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-semibold uppercase tracking-wider text-zinc-400">
            Category Breakdown
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Object.entries(data.category_scores).map(([cat, score]) => {
              const label = CATEGORY_LABELS[cat] ?? cat;
              return (
                <div key={cat} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-medium text-zinc-300">{label}</span>
                    <span className="text-zinc-500">
                      {score.attempts} attempts · Best: {score.best_score}%
                    </span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-zinc-800">
                    <motion.div
                      className={cn(
                        'h-full rounded-full',
                        score.average_score >= 70 ? 'bg-emerald-500' : score.average_score >= 50 ? 'bg-amber-500' : 'bg-red-500',
                      )}
                      initial={{ width: 0 }}
                      animate={{ width: `${score.average_score}%` }}
                      transition={{ duration: 0.8 }}
                    />
                  </div>
                  <p className="text-right font-mono text-[11px] text-zinc-500">
                    Avg: {score.average_score}%
                  </p>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}