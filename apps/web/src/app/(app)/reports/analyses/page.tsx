'use client';

import { useEffect, useState, useCallback } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { PageHeader } from '@/components/shared/page-header';
import { EmptyState } from '@/components/shared/empty-state';
import {
  FileText,
  Mail,
  Link2,
  QrCode,
  Mic,
  Video,
  Image as ImageIcon,
  ShieldCheck,
  AlertTriangle,
  ShieldAlert,
  ChevronLeft,
  ChevronRight,
  Clock,
  Filter,
  RefreshCw,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { api } from '@/lib/api';
import { motion } from 'framer-motion';

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */
interface AnalysisSummary {
  id: string;
  type: 'email' | 'url' | 'qr' | 'audio' | 'video' | 'image';
  risk_score: number;
  risk_label: 'safe' | 'suspicious' | 'dangerous';
  explanation_summary: string;
  created_at: string;
  is_demo?: boolean;
  processing_time_ms?: number;
}

/* ------------------------------------------------------------------ */
/*  Config maps                                                        */
/* ------------------------------------------------------------------ */
const TYPE_META: Record<
  string,
  { icon: React.ElementType; label: string; color: string }
> = {
  email: { icon: Mail, label: 'Email', color: 'text-cyan-400' },
  url: { icon: Link2, label: 'URL', color: 'text-blue-400' },
  qr: { icon: QrCode, label: 'QR', color: 'text-indigo-400' },
  audio: { icon: Mic, label: 'Audio', color: 'text-purple-400' },
  video: { icon: Video, label: 'Video', color: 'text-rose-400' },
  image: { icon: ImageIcon, label: 'Image', color: 'text-teal-400' },
};

const LABEL_META: Record<
  string,
  { icon: React.ElementType; cls: string }
> = {
  safe: {
    icon: ShieldCheck,
    cls: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400',
  },
  suspicious: {
    icon: AlertTriangle,
    cls: 'border-amber-500/30 bg-amber-500/10 text-amber-400',
  },
  dangerous: {
    icon: ShieldAlert,
    cls: 'border-red-500/30 bg-red-500/10 text-red-400',
  },
};

function fmtDate(d: string) {
  try {
    return new Date(d).toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return d;
  }
}

/* ------------------------------------------------------------------ */
/*  Skeleton rows                                                      */
/* ------------------------------------------------------------------ */
function SkeletonTable() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 6 }).map((_, i) => (
        <div
          key={i}
          className="flex items-center gap-4 rounded-lg border border-zinc-800/40 bg-zinc-900/40 p-4"
        >
          <Skeleton className="h-9 w-9 rounded-lg" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-3.5 w-3/4" />
            <Skeleton className="h-3 w-1/2" />
          </div>
          <Skeleton className="h-5 w-20 rounded-full" />
          <Skeleton className="h-4 w-8" />
        </div>
      ))}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Page                                                               */
