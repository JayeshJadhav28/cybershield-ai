'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, Scan, RotateCcw, Link2 } from 'lucide-react';
import { DemoSamplePicker, type DemoSample } from './demo-sample-picker';
import { toast } from 'sonner';
import { api } from '@/lib/api';
import type { AnalysisResult } from './result-card';

/* ── Schema ── */
const urlSchema = z.object({
  url: z
    .string()
    .min(1, 'URL is required')
    .max(2048, 'URL is too long')
    .refine(
      (v) => {
        try {
          new URL(v.startsWith('http') ? v : `https://${v}`);
          return true;
        } catch {
          return false;
        }
      },
      { message: 'Please enter a valid URL' },
    ),
});

type UrlFormValues = z.infer<typeof urlSchema>;

/* ── Props ── */
interface UrlFormProps {
  onResult: (result: AnalysisResult) => void;
  onReset: () => void;
}

/* ── Component ── */
export function UrlForm({ onResult, onReset }: UrlFormProps) {
  const [isLoading, setIsLoading] = useState(false);

  const form = useForm<UrlFormValues>({
    resolver: zodResolver(urlSchema),
    defaultValues: { url: '' },
  });

  function handleDemoSelect(sample: DemoSample) {
    const d = sample.data as any;
    if (d?.url) {
      form.setValue('url', d.url);
      toast.info(`Demo loaded: "${sample.title}"`);
    }
  }

  async function onSubmit(values: UrlFormValues) {
    setIsLoading(true);
    try {
      const normalised = values.url.startsWith('http')
        ? values.url
        : `https://${values.url}`;
      const result = await api.analyzeUrl(normalised);
      onResult(result as AnalysisResult);
    } catch (err: any) {
      toast.error(err?.message ?? 'Analysis failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <Card className="border-zinc-800/60 bg-zinc-900/70 backdrop-blur-sm">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-zinc-400">
            <Link2 className="h-4 w-4 text-cyan-500" />
            URL to Analyze
          </CardTitle>
          <div className="flex items-center gap-2">
            <DemoSamplePicker filterType="url" onSelect={handleDemoSelect} />
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                form.reset();
                onReset();
              }}
              className="h-7 gap-1.5 text-xs text-zinc-500 hover:text-zinc-300"
            >
              <RotateCcw className="h-3 w-3" />
              Reset
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="url"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-xs text-zinc-400">
                    URL <span className="text-red-400">*</span>
                  </FormLabel>
                  <FormControl>
                    <Input
                      {...field}
                      placeholder="https://example.com/suspicious-link"
                      className="border-zinc-700 bg-zinc-800/60 font-mono text-sm text-zinc-200 placeholder:text-zinc-600 focus-visible:ring-cyan-500/50"
                      data-testid="url-input"
                    />
                  </FormControl>
                  <FormMessage className="text-xs" />
                </FormItem>
              )}
            />

            <Button
              type="submit"
              disabled={isLoading}
              className="w-full gap-2 bg-cyan-600 text-white hover:bg-cyan-500 disabled:opacity-50"
              data-testid="analyze-button"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Checking URL…
                </>
              ) : (
                <>
                  <Scan className="h-4 w-4" />
                  Analyze URL
                </>
              )}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}