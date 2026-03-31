"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  RotateCcw,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { getScenarioById } from "@/lib/scenarios-data";
import type { ScenarioStep } from "@/lib/scenarios-data";

export default function ScenarioDetailPage() {
  const params = useParams();
  const router = useRouter();
  const scenario = getScenarioById(params.id as string);

  const [currentStep, setCurrentStep] = useState(0);
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [score, setScore] = useState(0);
  const [totalChoices, setTotalChoices] = useState(0);
  const [completed, setCompleted] = useState(false);

  if (!scenario) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-4">
        <XCircle className="h-12 w-12 text-red-400" />
        <h2 className="text-lg font-semibold text-zinc-200">
          Scenario not found
        </h2>
        <p className="text-sm text-zinc-400">
          The scenario you&apos;re looking for doesn&apos;t exist.
        </p>
        <Button
          variant="outline"
          onClick={() => router.push("/awareness/scenarios")}
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Scenarios
        </Button>
      </div>
    );
  }

  const step = scenario.steps[currentStep];
  const progress = ((currentStep + 1) / scenario.steps.length) * 100;

  const handleSelectOption = (index: number) => {
    if (showFeedback) return;
    setSelectedOption(index);
    setShowFeedback(true);
    setTotalChoices((prev) => prev + 1);
    if (index === step.correct_index) {
      setScore((prev) => prev + 1);
    }
  };

  const handleNext = () => {
    if (currentStep < scenario.steps.length - 1) {
      setCurrentStep((prev) => prev + 1);
      setSelectedOption(null);
      setShowFeedback(false);
    } else {
      setCompleted(true);
    }
  };

  const handleRestart = () => {
    setCurrentStep(0);
    setSelectedOption(null);
    setShowFeedback(false);
    setScore(0);
    setTotalChoices(0);
    setCompleted(false);
  };

  const canProceed =
    step.type === "message" || (step.type === "choice" && showFeedback);

  // ── Completed screen ──
  if (completed) {
    const percentage = totalChoices > 0 ? Math.round((score / totalChoices) * 100) : 100;

    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <button
          onClick={() => router.push("/awareness/scenarios")}
          className="flex items-center gap-1.5 text-xs text-zinc-500 hover:text-zinc-300 transition-colors"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          All Scenarios
        </button>

        <div className="flex flex-col items-center text-center space-y-6 py-12">
          <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-cyan-500/10 border border-cyan-500/20">
            <CheckCircle2 className="h-10 w-10 text-cyan-400" />
          </div>

          <div>
            <h2 className="text-2xl font-bold text-zinc-100 mb-2">
              Scenario Complete!
            </h2>
            <p className="text-zinc-400">{scenario.title}</p>
          </div>

          <div className="flex items-center gap-6 py-4">
            <div className="text-center">
              <p className="text-3xl font-bold text-cyan-400">{percentage}%</p>
              <p className="text-xs text-zinc-500 mt-1">Score</p>
            </div>
            <div className="h-12 w-px bg-zinc-800" />
            <div className="text-center">
              <p className="text-3xl font-bold text-zinc-200">
                {score}/{totalChoices}
              </p>
              <p className="text-xs text-zinc-500 mt-1">Correct</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Button variant="outline" onClick={handleRestart}>
              <RotateCcw className="h-4 w-4 mr-2" />
              Try Again
            </Button>
            <Button
              onClick={() => router.push("/awareness/scenarios")}
              className="bg-cyan-500 hover:bg-cyan-600 text-black"
            >
              More Scenarios
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // ── Active scenario ──
  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Back + progress */}
      <div className="space-y-3">
        <button
          onClick={() => router.push("/awareness/scenarios")}
          className="flex items-center gap-1.5 text-xs text-zinc-500 hover:text-zinc-300 transition-colors"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          All Scenarios
        </button>

        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold text-zinc-100">
              {scenario.icon} {scenario.title}
            </h1>
            <p className="text-xs text-zinc-500 mt-0.5">
              Step {currentStep + 1} of {scenario.steps.length}
            </p>
          </div>
          {totalChoices > 0 && (
            <span className="text-xs text-zinc-500">
              Score: {score}/{totalChoices}
            </span>
          )}
        </div>

        {/* Progress bar */}
        <div className="h-1 w-full rounded-full bg-zinc-800 overflow-hidden">
          <div
            className="h-full rounded-full bg-cyan-500 transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Step content */}
      <div className="space-y-4">
        {step.type === "message" && (
          <MessageStep step={step} />
        )}

        {step.type === "choice" && (
          <ChoiceStep
            step={step}
            selectedOption={selectedOption}
            showFeedback={showFeedback}
            onSelect={handleSelectOption}
          />
        )}
      </div>

      {/* Next button */}
      <div className="flex justify-end pt-2">
        <Button
          onClick={handleNext}
          disabled={!canProceed}
          className="bg-cyan-500 hover:bg-cyan-600 text-black disabled:opacity-40"
        >
          {currentStep === scenario.steps.length - 1 ? "Finish" : "Continue"}
          <ArrowRight className="h-4 w-4 ml-2" />
        </Button>
      </div>
    </div>
  );
}

