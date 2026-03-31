'use client';

import { useState } from 'react';
import { UrlForm } from '@/components/analyze/url-form';
import { QrUpload } from '@/components/analyze/qr-upload';
import { ResultCard, type AnalysisResult } from '@/components/analyze/result-card';
import { ExplanationPanel } from '@/components/analyze/explanation-panel';
import { AwarenessTip } from '@/components/analyze/awareness-tip';
import { PageHeader } from '@/components/shared/page-header';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Link2, QrCode } from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';
import { cn } from '@/lib/utils';

/* ------------------------------------------------------------------ */
/*  Tab definitions                                                    */
/* ------------------------------------------------------------------ */
const TABS = [
  {
    key: 'url' as const,
    label: 'URL',
    icon: Link2,
    activeText: 'text-cyan-400',
    activeBg: 'bg-cyan-500/10',
    activeBorder: 'border-cyan-500/30',
    activeGlow: 'shadow-cyan-500/10',
  },
  {
    key: 'qr' as const,
    label: 'QR Code',
    icon: QrCode,
    activeText: 'text-indigo-400',
    activeBg: 'bg-indigo-500/10',
    activeBorder: 'border-indigo-500/30',
    activeGlow: 'shadow-indigo-500/10',
  },
] as const;

type TabKey = (typeof TABS)[number]['key'];

/* ------------------------------------------------------------------ */
/*  Decoded QR payload panel                                           */
/* ------------------------------------------------------------------ */
function DecodedPayload({ decoded }: { decoded: AnalysisResult['decoded'] }) {
  if (!decoded) return null;
  return (
    <Card className="border-zinc-800/60 bg-zinc-900/70">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-zinc-400">
          Decoded QR Content
          <Badge
            variant="outline"
            className="border-cyan-500/30 bg-cyan-500/10 text-[10px] font-bold text-cyan-400"
          >
            {decoded.type?.toUpperCase()}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Raw payload */}
        <div className="rounded-lg border border-zinc-800 bg-zinc-950/60 p-3">
          <p className="mb-1 text-[10px] uppercase tracking-wider text-zinc-500">
            Raw
          </p>
          <p className="break-all font-mono text-xs text-zinc-300">
            {decoded.raw}
          </p>
        </div>

        {/* Parsed fields */}
        {decoded.parsed && Object.keys(decoded.parsed).length > 0 && (
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
            {Object.entries(decoded.parsed).map(([k, v]) => (
              <div
                key={k}
                className="rounded-lg border border-zinc-800 bg-zinc-800/40 p-2.5"
              >
                <p className="text-[10px] uppercase tracking-wider text-zinc-500">
                  {k}
                </p>
                <p className="mt-0.5 truncate font-mono text-xs font-medium text-zinc-200">
                  {v}
                </p>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

/* ------------------------------------------------------------------ */
/*  Page                                                               */
/* ------------------------------------------------------------------ */
export default function UrlAnalyzerPage() {
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [activeTab, setActiveTab] = useState<TabKey>('url');

  function handleReset() {
    setResult(null);
  }

  function switchTab(key: TabKey) {
    if (key !== activeTab) {
      setActiveTab(key);
      handleReset();
    }
  }

  const currentTab = TABS.find((t) => t.key === activeTab)!;

  return (
    <div className="space-y-6">
      <PageHeader
        title="URL & QR Analyzer"
        description="Check if a URL is malicious or decode and verify a QR code."
        icon={Link2}
      />

      {/* ── Segmented Toggle ── */}
      <div className="flex items-center">
        <div className="inline-flex items-center gap-1 rounded-xl border border-zinc-800 bg-zinc-900/80 p-1 backdrop-blur-sm">
          {TABS.map((tab) => {
            const isActive = activeTab === tab.key;
            const Icon = tab.icon;
            return (
              <button
                key={tab.key}
                type="button"
                onClick={() => switchTab(tab.key)}
                className={cn(
                  'relative flex items-center gap-2 rounded-lg px-5 py-2.5 text-sm font-medium transition-all duration-200',
                  isActive
                    ? [
                        'bg-zinc-800 shadow-lg',
                        tab.activeText,
                        tab.activeGlow,
                      ]
                    : 'text-zinc-500 hover:bg-zinc-800/50 hover:text-zinc-300',
                )}
              >
                {/* Active indicator dot */}
                {isActive && (
                  <motion.span
                    layoutId="tab-dot"
                    className={cn(
                      'absolute -top-0.5 left-1/2 h-0.5 w-6 -translate-x-1/2 rounded-full',
                      activeTab === 'url' ? 'bg-cyan-400' : 'bg-indigo-400',
                    )}
                    transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                  />
                )}
                <Icon className="h-4 w-4" />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* ── Tab Content ── */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.2 }}
        >
          {activeTab === 'url' ? (
            <UrlForm onResult={setResult} onReset={handleReset} />
          ) : (
            <QrUpload onResult={setResult} onReset={handleReset} />
          )}
        </motion.div>
      </AnimatePresence>

      {/* ── Results ── */}
      <AnimatePresence>
        {result && (
          <motion.div
            key="results"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 12 }}
            transition={{ duration: 0.25 }}
            className="space-y-4"
          >
            {result.decoded && <DecodedPayload decoded={result.decoded} />}
            <ResultCard result={result} />
            <ExplanationPanel explanation={result.explanation} />
            <AwarenessTip tip={result.tip} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}