'use client';

import { useState, useCallback } from 'react';
import { api } from '@/lib/api';

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */
export interface QuizQuestion {
  id: string;
  question_text: string;
  options: string[];
  difficulty: number;
}

export interface QuizAnswerResult {
  question_id: string;
  selected_option_index: number;
  correct_option_index: number;
  is_correct: boolean;
  explanation: string;
}

export interface QuizSessionResult {
  session_id: string;
  category: string;
  total_questions: number;
  correct_count: number;
  score_pct: number;
  badge_earned: string | null;
  results: QuizAnswerResult[];
}

export type QuizPhase = 'idle' | 'loading' | 'active' | 'submitting' | 'results';

interface QuizAnswer {
  question_id: string;
  selected_option_index: number;
}

/* ------------------------------------------------------------------ */
/*  Hook                                                               */
/* ------------------------------------------------------------------ */
export function useQuiz() {
  const [phase, setPhase] = useState<QuizPhase>('idle');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [category, setCategory] = useState<string>('');
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<QuizAnswer[]>([]);
  const [result, setResult] = useState<QuizSessionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  /* Start a new session */
  const startSession = useCallback(async (cat: string) => {
    setPhase('loading');
    setError(null);
    setCategory(cat);
    setAnswers([]);
    setCurrentIndex(0);
    setResult(null);

    try {
      const res: any = await api.startQuizSession(cat);
      setSessionId(res.session_id);
      setQuestions(res.questions ?? []);
      setPhase('active');
    } catch (err: any) {
      setError(err?.message ?? 'Failed to start quiz session');
      setPhase('idle');
    }
  }, []);

  /* Record an answer for the current question */
  const answerQuestion = useCallback(
    (optionIndex: number) => {
      const q = questions[currentIndex];
      if (!q) return;

      setAnswers((prev) => [
        ...prev,
        { question_id: q.id, selected_option_index: optionIndex },
      ]);

      if (currentIndex < questions.length - 1) {
        setCurrentIndex((i) => i + 1);
      }
    },
    [currentIndex, questions],
  );

  /* Submit all answers */
  const submitAnswers = useCallback(async () => {
    if (!sessionId) return;
    setPhase('submitting');
    setError(null);

    try {
      const res: any = await api.submitQuizAnswers(sessionId, answers);
      setResult(res as QuizSessionResult);
      setPhase('results');
    } catch (err: any) {
      setError(err?.message ?? 'Failed to submit answers');
      setPhase('active');
    }
  }, [sessionId, answers]);

  /* Go to previous question */
  const prevQuestion = useCallback(() => {
    setCurrentIndex((i) => Math.max(0, i - 1));
  }, []);

  /* Reset everything */
  const resetQuiz = useCallback(() => {
    setPhase('idle');
    setSessionId(null);
    setCategory('');
    setQuestions([]);
    setCurrentIndex(0);
    setAnswers([]);
    setResult(null);
    setError(null);
  }, []);

  /* Derived state */
  const currentQuestion = questions[currentIndex] ?? null;
  const isLastQuestion = currentIndex === questions.length - 1;
  const hasAnsweredCurrent = answers.some(
    (a) => a.question_id === currentQuestion?.id,
  );
  const allAnswered = answers.length === questions.length && questions.length > 0;
  const progress =
    questions.length > 0 ? Math.round((answers.length / questions.length) * 100) : 0;

  return {
    phase,
    category,
    questions,
    currentIndex,
    currentQuestion,
    answers,
    result,
    error,
    progress,
    isLastQuestion,
    hasAnsweredCurrent,
    allAnswered,
    startSession,
    answerQuestion,
    submitAnswers,
    prevQuestion,
    setCurrentIndex,
    resetQuiz,
  };
}