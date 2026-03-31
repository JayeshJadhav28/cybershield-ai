"use client";

import { Bot, User } from "lucide-react";
import { cn } from "@/lib/utils";

export interface Message {
  role: "user" | "assistant";
  content: string;
}

export function ChatMessage({ message }: { message: Message }) {
  const isUser = message.role === "user";

  return (
    <div className={cn("flex gap-3 px-2", isUser ? "flex-row-reverse" : "flex-row")}>
      {/* avatar */}
      <div
        className={cn(
          "flex-none flex h-8 w-8 items-center justify-center rounded-lg",
          isUser
            ? "bg-purple-500/10 border border-purple-500/20"
            : "bg-cyan-500/10 border border-cyan-500/20"
        )}
      >
        {isUser ? (
          <User className="h-4 w-4 text-purple-400" />
        ) : (
          <Bot className="h-4 w-4 text-cyan-400" />
        )}
      </div>

      {/* bubble */}
      <div
        className={cn(
          "max-w-[80%] rounded-xl px-4 py-3 text-sm leading-relaxed",
          isUser
            ? "bg-purple-500/10 border border-purple-500/10 text-zinc-200"
            : "bg-zinc-800/50 border border-zinc-700/50 text-zinc-300"
        )}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div
            className="prose prose-invert prose-sm max-w-none prose-p:text-zinc-300 prose-strong:text-zinc-200 prose-a:text-cyan-400 prose-code:text-cyan-300 prose-code:bg-zinc-800 prose-code:px-1 prose-code:rounded prose-li:text-zinc-300"
            dangerouslySetInnerHTML={{ __html: md(message.content) }}
          />
        )}
      </div>
    </div>
  );
}

/** Minimal markdown → HTML (swap for react-markdown in production) */
function md(t: string): string {
  return t
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/^### (.+)$/gm, '<h3 class="text-base mt-3 mb-1">$1</h3>')
    .replace(/^## (.+)$/gm, '<h2 class="text-lg mt-3 mb-1">$1</h2>')
    .replace(/^[•\-\*] (.+)$/gm, "<li>$1</li>")
    .replace(/^\d+\. (.+)$/gm, "<li>$1</li>")
    .replace(/((?:<li>.*<\/li>\n?)+)/g, '<ul class="list-disc pl-4 my-1">$1</ul>')
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
    .replace(/\n\n/g, "</p><p>")
    .replace(/\n/g, "<br/>");
}