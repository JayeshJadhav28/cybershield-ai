"use client";

import { useState } from "react";
import { Bot, Newspaper, GraduationCap } from "lucide-react";
import { ChatPanel } from "@/components/assistant/chat-panel";
import { type AssistantMode } from "@/components/assistant/mode-toggle";

const modes = [
  { id: "general" as const, label: "Chat", icon: Bot },
  { id: "india_news" as const, label: "News", icon: Newspaper },
  { id: "quiz_gen" as const, label: "Quiz AI", icon: GraduationCap },
];

export default function AssistantPage() {
  const [mode, setMode] = useState<AssistantMode>("general");

  return (
    <div className="-m-4 lg:-m-6 flex flex-col h-[calc(100vh-3.5rem)] overflow-hidden">

      {/* ── Header ── */}
      <div className="flex-none flex items-center justify-between gap-2 border-b border-zinc-800/50 px-4 py-2.5 sm:px-6 sm:py-3">

        {/* Left — logo + title */}
        <div className="flex items-center gap-2 min-w-0">
          <div className="flex-none flex h-8 w-8 sm:h-10 sm:w-10 items-center justify-center rounded-xl bg-cyan-500/10 border border-cyan-500/20">
            <Bot className="h-4 w-4 sm:h-5 sm:w-5 text-cyan-400" />
          </div>
          <div className="min-w-0">
            <h1 className="text-xs sm:text-sm font-semibold text-zinc-100 truncate">
              CyberShield Assistant
            </h1>
            <p className="hidden sm:block text-xs text-zinc-500 truncate">
              AI cybersecurity advisor for India • Powered by Groq
            </p>
          </div>
        </div>

        {/* Right — mode tabs */}
        <div className="flex-none flex items-center gap-0.5 sm:gap-1 rounded-lg border border-zinc-800 bg-zinc-900/50 p-0.5 sm:p-1">
          {modes.map((m) => {
            const Icon = m.icon;
            const active = mode === m.id;
            return (
              <button
                key={m.id}
                onClick={() => setMode(m.id)}
                className={`flex items-center gap-1 sm:gap-1.5 rounded-md px-2 py-1.5 sm:px-3 text-xs font-medium transition-all whitespace-nowrap ${
                  active
                    ? "bg-cyan-500/15 text-cyan-400 border border-cyan-500/30"
                    : "text-zinc-500 hover:text-zinc-300 border border-transparent"
                }`}
              >
                <Icon className="h-3.5 w-3.5 flex-none" />
                {/* Hide label on very small screens for "Quiz AI" */}
                <span className={m.id === "quiz_gen" ? "hidden xs:inline sm:inline" : ""}>
                  {m.label}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* ── Chat panel ── */}
      <ChatPanel mode={mode} />
    </div>
  );
}