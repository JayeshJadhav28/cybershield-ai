'use client';

import { cn } from '@/lib/utils';
import { Award } from 'lucide-react';

/* ------------------------------------------------------------------ */
/*  Badge config                                                       */
/* ------------------------------------------------------------------ */
const BADGE_CONFIG = {
  gold: {
    emoji: '🥇',
    label: 'Gold',
    color: 'text-amber-400',
    bg: 'bg-amber-500/10',
    border: 'border-amber-500/30',
    glow: 'shadow-amber-500/20',
  },
  silver: {
    emoji: '🥈',
    label: 'Silver',
    color: 'text-zinc-300',
    bg: 'bg-zinc-400/10',
    border: 'border-zinc-400/30',
    glow: 'shadow-zinc-400/10',
  },
  bronze: {
    emoji: '🥉',
    label: 'Bronze',
    color: 'text-orange-400',
    bg: 'bg-orange-500/10',
    border: 'border-orange-500/30',
    glow: 'shadow-orange-500/10',
  },
} as const;

type BadgeLevel = keyof typeof BADGE_CONFIG;

/* ------------------------------------------------------------------ */
/*  Component                                                          */
/* ------------------------------------------------------------------ */
interface BadgeDisplayProps {
  badge: string | null;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

export function BadgeDisplay({
  badge,
  size = 'md',
  showLabel = true,
  className,
}: BadgeDisplayProps) {
  if (!badge || !(badge in BADGE_CONFIG)) {
    return (
      <div
        className={cn(
          'flex items-center gap-1.5 text-zinc-600',
          className,
        )}
      >
        <Award
          className={cn(
            size === 'sm' && 'h-4 w-4',
            size === 'md' && 'h-5 w-5',
            size === 'lg' && 'h-8 w-8',
          )}
        />
        {showLabel && <span className="text-xs">No badge</span>}
      </div>
    );
  }

  const cfg = BADGE_CONFIG[badge as BadgeLevel];

  return (
    <div
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full border px-3 py-1',
        cfg.bg,
        cfg.border,
        cfg.glow,
        'shadow-sm',
        className,
      )}
    >
      <span
        className={cn(
          size === 'sm' && 'text-base',
          size === 'md' && 'text-xl',
          size === 'lg' && 'text-3xl',
        )}
      >
        {cfg.emoji}
      </span>
      {showLabel && (
        <span
          className={cn(
            'font-semibold',
            cfg.color,
            size === 'sm' && 'text-xs',
            size === 'md' && 'text-sm',
            size === 'lg' && 'text-lg',
          )}
        >
          {cfg.label}
        </span>
      )}
    </div>
  );
}

export { BADGE_CONFIG };
export type { BadgeLevel };