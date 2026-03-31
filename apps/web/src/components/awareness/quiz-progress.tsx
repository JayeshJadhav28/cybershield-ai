'use client';

import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

interface QuizProgressProps {
  current: number;
  total: number;
  progress: number; // 0-100
  className?: string;
}

export function QuizProgress({
  current,
  total,
  progress,
  className,
}: QuizProgressProps) {
  return (
    <div className={cn('space-y-2', className)}>
      <div className="flex items-center justify-between text-xs">
        <span className="font-medium text-zinc-400">
          Question{' '}
          <span className="font-mono text-zinc-200">
            {current + 1}
          </span>{' '}
          of{' '}
          <span className="font-mono text-zinc-200">{total}</span>
        </span>
        <span className="font-mono text-zinc-500">{progress}%</span>
      </div>
      <Progress
        value={progress}
        className="h-1.5 bg-zinc-800"
      />
    </div>
  );
}