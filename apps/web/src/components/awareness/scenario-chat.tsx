'use client';

import { useState, useRef, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Phone,
  User,
  Shield,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ArrowRight,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */
interface ScenarioStep {
  step: number;
  role?: string;
  message?: string;
  type: 'message' | 'choice';
  prompt?: string;
  options?: string[];
  correct_index?: number;
  feedback?: Record<string, string>;
}

export interface Scenario {
  id: string;
  title: string;
  steps: ScenarioStep[];
}

/* ------------------------------------------------------------------ */
/*  Chat bubble                                                        */
/* ------------------------------------------------------------------ */
function ChatBubble({
  role,
  message,
  index,
}: {
  role: string;
  message: string;
  index: number;
}) {
  const isAttacker = role === 'caller' || role === 'attacker';

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.15, duration: 0.3 }}
      className={cn('flex gap-3', isAttacker ? 'justify-start' : 'justify-end')}
    >
      {isAttacker && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-red-500/15">
          <Phone className="h-4 w-4 text-red-400" />
        </div>
      )}

      <div
        className={cn(
          'max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed',
          isAttacker
            ? 'rounded-tl-md border border-red-500/20 bg-red-500/10 text-zinc-200'
            : 'rounded-tr-md border border-cyan-500/20 bg-cyan-500/10 text-zinc-200',
        )}
      >
        {message}
      </div>

      {!isAttacker && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-cyan-500/15">
          <User className="h-4 w-4 text-cyan-400" />
        </div>
      )}
    </motion.div>
  );
}

/* ------------------------------------------------------------------ */
/*  Feedback card                                                      */
/* ------------------------------------------------------------------ */
function FeedbackCard({
  feedback,
  isCorrect,
}: {
  feedback: string;
  isCorrect: boolean;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={cn(
        'rounded-xl border p-4 text-sm',
        isCorrect
          ? 'border-emerald-500/20 bg-emerald-500/5'
          : 'border-amber-500/20 bg-amber-500/5',
      )}
    >
      <div className="flex items-start gap-2">
        {isCorrect ? (
          <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-400" />
        ) : feedback.startsWith('⚠') ? (
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" />
        ) : (
          <XCircle className="mt-0.5 h-4 w-4 shrink-0 text-red-400" />
        )}
        <p className="text-zinc-300">{feedback}</p>
      </div>
    </motion.div>
  );
}

/* ------------------------------------------------------------------ */
/*  Props                                                              */
/* ------------------------------------------------------------------ */
interface ScenarioChatProps {
  scenario: Scenario;
  onComplete: () => void;
}

/* ------------------------------------------------------------------ */
/*  Component                                                          */
/* ------------------------------------------------------------------ */
export function ScenarioChat({ scenario, onComplete }: ScenarioChatProps) {
  const [visibleSteps, setVisibleSteps] = useState(1);
  const [choiceMade, setChoiceMade] = useState<Record<number, number>>({});
  const [feedbacks, setFeedbacks] = useState<Record<number, string>>({});
  const scrollRef = useRef<HTMLDivElement>(null);

  /* Auto-scroll to bottom */
  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: 'smooth',
    });
  }, [visibleSteps, feedbacks]);

  const steps = scenario.steps.slice(0, visibleSteps);
  const currentStep = scenario.steps[visibleSteps - 1];
  const isFinished = visibleSteps > scenario.steps.length;

  /* Handle choice selection */
  function handleChoice(stepNum: number, optIndex: number) {
    const step = scenario.steps.find((s) => s.step === stepNum);
    if (!step) return;

    setChoiceMade((prev) => ({ ...prev, [stepNum]: optIndex }));

    const fb = step.feedback?.[String(optIndex)] ?? '';
    setFeedbacks((prev) => ({ ...prev, [stepNum]: fb }));

    /* Advance after short delay */
    setTimeout(() => {
      setVisibleSteps((v) => Math.min(v + 1, scenario.steps.length + 1));
    }, 1500);
  }

  return (
    <Card className="border-zinc-800/60 bg-zinc-900/70 backdrop-blur-sm">
      <CardContent className="p-0">
        {/* Header */}
        <div className="flex items-center gap-3 border-b border-zinc-800 px-5 py-4">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-cyan-500/15">
            <Shield className="h-5 w-5 text-cyan-400" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-zinc-200">
              {scenario.title}
            </h3>
            <p className="text-xs text-zinc-500">Interactive scenario simulation</p>
          </div>
        </div>

        {/* Chat area */}
        <div
          ref={scrollRef}
          className="h-[400px] overflow-y-auto px-5 py-4 space-y-4 scrollbar-thin scrollbar-track-transparent scrollbar-thumb-zinc-800"
        >
          <AnimatePresence>
            {steps.map((step, i) => {
              if (step.type === 'message' && step.message) {
                return (
                  <ChatBubble
                    key={step.step}
                    role={step.role ?? 'system'}
                    message={step.message}
                    index={i}
                  />
                );
              }

              if (step.type === 'choice') {
                const chosen = choiceMade[step.step];
                return (
                  <motion.div
                    key={step.step}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.15 }}
                    className="space-y-3"
                  >
                    {/* Prompt */}
                    <div className="rounded-xl border border-zinc-700 bg-zinc-800/40 p-4">
                      <p className="mb-3 text-sm font-medium text-zinc-200">
                        {step.prompt}
                      </p>
                      <div className="space-y-2">
                        {step.options?.map((opt, optIdx) => (
                          <button
                            key={optIdx}
                            type="button"
                            disabled={chosen !== undefined}
                            onClick={() =>
                              handleChoice(step.step, optIdx)
                            }
                            className={cn(
                              'flex w-full items-start gap-2 rounded-lg border p-3 text-left text-sm transition-all',
                              chosen === optIdx
                                ? optIdx === step.correct_index
                                  ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300'
                                  : 'border-red-500/40 bg-red-500/10 text-red-300'
                                : chosen !== undefined
                                  ? 'border-zinc-800 opacity-40 cursor-not-allowed'
                                  : 'border-zinc-700 bg-zinc-800/30 hover:border-zinc-600 hover:bg-zinc-800/60 text-zinc-300',
                            )}
                          >
                            <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded border border-zinc-600 text-[10px] font-bold">
                              {String.fromCharCode(65 + optIdx)}
                            </span>
                            <span>{opt}</span>
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Feedback */}
                    {feedbacks[step.step] && (
                      <FeedbackCard
                        feedback={feedbacks[step.step]}
                        isCorrect={chosen === step.correct_index}
                      />
                    )}
                  </motion.div>
                );
              }

              return null;
            })}
          </AnimatePresence>

          {/* Completion */}
          {isFinished && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col items-center gap-4 py-6 text-center"
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-500/10">
                <CheckCircle2 className="h-6 w-6 text-emerald-400" />
              </div>
              <div>
                <p className="text-sm font-semibold text-zinc-200">
                  Scenario Complete!
                </p>
                <p className="mt-1 text-xs text-zinc-500">
                  You&apos;ve learned how to handle this situation safely.
                </p>
              </div>
              <Button
                onClick={onComplete}
                className="gap-1.5 bg-cyan-600 text-white hover:bg-cyan-500"
              >
                Back to Scenarios
                <ArrowRight className="h-4 w-4" />
              </Button>
            </motion.div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}