"use client";

import { useEffect, useMemo, useState, useCallback, useRef } from "react";
import { motion } from "framer-motion";
import { Shield, RefreshCw } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { QuickAccessTiles } from "@/components/dashboard/quick-access-tiles";
import {
  RecentAnalyses,
  type RecentAnalysis,
} from "@/components/dashboard/recent-analyses";
import {
  StatsCards,
  type DashboardStats,
} from "@/components/dashboard/stats-cards";
import {
  ThreatChart,
  type ThreatDistribution,
} from "@/components/dashboard/threat-chart";
import { useAuth } from "@/hooks/use-auth";
import { api } from "@/lib/api";
import type { AnalysisSummary } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const POLL_INTERVAL_MS = 30_000; // 30 seconds

function computeDistribution(analyses: RecentAnalysis[]): ThreatDistribution {
  return analyses.reduce(
    (acc, item) => {
      if (item.risk_label === "safe") acc.safe += 1;
      if (item.risk_label === "suspicious") acc.suspicious += 1;
      if (item.risk_label === "dangerous") acc.dangerous += 1;
      return acc;
    },
    { safe: 0, suspicious: 0, dangerous: 0 }
  );
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [analyses, setAnalyses] = useState<RecentAnalysis[]>([]);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  /* ── Fetch analyses ── */
  const loadAnalyses = useCallback(
    async (showSpinner = false) => {
      if (showSpinner) setIsRefreshing(true);

      try {
        const response = await api.getAnalysisHistory(1, 10);
        const items = (response.items ?? []) as RecentAnalysis[];
        setAnalyses(items);
        setLastUpdated(new Date());
      } catch {
        // On error, try to show local cache
        const local = api.getLocalAnalyses() as RecentAnalysis[];
        if (local.length > 0 && analyses.length === 0) {
          setAnalyses(local.slice(0, 10));
        }
      } finally {
        setIsLoading(false);
        setIsRefreshing(false);
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  );

  /* ── Initial load ── */
  useEffect(() => {
    loadAnalyses();
  }, [loadAnalyses]);

  /* ── Poll every 30s ── */
  useEffect(() => {
    pollRef.current = setInterval(() => {
      loadAnalyses(false);
    }, POLL_INTERVAL_MS);

    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [loadAnalyses]);

  /* ── Refetch on window focus ── */
  useEffect(() => {
    const onFocus = () => {
      loadAnalyses(false);
    };
    window.addEventListener("focus", onFocus);
    return () => window.removeEventListener("focus", onFocus);
  }, [loadAnalyses]);

  /* ── Refetch on storage change (cross-tab sync) ── */
  useEffect(() => {
    const onStorage = (e: StorageEvent) => {
      if (e.key === "cs-recent-analyses") {
        loadAnalyses(false);
      }
    };
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, [loadAnalyses]);

  /* ── Derived data ── */
  const distribution = useMemo(
    () => computeDistribution(analyses),
    [analyses]
  );

  const stats: DashboardStats = {
    totalScans: user?.stats?.total_analyses ?? analyses.length,
    threatsDetected: distribution.suspicious + distribution.dangerous,
    awarenessScore: Math.min(
      100,
      (user?.stats?.quizzes_completed ?? 0) * 10
    ),
    badgesEarned: user?.stats?.badges_earned?.length ?? 0,
  };

  /* ── Manual refresh ── */
  const handleRefresh = () => loadAnalyses(true);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Dashboard"
        description="Your cyber command center. Monitor threats and track your security awareness."
      >
        <div className="flex items-center gap-2">
          {/* Refresh button */}
          <Button
            variant="ghost"
            size="sm"
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="h-7 gap-1.5 text-xs text-zinc-500 hover:text-zinc-300"
          >
            <RefreshCw
              className={cn(
                "h-3.5 w-3.5",
                isRefreshing && "animate-spin"
              )}
            />
            {isRefreshing ? "Refreshing…" : "Refresh"}
          </Button>

          {/* Live badge */}
          <span className="inline-flex items-center gap-1 rounded-full border border-cs-cyan/30 bg-cs-cyan/10 px-2 py-0.5 text-xs text-cs-cyan">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-cs-cyan opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-cs-cyan" />
            </span>
            Live
          </span>
        </div>
      </PageHeader>

      <motion.div
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <p className="text-sm text-muted-foreground">
          Welcome back,{" "}
          {user?.display_name || user?.email?.split("@")[0] || "Analyst"}
          <span className="ml-1 inline-block origin-[70%_70%] animate-[wave_2s_ease-in-out_infinite]">
            👋
          </span>
        </p>
        {lastUpdated && (
          <p className="text-[10px] text-zinc-600 tabular-nums">
            Updated {lastUpdated.toLocaleTimeString()}
          </p>
        )}
      </motion.div>

      <StatsCards stats={stats} />
      <QuickAccessTiles />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-5">
        <div className="lg:col-span-3">
          <RecentAnalyses analyses={analyses} isLoading={isLoading} />
        </div>
        <div className="lg:col-span-2">
          <ThreatChart distribution={distribution} />
        </div>
      </div>
    </div>
  );
}