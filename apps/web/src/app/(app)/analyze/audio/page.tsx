'use client';

import { useState } from 'react';
import { AudioUpload } from '@/components/analyze/audio-upload';
import { ResultCard, type AnalysisResult } from '@/components/analyze/result-card';
import { ExplanationPanel } from '@/components/analyze/explanation-panel';
import { AwarenessTip } from '@/components/analyze/awareness-tip';
import { PageHeader } from '@/components/shared/page-header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Mic } from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';

/* ------------------------------------------------------------------ */
/*  Audio metadata panel                                               */
/* ------------------------------------------------------------------ */
function AudioMetadataPanel({
  meta,
}: {
  meta: NonNullable<AnalysisResult['audio_metadata']>;
}) {
  const fields = [
    { label: 'Duration', value: meta.duration_seconds != null ? `${meta.duration_seconds.toFixed(1)}s` : 'N/A' },
    { label: 'Sample Rate', value: meta.sample_rate != null ? `${(meta.sample_rate / 1000).toFixed(0)} kHz` : 'N/A' },
    { label: 'Format', value: meta.format?.toUpperCase() || 'UNKNOWN' },
  ];

  return (
    <Card className="border-zinc-800/60 bg-zinc-900/70">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold uppercase tracking-wider text-zinc-400">
          Audio Properties
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-3">
          {fields.map((f) => (
            <div
              key={f.label}
              className="rounded-lg border border-zinc-800 bg-zinc-800/40 p-3 text-center"
            >
              <p className="text-[10px] uppercase tracking-wider text-zinc-500">
                {f.label}
              </p>
              <p className="mt-1 font-mono text-sm font-semibold text-zinc-200">
                {f.value}
              </p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

/* ------------------------------------------------------------------ */
/*  Page                                                               */
/* ------------------------------------------------------------------ */
export default function AudioAnalyzerPage() {
  const [result, setResult] = useState<AnalysisResult | null>(null);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Audio Analyzer"
        description="Upload an audio clip (≤ 30s) to detect AI-generated deepfake speech."
        icon={Mic}
      />

      {/* Upload */}
      <AudioUpload
        onResult={(r) => setResult(r)}
        onReset={() => setResult(null)}
      />

      {/* Results */}
      <AnimatePresence>
        {result && (
          <motion.div
            key="audio-results"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="space-y-4"
          >
            <ResultCard result={result} />
            {result.audio_metadata && (
              <AudioMetadataPanel meta={result.audio_metadata} />
            )}
            <ExplanationPanel explanation={result.explanation} />
            <AwarenessTip tip={result.tip} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}