'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { FlaskConical, ChevronDown, Loader2 } from 'lucide-react';
import { api } from '@/lib/api';

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */
export interface DemoSample {
  id: string;
  type: string;
  title: string;
  expected_label: string;
  data?: Record<string, unknown>;
  file_url?: string;
}

interface DemoSamplePickerProps {
  filterType: 'email' | 'url' | 'qr' | 'audio' | 'video';
  onSelect: (sample: DemoSample) => void;
}

/* ------------------------------------------------------------------ */
/*  Component                                                          */
/* ------------------------------------------------------------------ */
export function DemoSamplePicker({
  filterType,
  onSelect,
}: DemoSamplePickerProps) {
  const [samples, setSamples] = useState<DemoSample[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    api
      .getDemoSamples()
      .then((res: any) => {
        if (!cancelled) {
          const filtered = (res.samples ?? []).filter(
            (s: DemoSample) => s.type === filterType,
          );
          setSamples(filtered);
        }
      })
      .catch(() => {
        /* API not running — show nothing */
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [filterType]);

  if (samples.length === 0 && !loading) return null;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className="gap-1.5 border-zinc-700 text-xs text-zinc-400 hover:border-zinc-600 hover:text-zinc-200"
          data-testid="demo-sample-picker"
          disabled={loading}
        >
          {loading ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <FlaskConical className="h-3.5 w-3.5" />
          )}
          Demo Sample
          <ChevronDown className="h-3 w-3" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        align="start"
        className="border-zinc-800 bg-zinc-900"
      >
        <DropdownMenuLabel className="text-xs text-zinc-500">
          Pre-loaded Samples
        </DropdownMenuLabel>
        <DropdownMenuSeparator className="bg-zinc-800" />
        {samples.map((s) => (
          <DropdownMenuItem
            key={s.id}
            onClick={() => onSelect(s)}
            className="cursor-pointer text-sm text-zinc-300 focus:bg-zinc-800 focus:text-zinc-100"
          >
            <span
              className={
                s.expected_label === 'dangerous'
                  ? 'mr-2 text-red-400'
                  : s.expected_label === 'suspicious'
                    ? 'mr-2 text-amber-400'
                    : 'mr-2 text-emerald-400'
              }
            >
              {s.expected_label === 'dangerous'
                ? '🔴'
                : s.expected_label === 'suspicious'
                  ? '🟡'
                  : '🟢'}
            </span>
            {s.title}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}