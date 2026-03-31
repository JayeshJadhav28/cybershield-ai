'use client';

import { useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useQuiz } from '@/hooks/use-quiz';
import { QuizCard } from '@/components/awareness/quiz-card';
import { QuizProgress } from '@/components/awareness/quiz-progress';
import { QuizResult } from '@/components/awareness/quiz-result';
import { PageHeader } from '@/components/shared/page-header';
import { Button } from '@/components/ui/button';
import { LoadingSpinner } from '@/components/shared/loading-spinner';
import {
  GraduationCap,
  ArrowLeft,
  ArrowRight,
  Send,
} from 'lucide-react';

const CATEGORY_TITLES: Record<string, string> = {
  deepfake: 'Deepfake Detection',
  upi_qr: 'UPI & QR Scams',
  phishing: 'KYC & OTP Phishing',
};

export default function ActiveQuizPage() {
  const params = useParams();
  const router = useRouter();
  const category = params.category as string;

  const {
    phase,
    currentIndex,
    currentQuestion,
    questions,
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
  } = useQuiz();

  /* Start session on mount */
  useEffect(() => {
    if (category) {
      startSession(category);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [category]);

  /* Loading */
  if (phase === 'loading') {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <LoadingSpinner label="Loading quiz…" />
      </div>
    );
  }

  /* Error */
  if (error) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Quiz Error"
          description={error}
          icon={GraduationCap}
        />
        <Button
          variant="outline"
          onClick={() => router.push('/awareness/quizzes')}
          className="gap-1.5"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Quizzes
        </Button>
      </div>
    );
  }

  /* Results */
  if (phase === 'results' && result) {
    return (
      <div className="space-y-6">
        <PageHeader
          title={CATEGORY_TITLES[category] ?? 'Quiz Results'}
          icon={GraduationCap}
        />
        <QuizResult
          result={result}
          onRetry={() => startSession(category)}
        />
      </div>
    );
  }

  /* Active quiz */
  if (phase === 'active' && currentQuestion) {
    const selectedAnswer = answers.find(
      (a) => a.question_id === currentQuestion.id,
    );
    const selectedIndex = selectedAnswer
      ? selectedAnswer.selected_option_index
      : null;

    return (
      <div className="space-y-6">
        <PageHeader
          title={CATEGORY_TITLES[category] ?? 'Quiz'}
          icon={GraduationCap}
        />

        <QuizProgress
          current={currentIndex}
          total={questions.length}
          progress={progress}
        />

        <QuizCard
          question={currentQuestion}
          questionNumber={currentIndex + 1}
          selectedIndex={selectedIndex}
          onAnswer={answerQuestion}
        />

        {/* Navigation */}
        <div className="flex items-center justify-between">
          <Button
            variant="ghost"
            size="sm"
            onClick={prevQuestion}
            disabled={currentIndex === 0}
            className="gap-1.5 text-zinc-400 hover:text-zinc-200"
          >
            <ArrowLeft className="h-4 w-4" />
            Previous
          </Button>

          {isLastQuestion && allAnswered ? (
            <Button
              onClick={submitAnswers}
              className="gap-1.5 bg-cyan-600 text-white hover:bg-cyan-500"
            >
              <Send className="h-4 w-4" />
              Submit Answers
            </Button>
          ) : (
            <Button
              variant="ghost"
              size="sm"
              onClick={() =>
                setCurrentIndex(
                  Math.min(currentIndex + 1, questions.length - 1),
                )
              }
              disabled={!hasAnsweredCurrent || isLastQuestion}
              className="gap-1.5 text-zinc-400 hover:text-zinc-200"
            >
              Next
              <ArrowRight className="h-4 w-4" />
            </Button>
          )}
        </div>

        {/* Question dots navigation */}
        <div className="flex justify-center gap-1.5">
          {questions.map((q, i) => {
            const answered = answers.some((a) => a.question_id === q.id);
            return (
              <button
                key={q.id}
                type="button"
                onClick={() => setCurrentIndex(i)}
                className={`h-2 w-2 rounded-full transition-all ${
                  i === currentIndex
                    ? 'scale-125 bg-cyan-400'
                    : answered
                      ? 'bg-cyan-600'
                      : 'bg-zinc-700'
                }`}
                title={`Question ${i + 1}`}
              />
            );
          })}
        </div>
      </div>
    );
  }

  /* Submitting */
  if (phase === 'submitting') {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <LoadingSpinner label="Submitting answers…" />
      </div>
    );
  }

  return null;
}