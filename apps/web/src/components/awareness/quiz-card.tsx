'use client';

import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';
import type { QuizQuestion } from '@/hooks/use-quiz';

/* ------------------------------------------------------------------ */
/*  Props                                                              */
/* ------------------------------------------------------------------ */
interface QuizCardProps {
  question: QuizQuestion;
  questionNumber: number;
  selectedIndex: number | null;
  onAnswer: (index: number) => void;
  disabled?: boolean;
}

/* ------------------------------------------------------------------ */
/*  Option labels                                                      */
/* ------------------------------------------------------------------ */
const OPTION_LETTERS = ['A', 'B', 'C', 'D'];

/* ------------------------------------------------------------------ */
/*  Difficulty indicator                                               */
/* ------------------------------------------------------------------ */
function DifficultyDots({ level }: { level: number }) {
  return (
    <div className="flex items-center gap-1" title={`Difficulty: ${level}/3`}>
      {[1, 2, 3].map((d) => (
        <div
          key={d}
          className={cn(
            'h-1.5 w-1.5 rounded-full',
            d <= level ? 'bg-cyan-400' : 'bg-zinc-700',
          )}
        />
      ))}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Component                                                          */
/* ------------------------------------------------------------------ */
export function QuizCard({
  question,
  questionNumber,
  selectedIndex,
  onAnswer,
  disabled = false,
}: QuizCardProps) {
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={question.id}
        initial={{ opacity: 0, x: 30 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -30 }}
        transition={{ duration: 0.3 }}
      >
        <Card className="border-zinc-800/60 bg-zinc-900/70 backdrop-blur-sm">
          <CardContent className="p-6 space-y-5">
            {/* Header */}
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-center gap-2">
                <span className="flex h-7 w-7 items-center justify-center rounded-md bg-cyan-500/15 font-mono text-xs font-bold text-cyan-400">
                  {questionNumber}
                </span>
                <DifficultyDots level={question.difficulty} />
              </div>
            </div>

            {/* Question text */}
            <p className="text-base font-medium leading-relaxed text-zinc-200">
              {question.question_text}
            </p>

            {/* Options */}
            <div className="space-y-2.5">
              {question.options.map((option, i) => {
                const isSelected = selectedIndex === i;
                return (
                  <button
                    key={i}
                    type="button"
                    disabled={disabled || selectedIndex !== null}
                    onClick={() => onAnswer(i)}
                    className={cn(
                      'group flex w-full items-start gap-3 rounded-xl border p-4 text-left transition-all duration-200',
                      isSelected
                        ? 'border-cyan-500/50 bg-cyan-500/10'
                        : 'border-zinc-800 bg-zinc-800/30 hover:border-zinc-700 hover:bg-zinc-800/60',
                      (disabled || selectedIndex !== null) &&
                        !isSelected &&
                        'opacity-50 cursor-not-allowed',
                    )}
                  >
                    <span
                      className={cn(
                        'flex h-7 w-7 shrink-0 items-center justify-center rounded-lg border text-xs font-bold transition-colors',
                        isSelected
                          ? 'border-cyan-500 bg-cyan-500 text-white'
                          : 'border-zinc-700 bg-zinc-800 text-zinc-500 group-hover:border-zinc-600 group-hover:text-zinc-400',
                      )}
                    >
                      {OPTION_LETTERS[i]}
                    </span>
                    <span
                      className={cn(
                        'pt-0.5 text-sm',
                        isSelected ? 'text-cyan-200' : 'text-zinc-300',
                      )}
                    >
                      {option}
                    </span>
                  </button>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </AnimatePresence>
  );
}