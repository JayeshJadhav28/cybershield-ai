'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ExternalLink } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ResourceCardProps {
  title: string;
  description: string;
  category: string;
  icon: React.ElementType;
  iconColor: string;
  href?: string;
  tags?: string[];
}

export function ResourceCard({
  title,
  description,
  category,
  icon: Icon,
  iconColor,
  href,
  tags = [],
}: ResourceCardProps) {
  const isExternal = href?.startsWith('http') || href?.startsWith('tel:');
  const Wrapper = href ? 'a' : 'div';
  const wrapperProps = href
    ? isExternal
      ? { href, target: '_blank', rel: 'noopener noreferrer' }
      : { href }
    : {};

  return (
    <Wrapper {...(wrapperProps as any)} className="block h-full">
      <Card
        className={cn(
          'group relative h-full overflow-hidden',
          'border-zinc-800/60 bg-zinc-900/70 backdrop-blur-sm',
          'transition-all duration-300',
          // All cards get hover effect — whether they have href or not
          'hover:border-zinc-700 hover:bg-zinc-800/80',
          'hover:shadow-lg hover:shadow-black/20',
          href && 'cursor-pointer',
        )}
      >
        {/* Hover gradient overlay */}
        <div
          className={cn(
            'pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-300',
            'group-hover:opacity-100',
            'bg-gradient-to-br from-white/[0.02] via-transparent to-transparent',
          )}
        />

        <CardContent className="relative flex h-full flex-col p-5">
          {/* Top row: icon + external link */}
          <div className="flex items-start justify-between">
            <div
              className={cn(
                'flex h-10 w-10 items-center justify-center rounded-xl',
                'bg-zinc-800/80 border border-zinc-700/50',
                'transition-all duration-300',
                'group-hover:border-zinc-600/50 group-hover:scale-105',
              )}
            >
              <Icon className={cn('h-5 w-5', iconColor)} />
            </div>

            {/* External link icon — show for ALL cards with href */}
            {href && (
              <div
                className={cn(
                  'flex h-7 w-7 items-center justify-center rounded-md',
                  'transition-all duration-300',
                  'opacity-40 group-hover:opacity-100',
                  'group-hover:bg-zinc-800/60',
                )}
              >
                <ExternalLink className="h-3.5 w-3.5 text-zinc-500 transition-colors group-hover:text-zinc-300" />
              </div>
            )}
          </div>

          {/* Content */}
          <div className="mt-3 flex-1">
            <Badge
              variant="outline"
              className="mb-2 border-zinc-700/60 text-[10px] text-zinc-500"
            >
              {category}
            </Badge>
            <h3 className="text-sm font-semibold text-zinc-200 transition-colors group-hover:text-white">
              {title}
            </h3>
            <p className="mt-1.5 text-xs leading-relaxed text-zinc-500 transition-colors group-hover:text-zinc-400">
              {description}
            </p>
          </div>

          {/* Tags */}
          {tags.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1">
              {tags.map((t) => (
                <span
                  key={t}
                  className={cn(
                    'rounded-md px-1.5 py-0.5 text-[10px] font-medium',
                    'bg-zinc-800/80 text-zinc-500 border border-zinc-700/30',
                    'transition-colors group-hover:text-zinc-400 group-hover:border-zinc-700/50',
                  )}
                >
                  {t}
                </span>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </Wrapper>
  );
}