"use client";

import { MessageSquare, Newspaper, GraduationCap } from "lucide-react";
import { cn } from "@/lib/utils";

export type AssistantMode = "general" | "india_news" | "quiz_gen";

const MODES: { id: AssistantMode; label: string; icon: typeof MessageSquare }[] = [
  { id: "general", label: "Chat", icon: MessageSquare },
  { id: "india_news", label: "News", icon: Newspaper },
  { id: "quiz_gen", label: "Quiz AI", icon: GraduationCap },
];

interface ModeToggleProps {
  mode: AssistantMode;
  onModeChange: (m: AssistantMode) => void;
}

export function ModeToggle({ mode, onModeChange }: ModeToggleProps) {
  return (
    <div className="flex rounded-lg border border-zinc-800 bg-zinc-900/50 p-1">
      {MODES.map(({ id, label, icon: Icon }) => (
        <button
          key={id}
          onClick={() => onModeChange(id)}
          className={cn(
            "flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all",
            mode === id
              ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/20"
              : "text-zinc-400 hover:text-zinc-200"
          )}
        >
          <Icon className="h-3.5 w-3.5" />
          {label}
        </button>
      ))}
    </div>
  );
}