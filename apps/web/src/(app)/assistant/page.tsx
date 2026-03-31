"use client";

import { useState } from "react";
import { Bot } from "lucide-react";
import { ChatPanel } from "@/components/assistant/chat-panel";
import { ModeToggle } from "@/components/assistant/mode-toggle";

export type AssistantMode = "general" | "india_news" | "quiz_gen";

export default function AssistantPage() {
  const [mode, setMode] = useState<AssistantMode>("general");

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] max-h-[calc(100vh-4rem)]">
      {/* Header */}
      <div className="flex-none border-b border-zinc-800 px-6 py-4">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-cyan-500/10 border border-cyan-500/20">
              <Bot className="h-5 w-5 text-cyan-400" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-zinc-100">
                CyberShield Assistant
              </h1>
              <p className="text-sm text-zinc-400">
                AI cybersecurity advisor for India &bull; Powered by Groq
              </p>
            </div>
          </div>
          <ModeToggle mode={mode} onModeChange={setMode} />
        </div>
      </div>

      {/* Chat */}
      <ChatPanel mode={mode} />
    </div>
  );
}