'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { PageHeader } from '@/components/shared/page-header';
import { LoadingSpinner } from '@/components/shared/loading-spinner';
import { EmptyState } from '@/components/shared/empty-state';
import {
  BarChart3,
  Users,
  Scan,
  Mail,
  Link2,
  QrCode,
  Mic,
  Video,
  ShieldCheck,
  AlertTriangle,
  ShieldAlert,
  Brain,
  TrendingDown,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { api } from '@/lib/api';
import { motion } from 'framer-motion';

interface OrgMetrics {
  org_id: string;
  period: string;
  total_users: number;
  total_analyses: number;
  analyses_by_type: Record<string, number>;
  risk_distribution: { safe: number; suspicious: number; dangerous: number };
  quiz_metrics: {
    total_sessions: number;
    average_score: number;
    weakest_category: string;
    completion_rate: number;
  };
}

function MetricCard({
  icon: Icon,
  label,
  value,
  color,
  sub,
}: {
  icon: React.ElementType;
  label: string;
  value: string | number;
  color: string;
  sub?: string;
}) {
  return (
    <Card className="border-zinc-800/60 bg-zinc-900/70">
      <CardContent className="flex items-center gap-4 p-5">
        <div className={cn('flex h-10 w-10 items-center justify-center rounded-xl', `bg-${color}-500/10`)}>
          <Icon className={cn('h-5 w-5', `text-${color}-400`)} />
        </div>
        <div>
          <p className="font-mono text-2xl font-bold text-zinc-100">{value}</p>
          <p className="text-xs text-zinc-500">{label}</p>
          {sub && <p className="text-[10px] text-zinc-600">{sub}</p>}
        </div>
      </CardContent>
    </Card>
  );
}

const TYPE_ICONS: Record<string, React.ElementType> = {
  email: Mail, url: Link2, qr: QrCode, audio: Mic, video: Video,
};

export default function AdminMetricsPage() {
  const [metrics, setMetrics] = useState<OrgMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    api
      .request<OrgMetrics>('/admin/metrics')
      .then((res) => { if (!cancelled) setMetrics(res); })
      .catch(() => { if (!cancelled) setMetrics(null); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, []);

  if (loading) return <div className="flex min-h-[40vh] items-center justify-center"><LoadingSpinner label="Loading metrics…" /></div>;

  if (!metrics) {
    return (
      <div className="space-y-6">
        <PageHeader title="Organization Metrics" icon={BarChart3} />
        <EmptyState title="Metrics unavailable" description="Sign in as an admin to view organization analytics." />
      </div>
    );
  }

  const rd = metrics.risk_distribution;
  const rdTotal = rd.safe + rd.suspicious + rd.dangerous || 1;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Organization Metrics"
        description={`Showing data for ${metrics.period.replace(/_/g, ' ')}`}
        icon={BarChart3}
      />

      {/* Top-level stats */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <MetricCard icon={Users} label="Total Users" value={metrics.total_users} color="cyan" />
        <MetricCard icon={Scan} label="Total Analyses" value={metrics.total_analyses} color="blue" />
        <MetricCard icon={Brain} label="Quiz Sessions" value={metrics.quiz_metrics.total_sessions} color="purple" />
        <MetricCard icon={TrendingDown} label="Weakest Category" value={metrics.quiz_metrics.weakest_category.replace(/_/g, ' ')} color="amber" sub={`Avg Score: ${metrics.quiz_metrics.average_score}%`} />
      </div>

      {/* Analysis by type */}
      <Card className="border-zinc-800/60 bg-zinc-900/70">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-semibold uppercase tracking-wider text-zinc-400">Analyses by Type</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-5 gap-3">
            {Object.entries(metrics.analyses_by_type).map(([type, count]) => {
              const Icon = TYPE_ICONS[type] ?? Scan;
              return (
                <div key={type} className="rounded-lg border border-zinc-800 bg-zinc-800/30 p-4 text-center">
                  <Icon className="mx-auto h-5 w-5 text-zinc-400" />
                  <p className="mt-2 font-mono text-lg font-bold text-zinc-200">{count}</p>
                  <p className="text-[10px] uppercase text-zinc-500">{type}</p>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Risk distribution */}
      <Card className="border-zinc-800/60 bg-zinc-900/70">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-semibold uppercase tracking-wider text-zinc-400">Risk Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[
              { key: 'safe', icon: ShieldCheck, color: 'emerald', count: rd.safe },
              { key: 'suspicious', icon: AlertTriangle, color: 'amber', count: rd.suspicious },
              { key: 'dangerous', icon: ShieldAlert, color: 'red', count: rd.dangerous },
            ].map((r) => (
              <div key={r.key} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="flex items-center gap-1.5 text-zinc-300">
                    <r.icon className={`h-3.5 w-3.5 text-${r.color}-400`} />
                    {r.key.charAt(0).toUpperCase() + r.key.slice(1)}
                  </span>
                  <span className="font-mono text-zinc-500">{r.count} ({Math.round((r.count / rdTotal) * 100)}%)</span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-zinc-800">
                  <motion.div
                    className={`h-full rounded-full bg-${r.color}-500`}
                    initial={{ width: 0 }}
                    animate={{ width: `${(r.count / rdTotal) * 100}%` }}
                    transition={{ duration: 0.8 }}
                  />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}