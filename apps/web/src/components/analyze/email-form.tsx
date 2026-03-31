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
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Loader2, Scan, RotateCcw } from 'lucide-react';
import { DemoSamplePicker, type DemoSample } from './demo-sample-picker';
import { toast } from 'sonner';
import { api } from '@/lib/api';
import type { AnalysisResult } from './result-card';

/* ------------------------------------------------------------------ */
/*  Schema                                                             */
/* ------------------------------------------------------------------ */
const emailSchema = z.object({
  subject: z.string().min(1, 'Subject is required').max(500, 'Subject too long'),
  body: z.string().min(1, 'Body is required').max(50000, 'Body too long'),
  sender: z.string().email('Invalid email address').or(z.literal('')).optional(),
  urls: z.string().optional(),
});

type EmailFormValues = z.infer<typeof emailSchema>;

/* ------------------------------------------------------------------ */
/*  Props                                                              */
/* ------------------------------------------------------------------ */
interface EmailFormProps {
  onResult: (result: AnalysisResult) => void;
  onReset: () => void;
}

/* ------------------------------------------------------------------ */
/*  Component                                                          */
/* ------------------------------------------------------------------ */
export function EmailForm({ onResult, onReset }: EmailFormProps) {
  const [isLoading, setIsLoading] = useState(false);

  const form = useForm<EmailFormValues>({
    resolver: zodResolver(emailSchema),
    defaultValues: { subject: '', body: '', sender: '', urls: '' },
  });

  /* Demo sample fill */
  function handleDemoSelect(sample: DemoSample) {
    const d = sample.data as any;
    if (!d) return;
    form.setValue('subject', d.subject ?? '');
    form.setValue('body', d.body ?? '');
    form.setValue('sender', d.sender ?? '');
    form.setValue('urls', (d.urls ?? []).join('\n'));
    toast.info(`Demo loaded: "${sample.title}"`);
  }

  /* Submit */
  async function onSubmit(values: EmailFormValues) {
    setIsLoading(true);
    try {
      const urls = values.urls
        ? values.urls
            .split(/[\n,]+/)
            .map((u) => u.trim())
            .filter(Boolean)
        : [];

      const result = await api.analyzeEmail({
        subject: values.subject,
        body: values.body,
        sender: values.sender ?? '',
        urls,
      });

      onResult(result as AnalysisResult);
    } catch (err: any) {
      toast.error(err?.message ?? 'Analysis failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }

  /* Reset */
  function handleReset() {
    form.reset();
    onReset();
  }

  return (
    <Card className="border-zinc-800/60 bg-zinc-900/70 backdrop-blur-sm overflow-hidden">
      <CardContent className="p-5">
        {/* ── Header row ── */}
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-zinc-400">
            Email Details
          </h3>
          <div className="flex items-center gap-2">
            <DemoSamplePicker filterType="email" onSelect={handleDemoSelect} />
            <Button
              variant="ghost"
              size="sm"
              onClick={handleReset}
              className="h-7 gap-1.5 text-xs text-zinc-500 hover:text-zinc-300"
            >
              <RotateCcw className="h-3 w-3" />
              Reset
            </Button>
          </div>
        </div>

        {/* ── Form ── */}
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-3">
            {/* Subject + Sender — side by side */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <FormField
                control={form.control}
                name="subject"
                render={({ field }) => (
                  <FormItem className="space-y-1">
                    <FormLabel className="text-xs text-zinc-400">
                      Subject *
                    </FormLabel>
                    <FormControl>
                      <Input
                        {...field}
                        placeholder="e.g. URGENT: Account suspended"
                        className="h-9 border-zinc-700 bg-zinc-800/60 text-sm text-zinc-200
                                   placeholder:text-zinc-600 focus-visible:ring-cyan-500/50"
                        data-testid="email-subject"
                      />
                    </FormControl>
                    <FormMessage className="text-xs" />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="sender"
                render={({ field }) => (
                  <FormItem className="space-y-1">
                    <FormLabel className="text-xs text-zinc-400">
                      Sender Email
                    </FormLabel>
                    <FormControl>
                      <Input
                        {...field}
                        placeholder="e.g. security@sbi-alerts.xyz"
                        className="h-9 border-zinc-700 bg-zinc-800/60 text-sm text-zinc-200
                                   placeholder:text-zinc-600 focus-visible:ring-cyan-500/50"
                        data-testid="email-sender"
                      />
                    </FormControl>
                    <FormMessage className="text-xs" />
                  </FormItem>
                )}
              />
            </div>

            {/* Body + URLs — side by side on larger screens, stacked on small */}
            <div className="grid grid-cols-1 lg:grid-cols-[1fr_0.45fr] gap-3">
              <FormField
                control={form.control}
                name="body"
                render={({ field }) => (
                  <FormItem className="space-y-1">
                    <FormLabel className="text-xs text-zinc-400">
                      Email Body *
                    </FormLabel>
                    <FormControl>
                      <Textarea
                        {...field}
                        rows={5}
                        placeholder="Paste the full email body here…"
                        className="resize-none border-zinc-700 bg-zinc-800/60 text-sm text-zinc-200
                                   placeholder:text-zinc-600 focus-visible:ring-cyan-500/50
                                   min-h-[120px]"
                        data-testid="email-body"
                      />
                    </FormControl>
                    <FormMessage className="text-xs" />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="urls"
                render={({ field }) => (
                  <FormItem className="space-y-1">
                    <FormLabel className="text-xs text-zinc-400">
                      URLs
                      <span className="text-zinc-600 ml-1 font-normal">
                        (one per line)
                      </span>
                    </FormLabel>
                    <FormControl>
                      <Textarea
                        {...field}
                        rows={5}
                        placeholder={"https://example.com/link1\nhttps://example.com/link2"}
                        className="resize-none border-zinc-700 bg-zinc-800/60 font-mono text-xs
                                   text-zinc-200 placeholder:text-zinc-600
                                   focus-visible:ring-cyan-500/50 min-h-[120px]"
                        data-testid="email-urls"
                      />
                    </FormControl>
                    <FormMessage className="text-xs" />
                  </FormItem>
                )}
              />
            </div>

            {/* Submit */}
            <Button
              type="submit"
              disabled={isLoading}
              className="w-full h-11 gap-2 font-semibold text-sm tracking-wide
                         bg-gradient-to-r from-cyan-600 to-blue-600
                         hover:from-cyan-500 hover:to-blue-500
                         text-white shadow-lg shadow-cyan-500/20
                         transition-all duration-300"
              data-testid="analyze-button"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Analyzing…
                </>
              ) : (
                <>
                  <Scan className="h-4 w-4" />
                  Analyze Email
                </>
              )}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}