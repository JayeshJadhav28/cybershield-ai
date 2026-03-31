import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { SearchX, ArrowRight } from 'lucide-react';
import { cn } from '@/lib/utils';

interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: React.ElementType;
  action?: { label: string; href: string };
  className?: string;
}

export function EmptyState({
  title,
  description,
  icon: Icon = SearchX,
  action,
  className,
}: EmptyStateProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center py-16 text-center', className)}>
      <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-zinc-800/80">
        <Icon className="h-8 w-8 text-zinc-500" />
      </div>
      <h3 className="text-base font-semibold text-zinc-300">{title}</h3>
      {description && (
        <p className="mt-1 max-w-sm text-sm text-zinc-500">{description}</p>
      )}
      {action && (
        <Link href={action.href} className="mt-4">
          <Button variant="outline" size="sm" className="gap-1.5 border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10">
            {action.label}
            <ArrowRight className="h-3.5 w-3.5" />
          </Button>
        </Link>
      )}
    </div>
  );
}