// ── Sub-components ──

function MessageStep({ step }: { step: ScenarioStep }) {
  const roleStyles = {
    attacker: {
      bg: "bg-red-500/5 border-red-500/20",
      label: "🔴 Scammer",
      labelColor: "text-red-400",
    },
    narrator: {
      bg: "bg-zinc-800/50 border-zinc-700/50",
      label: "📖 Narrator",
      labelColor: "text-zinc-400",
    },
    system: {
      bg: "bg-cyan-500/5 border-cyan-500/20",
      label: "ℹ️ System",
      labelColor: "text-cyan-400",
    },
  };

  const style = roleStyles[step.role || "narrator"];

  return (
    <div className={`rounded-xl border p-5 ${style.bg}`}>
      <p className={`text-xs font-medium mb-2 ${style.labelColor}`}>
        {style.label}
      </p>
      <p className="text-sm text-zinc-300 leading-relaxed whitespace-pre-line">
        {step.message}
      </p>
    </div>
  );
}

function ChoiceStep({
  step,
  selectedOption,
  showFeedback,
  onSelect,
}: {
  step: ScenarioStep;
  selectedOption: number | null;
  showFeedback: boolean;
  onSelect: (index: number) => void;
}) {
  return (
    <div className="space-y-4">
      {/* Prompt */}
      <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4">
        <p className="text-xs font-medium text-amber-400 mb-1">
          <AlertTriangle className="h-3.5 w-3.5 inline mr-1" />
          Decision Point
        </p>
        <p className="text-sm text-zinc-200 font-medium">{step.prompt}</p>
      </div>

      {/* Options */}
      <div className="space-y-2">
        {step.options?.map((option, index) => {
          const isSelected = selectedOption === index;
          const isCorrect = index === step.correct_index;
          let optionStyle =
            "border-zinc-700/50 bg-zinc-800/30 hover:border-zinc-600 hover:bg-zinc-800/50 cursor-pointer";

          if (showFeedback) {
            if (isCorrect) {
              optionStyle =
                "border-green-500/40 bg-green-500/10";
            } else if (isSelected && !isCorrect) {
              optionStyle =
                "border-red-500/40 bg-red-500/10";
            } else {
              optionStyle = "border-zinc-800 bg-zinc-900/50 opacity-50";
            }
          }

          return (
            <button
              key={index}
              onClick={() => onSelect(index)}
              disabled={showFeedback}
              className={`w-full flex items-start gap-3 rounded-lg border p-4 text-left transition-all ${optionStyle}`}
            >
              <span className="flex-none flex h-6 w-6 items-center justify-center rounded-full border border-zinc-600 bg-zinc-800 text-xs text-zinc-400 mt-0.5">
                {String.fromCharCode(65 + index)}
              </span>
              <span className="text-sm text-zinc-300">{option}</span>
              {showFeedback && isCorrect && (
                <CheckCircle2 className="h-5 w-5 text-green-400 flex-none ml-auto" />
              )}
              {showFeedback && isSelected && !isCorrect && (
                <XCircle className="h-5 w-5 text-red-400 flex-none ml-auto" />
              )}
            </button>
          );
        })}
      </div>

      {/* Feedback */}
      {showFeedback && selectedOption !== null && step.feedback && (
        <div
          className={`rounded-lg border p-4 ${
            selectedOption === step.correct_index
              ? "border-green-500/20 bg-green-500/5"
              : "border-red-500/20 bg-red-500/5"
          }`}
        >
          <p className="text-sm text-zinc-300 leading-relaxed">
            {step.feedback[String(selectedOption)]}
          </p>
        </div>
      )}
    </div>
  );
}