/* ------------------------------------------------------------------ */
export default function AnalysesReportPage() {
  const [analyses, setAnalyses] = useState<AnalysisSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [mounted, setMounted] = useState(false);
  const limit = 10;

  // Prevent hydration mismatch from Select (Radix generates random IDs)
  useEffect(() => {
    setMounted(true);
  }, []);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      // api.getAnalysisHistory returns { total, page, limit, items: [...] }
      const res = await api.getAnalysisHistory(page, limit);
      let items: AnalysisSummary[] = (res.items ?? []) as AnalysisSummary[];

      // Client-side type filter
      if (typeFilter !== 'all') {
        items = items.filter((a) => a.type === typeFilter);
      }

      setAnalyses(items);
      setTotal(res.total ?? 0);
    } catch {
      // Fallback to local cache
      const local = api.getLocalAnalyses() as AnalysisSummary[];
      let items = local;
      if (typeFilter !== 'all') {
        items = items.filter((a) => a.type === typeFilter);
      }
      setAnalyses(items.slice(0, limit));
      setTotal(local.length);
    } finally {
      setLoading(false);
    }
  }, [page, typeFilter]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Refetch on window focus
  useEffect(() => {
    const onFocus = () => fetchData();
    window.addEventListener('focus', onFocus);
    return () => window.removeEventListener('focus', onFocus);
  }, [fetchData]);

  // Refetch on cross-tab storage change
  useEffect(() => {
    const onStorage = (e: StorageEvent) => {
      if (e.key === 'cs-recent-analyses') {
        fetchData();
      }
    };
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, [fetchData]);

  const totalPages = Math.max(1, Math.ceil(total / limit));

  return (
    <div className="space-y-6">
      <PageHeader
        title="Analysis History"
        description="View all your past threat analyses and their results."
        icon={FileText}
      />

      {/* Filters — only render after mount to avoid hydration mismatch */}
      {mounted && (
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-xs text-zinc-500">
              <Filter className="h-3.5 w-3.5" />
              Filter by type:
            </div>
            <Select
              value={typeFilter}
              onValueChange={(v) => {
                setTypeFilter(v);
                setPage(1);
              }}
            >
              <SelectTrigger className="h-8 w-32 border-zinc-700 bg-zinc-800/60 text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="border-zinc-800 bg-zinc-900">
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="email">Email</SelectItem>
                <SelectItem value="url">URL</SelectItem>
                <SelectItem value="qr">QR</SelectItem>
                <SelectItem value="audio">Audio</SelectItem>
                <SelectItem value="image">Image</SelectItem>
                <SelectItem value="video">Video</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Button
            variant="ghost"
            size="sm"
            onClick={() => fetchData()}
            disabled={loading}
            className="h-7 gap-1.5 text-xs text-zinc-500 hover:text-zinc-300"
          >
            <RefreshCw
              className={cn('h-3.5 w-3.5', loading && 'animate-spin')}
            />
            Refresh
          </Button>
        </div>
      )}

      {/* Table */}
      <Card className="border-zinc-800/60 bg-zinc-900/70 backdrop-blur-sm">
        <CardContent className="p-4">
          {loading ? (
            <SkeletonTable />
          ) : analyses.length === 0 ? (
            <EmptyState
              title="No analyses found"
              description="Run your first analysis to see results here."
              action={{ label: 'Start Analyzing', href: '/analyze/email' }}
            />
          ) : (
            <div className="space-y-2">
              {analyses.map((a, i) => {
                const tm = TYPE_META[a.type] ?? TYPE_META.email;
                const lm = LABEL_META[a.risk_label] ?? LABEL_META.safe;
                const TypeIcon = tm.icon;
                const LabelIcon = lm.icon;

                return (
                  <motion.div
                    key={a.id}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.03 }}
                    className="flex items-center gap-4 rounded-lg border border-zinc-800/40 bg-zinc-800/20 p-4 transition-colors hover:bg-zinc-800/40"
                  >
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-zinc-800/80">
                      <TypeIcon className={cn('h-4 w-4', tm.color)} />
                    </div>

                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <Badge
                          variant="outline"
                          className="border-zinc-700 text-[10px] text-zinc-500"
                        >
                          {tm.label}
                        </Badge>
                        {a.is_demo && (
                          <Badge
                            variant="outline"
                            className="border-zinc-700 text-[10px] text-zinc-600"
                          >
                            Demo
                          </Badge>
                        )}
                      </div>
                      <p className="mt-1 truncate text-sm text-zinc-300">
                        {a.explanation_summary || `${tm.label} analysis`}
                      </p>
                      <p className="mt-0.5 flex items-center gap-1 text-[11px] text-zinc-600">
                        <Clock className="h-3 w-3" />
                        {fmtDate(a.created_at)}
                        {a.processing_time_ms != null && (
                          <>
                            <span className="mx-1">•</span>
                            {a.processing_time_ms}ms
                          </>
                        )}
                      </p>
                    </div>

                    <div className="flex shrink-0 items-center gap-3">
                      <span className="font-mono text-sm font-bold text-zinc-300">
                        {a.risk_score}
                      </span>
                      <Badge
                        variant="outline"
                        className={cn(
                          'gap-1 text-[11px] font-semibold',
                          lm.cls
                        )}
                      >
                        <LabelIcon className="h-3 w-3" />
                        {a.risk_label}
                      </Badge>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-3">
          <Button
            variant="outline"
            size="sm"
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
            className="h-8 gap-1 border-zinc-700 text-xs"
          >
            <ChevronLeft className="h-3.5 w-3.5" />
            Previous
          </Button>
          <span className="font-mono text-xs text-zinc-500">
            {page} / {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={page >= totalPages}
            onClick={() => setPage((p) => p + 1)}
            className="h-8 gap-1 border-zinc-700 text-xs"
          >
            Next
            <ChevronRight className="h-3.5 w-3.5" />
          </Button>
        </div>
      )}
    </div>
  );
}