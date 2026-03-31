import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface LoadingSpinnerProps {
  label?: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export function LoadingSpinner({
  label,
  className,
  size = 'md',
}: LoadingSpinnerProps) {
  return (
    <div className={cn('flex flex-col items-center gap-3', className)}>
      <Loader2
        className={cn(
          'animate-spin text-cyan-400',
          size === 'sm' && 'h-5 w-5',
          size === 'md' && 'h-8 w-8',
          size === 'lg' && 'h-12 w-12',
        )}
      />
      {label && (
        <p className="text-sm font-medium text-zinc-400">{label}</p>
      )}
    </div>
  );
}