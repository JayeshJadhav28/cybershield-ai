'use client';

import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Mail,
  Link2,
  QrCode,
  Mic,
  Video,
  Image as ImageIcon,
  ArrowRight,
  ShieldCheck,
  AlertTriangle,
  ShieldAlert,
  SearchX,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */
export interface RecentAnalysis {
  id: string;
  type: 'email' | 'url' | 'qr' | 'audio' | 'video' | 'image';
  risk_score: number;
  risk_label: 'safe' | 'suspicious' | 'dangerous';
  explanation_summary: string;
  created_at: string;
}

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */
const typeConfig: Record<
  RecentAnalysis['type'],
  { icon: React.ElementType; label: string; color: string }
> = {
  email: { icon: Mail, label: 'Email', color: 'text-cyan-400' },
  url: { icon: Link2, label: 'URL', color: 'text-blue-400' },
  qr: { icon: QrCode, label: 'QR', color: 'text-indigo-400' },
  audio: { icon: Mic, label: 'Audio', color: 'text-purple-400' },
  video: { icon: Video, label: 'Video', color: 'text-rose-400' },
  image: { icon: ImageIcon, label: 'Image', color: 'text-teal-400' },
};

const labelConfig: Record<
  RecentAnalysis['risk_label'],
  { icon: React.ElementType; className: string }
> = {
  safe: {
    icon: ShieldCheck,
    className: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400',
  },
  suspicious: {
    icon: AlertTriangle,
    className: 'border-amber-500/30 bg-amber-500/10 text-amber-400',
  },
  dangerous: {
    icon: ShieldAlert,
    className: 'border-red-500/30 bg-red-500/10 text-red-400',
  },
};

function timeAgo(dateStr: string): string {
  const seconds = Math.floor(
    (Date.now() - new Date(dateStr).getTime()) / 1000,
  );
  if (seconds < 0) return 'just now';
  if (seconds < 60) return 'just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;
  return new Date(dateStr).toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
  });
}

/* ------------------------------------------------------------------ */
/*  Loading skeleton                                                   */
/* ------------------------------------------------------------------ */
function SkeletonRows() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="flex items-center gap-3">
          <Skeleton className="h-9 w-9 rounded-lg" />
          <div className="flex-1 space-y-1.5">
            <Skeleton className="h-3.5 w-3/4" />
            <Skeleton className="h-3 w-1/2" />
          </div>
          <Skeleton className="h-5 w-16 rounded-full" />
        </div>
      ))}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Empty state                                                        */
/* ------------------------------------------------------------------ */
function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-10 text-center">
      <div className="mb-3 flex h-14 w-14 items-center justify-center rounded-2xl bg-zinc-800/80">
        <SearchX className="h-7 w-7 text-zinc-500" />
      </div>
      <p className="text-sm font-medium text-zinc-400">No analyses yet</p>
      <p className="mt-1 text-xs text-zinc-500">
        Run your first scan to see results here
      </p>
      <Link href="/analyze/email">
        <Button
          variant="outline"
          size="sm"
          className="mt-4 border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10"
        >
          Start Analyzing
          <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
        </Button>
      </Link>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Single row                                                         */
/* ------------------------------------------------------------------ */
function AnalysisRow({
  analysis,
  index,
}: {
  analysis: RecentAnalysis;
  index: number;
}) {
  const tCfg = typeConfig[analysis.type] ?? typeConfig.email;
  const lCfg = labelConfig[analysis.risk_label] ?? labelConfig.safe;
  const TypeIcon = tCfg.icon;
  const LabelIcon = lCfg.icon;

  return (
    <motion.div
      initial={{ opacity: 0, x: -12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.35, delay: 0.05 * index }}
    >
      <Link
        href="/reports/analyses"
        className={cn(
          'flex items-center gap-3 rounded-lg px-3 py-2.5',
          'transition-colors duration-200 hover:bg-zinc-800/60',
        )}
      >
        {/* Type icon */}
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-zinc-800/80">
          <TypeIcon className={cn('h-4 w-4', tCfg.color)} />
        </div>

        {/* Summary */}
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-medium text-zinc-200">
            {analysis.explanation_summary || `${tCfg.label} analysis`}
          </p>
          <div className="flex items-center gap-2">
            <p className="text-xs text-zinc-500">
              {timeAgo(analysis.created_at)}
            </p>
            <span className="text-xs text-zinc-600">•</span>
            <p className="text-xs text-zinc-500">
              Score: {analysis.risk_score}
            </p>
          </div>
        </div>

        {/* Risk badge */}
        <Badge
          variant="outline"
          className={cn(
            'shrink-0 gap-1 border text-[11px] font-semibold uppercase',
            lCfg.className,
          )}
        >
          <LabelIcon className="h-3 w-3" />
          {analysis.risk_label}
        </Badge>
      </Link>
    </motion.div>
  );
}

/* ------------------------------------------------------------------ */
/*  Exported component                                                 */
/* ------------------------------------------------------------------ */
export function RecentAnalyses({
  analyses,
  isLoading = false,
}: {
  analyses: RecentAnalysis[];
  isLoading?: boolean;
}) {
  return (
    <Card className="border-zinc-800/60 bg-zinc-900/70 backdrop-blur-sm">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-semibold uppercase tracking-wider text-zinc-400">
          Recent Analyses
        </CardTitle>
        {analyses.length > 0 && (
          <Link href="/reports/analyses">
            <Button
              variant="ghost"
              size="sm"
              className="h-7 text-xs text-zinc-500 hover:text-cyan-400"
            >
              View All
              <ArrowRight className="ml-1 h-3 w-3" />
            </Button>
          </Link>
        )}
      </CardHeader>
      <CardContent className="px-3 pb-3">
        {isLoading ? (
          <SkeletonRows />
        ) : analyses.length === 0 ? (
          <EmptyState />
        ) : (
          <div className="space-y-0.5">
            {analyses.map((a, i) => (
              <AnalysisRow key={a.id} analysis={a} index={i} />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}