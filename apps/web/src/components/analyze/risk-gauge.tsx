'use client';

import { useEffect, useRef } from 'react';
import { cn } from '@/lib/utils';

interface RiskGaugeProps {
  score: number;
  label: 'safe' | 'suspicious' | 'dangerous';
  size?: number;
  className?: string;
}

const COLORS = {
  safe: { stroke: '#22c55e', text: '#22c55e', glow: '#22c55e40' },
  suspicious: { stroke: '#f59e0b', text: '#f59e0b', glow: '#f59e0b40' },
  dangerous: { stroke: '#ef4444', text: '#ef4444', glow: '#ef444440' },
};

const LABELS = {
  safe: 'Safe',
  suspicious: 'Suspicious',
  dangerous: 'Dangerous',
};

export function RiskGauge({
  score,
  label,
  size = 180,
  className,
}: RiskGaugeProps) {
  const circleRef = useRef<SVGCircleElement>(null);
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const targetOffset = circumference - (score / 100) * circumference;
  const color = COLORS[label];

  /* Animate stroke-dashoffset on mount / score change */
  useEffect(() => {
    const el = circleRef.current;
    if (!el) return;

    /* start from full offset (empty) */
    el.style.strokeDashoffset = String(circumference);
    el.style.transition = 'none';

    const raf = requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        el.style.transition =
          'stroke-dashoffset 1.4s cubic-bezier(0.16, 1, 0.3, 1)';
        el.style.strokeDashoffset = String(targetOffset);
      });
    });

    return () => cancelAnimationFrame(raf);
  }, [score, circumference, targetOffset]);

  return (
    <div
      className={cn('relative flex items-center justify-center', className)}
      style={{ width: size, height: size }}
    >
      <svg
        viewBox="0 0 200 200"
        className="absolute inset-0 -rotate-90"
        style={{ filter: `drop-shadow(0 0 8px ${color.glow})` }}
      >
        {/* Track */}
        <circle
          cx="100"
          cy="100"
          r={radius}
          fill="none"
          stroke="#27272a"
          strokeWidth="10"
        />
        {/* Progress */}
        <circle
          ref={circleRef}
          cx="100"
          cy="100"
          r={radius}
          fill="none"
          stroke={color.stroke}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={circumference}
        />
      </svg>

      {/* Centre label */}
      <div className="relative flex flex-col items-center select-none">
        <span
          className="font-mono text-4xl font-bold leading-none"
          style={{ color: color.text }}
        >
          {score}
        </span>
        <span
          className="mt-1 text-xs font-semibold uppercase tracking-widest"
          style={{ color: color.text }}
        >
          {LABELS[label]}
        </span>
      </div>
    </div>
  );
}