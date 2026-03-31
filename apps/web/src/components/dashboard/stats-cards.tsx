'use client';

import { useEffect, useState, useCallback } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import {
  Shield,
  AlertTriangle,
  Brain,
  Award,
  TrendingUp,
  TrendingDown,
  Minus,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';

/* ------------------------------------------------------------------ */
/*  Animated number counter                                           */
/* ------------------------------------------------------------------ */
function useAnimatedCounter(target: number, duration = 1200) {
  const [value, setValue] = useState(0);

  useEffect(() => {
    if (target === 0) {
      setValue(0);
      return;
    }

    let start: number | null = null;
    let raf: number;

    const step = (ts: number) => {
      if (!start) start = ts;
      const progress = Math.min((ts - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
      setValue(Math.round(eased * target));
      if (progress < 1) raf = requestAnimationFrame(step);
    };

    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [target, duration]);

  return value;
}

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */
export interface DashboardStats {
  totalScans: number;
  threatsDetected: number;
  awarenessScore: number; // 0-100
  badgesEarned: number;
  /** Optional deltas vs previous period (positive = up) */
  scansDelta?: number;
  threatsDelta?: number;
}

interface StatCardDef {
  title: string;
  value: number;
  suffix?: string;
  icon: React.ElementType;
  iconColor: string;
  iconBg: string;
  glowColor: string;
  delta?: number;
}

/* ------------------------------------------------------------------ */
/*  Single stat card                                                   */
/* ------------------------------------------------------------------ */
function StatCard({
  card,
  index,
}: {
  card: StatCardDef;
  index: number;
}) {
  const displayValue = useAnimatedCounter(card.value);

  const TrendIcon =
    card.delta === undefined || card.delta === 0
      ? Minus
      : card.delta > 0
        ? TrendingUp
        : TrendingDown;

  const trendColor =
    card.delta === undefined || card.delta === 0
      ? 'text-zinc-500'
      : card.delta > 0
        ? 'text-emerald-400'
        : 'text-red-400';

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
    >
      <Card
        className={cn(
          'relative overflow-hidden border-zinc-800/60 bg-zinc-900/70 backdrop-blur-sm',
          'transition-all duration-300 hover:border-zinc-700/80',
          'group',
        )}
      >
        {/* subtle top glow line */}
        <div
          className="absolute inset-x-0 top-0 h-[2px] opacity-60 transition-opacity group-hover:opacity-100"
          style={{
            background: `linear-gradient(90deg, transparent, ${card.glowColor}, transparent)`,
          }}
        />

        <CardContent className="flex items-center gap-4 p-5">
          {/* Icon */}
          <div
            className={cn(
              'flex h-12 w-12 shrink-0 items-center justify-center rounded-xl',
              card.iconBg,
            )}
          >
            <card.icon className={cn('h-6 w-6', card.iconColor)} />
          </div>

          {/* Content */}
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium text-zinc-400">{card.title}</p>
            <div className="flex items-baseline gap-1.5">
              <span className="font-mono text-2xl font-bold tracking-tight text-zinc-100">
                {displayValue}
              </span>
              {card.suffix && (
                <span className="text-sm font-semibold text-zinc-400">
                  {card.suffix}
                </span>
              )}
            </div>
          </div>

          {/* Trend badge */}
          {card.delta !== undefined && (
            <div
              className={cn(
                'flex items-center gap-0.5 rounded-full px-2 py-0.5 text-xs font-medium',
                card.delta > 0 && 'bg-emerald-500/10',
                card.delta < 0 && 'bg-red-500/10',
                card.delta === 0 && 'bg-zinc-500/10',
                trendColor,
              )}
            >
              <TrendIcon className="h-3 w-3" />
              {card.delta !== 0 && (
                <span>{Math.abs(card.delta)}</span>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}

/* ------------------------------------------------------------------ */
/*  Exported component                                                 */
/* ------------------------------------------------------------------ */
export function StatsCards({ stats }: { stats: DashboardStats }) {
  const cards: StatCardDef[] = [
    {
      title: 'Total Scans',
      value: stats.totalScans,
      icon: Shield,
      iconColor: 'text-cyan-400',
      iconBg: 'bg-cyan-500/10',
      glowColor: '#06b6d4',
      delta: stats.scansDelta,
    },
    {
      title: 'Threats Detected',
      value: stats.threatsDetected,
      icon: AlertTriangle,
      iconColor: 'text-red-400',
      iconBg: 'bg-red-500/10',
      glowColor: '#ef4444',
      delta: stats.threatsDelta,
    },
    {
      title: 'Awareness Score',
      value: stats.awarenessScore,
      suffix: '%',
      icon: Brain,
      iconColor: 'text-purple-400',
      iconBg: 'bg-purple-500/10',
      glowColor: '#8b5cf6',
    },
    {
      title: 'Badges Earned',
      value: stats.badgesEarned,
      icon: Award,
      iconColor: 'text-amber-400',
      iconBg: 'bg-amber-500/10',
      glowColor: '#f59e0b',
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {cards.map((card, i) => (
        <StatCard key={card.title} card={card} index={i} />
      ))}
    </div>
  );
}