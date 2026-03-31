'use client';

import { useState } from 'react';
import { EmailForm } from '@/components/analyze/email-form';
import { ResultCard, type AnalysisResult } from '@/components/analyze/result-card';
import { ExplanationPanel } from '@/components/analyze/explanation-panel';
import { AwarenessTip } from '@/components/analyze/awareness-tip';
import { HighlightText } from '@/components/analyze/highlight-text';
import { Mail } from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';

export default function EmailAnalyzerPage() {
  const [result, setResult] = useState<AnalysisResult | null>(null);

  const phrases = result?.explanation?.highlights?.phrases ?? [];

  return (
    <div className="space-y-5">
      {/* ── Page Header (compact, matches other analyzers) ── */}
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-cyan-500/10 border border-cyan-500/20">
          <Mail className="h-5 w-5 text-cyan-400" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-zinc-100">Email Analyzer</h1>
          <p className="text-zinc-400 text-sm mt-0.5">
            Paste email details to detect phishing attempts and suspicious content.
          </p>
        </div>
      </div>

      {/* Input form */}
      <EmailForm
        onResult={(r) => setResult(r)}
        onReset={() => setResult(null)}
      />

      {/* Results */}
      <AnimatePresence>
        {result && (
          <motion.div
            key="results"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="space-y-4"
          >
            <ResultCard result={result} />

            {phrases.length > 0 && (
              <div className="rounded-xl border border-zinc-800/60 bg-zinc-900/60 p-5">
                <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-zinc-400">
                  Highlighted Body
                </p>
                <div className="text-sm leading-relaxed text-zinc-300">
                  <HighlightText
                    text={result.explanation.summary}
                    phrases={phrases}
                  />
                </div>
              </div>
            )}

            <ExplanationPanel explanation={result.explanation} />
            <AwarenessTip tip={result.tip} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}