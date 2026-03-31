"use client";

import { useRef, useEffect } from "react";
import { Loader2, Lightbulb } from "lucide-react";
import { ChatMessage } from "./chat-message";
import { useChat } from "@/hooks/use-chat";
import { PromptBox, type ToolItem } from "@/components/ui/chatgpt-prompt-input";
import type { AssistantMode } from "./mode-toggle";

const ShieldIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
  </svg>
);
const GlobeIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <circle cx="12" cy="12" r="10" /><path d="M2 12h20" />
    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
  </svg>
);
const NewsIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2" />
    <path d="M18 14h-8" /><path d="M15 18h-5" /><path d="M10 6h8v4h-8V6Z" />
  </svg>
);
const QuizIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M22 10v6M2 10l10-5 10 5-10 5z" />
    <path d="M6 12v5c3 3 12 3 12 0v-5" />
  </svg>
);
const AlertIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
    <line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" />
  </svg>
);

const CYBER_TOOLS: ToolItem[] = [
  { id: "analyzeEmail", name: "Analyze suspicious email", shortName: "Email", icon: ShieldIcon },
  { id: "checkUrl", name: "Check URL/QR safety", shortName: "URL", icon: GlobeIcon },
  { id: "cyberNews", name: "India cyber news", shortName: "News", icon: NewsIcon },
  { id: "generateQuiz", name: "Generate a quiz", shortName: "Quiz", icon: QuizIcon },
  { id: "reportFraud", name: "How to report fraud", shortName: "Report", icon: AlertIcon },
];

const TOOL_PROMPTS: Record<string, string> = {
  analyzeEmail: "Analyze this email for phishing red flags: ",
  checkUrl: "Is this URL safe? Check for suspicious patterns: ",
  cyberNews: "What are the latest cybersecurity threats and incidents in India?",
  generateQuiz: "Generate a cybersecurity quiz about ",
  reportFraud: "How do I report cyber fraud in India? What are the steps and helpline numbers?",
};

const QUICK_PROMPTS: Record<AssistantMode, string[]> = {
  general: [
    "How to spot a phishing email?",
    "Is this UPI payment safe?",
    "What to do if I'm scammed?",
    "How do deepfake calls work?",
    "Tips for safe online banking",
  ],
  india_news: [
    "Latest cyber threats in India",
    "Recent CERT-In advisories",
    "UPI fraud trends 2024",
    "New cyber laws in India",
  ],
  quiz_gen: [
    "Generate quiz on UPI scams",
    "Test me on phishing detection",
    "Deepfake awareness quiz",
    "Quiz on KYC/OTP fraud",
  ],
};

const PLACEHOLDERS: Record<AssistantMode, string> = {
  general: "Ask about cybersecurity, scams, or digital safety…",
  india_news: "Ask about Indian cyber threats and news…",
  quiz_gen: "Describe the quiz topic…",
};

export function ChatPanel({ mode }: { mode: AssistantMode }) {
  const { messages, sendMessage, isLoading, clearChat, facts } = useChat({ mode });
  const endRef = useRef<HTMLDivElement>(null);
  const promptRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleToolSelect = (toolId: string) => {
    const prompt = TOOL_PROMPTS[toolId];
    if (prompt && promptRef.current) {
      const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
        window.HTMLTextAreaElement.prototype,
        "value"
      )?.set;
      nativeInputValueSetter?.call(promptRef.current, prompt);
      promptRef.current.dispatchEvent(new Event("input", { bubbles: true }));
      promptRef.current.focus();
      if (!prompt.endsWith(" ") && !prompt.endsWith(": ")) {
        sendMessage(prompt);
      }
    }
  };

  return (
    <div className="flex flex-1 flex-col min-h-0 overflow-hidden">

      {/* ── Scrollable messages ── */}
      <div className="flex-1 min-h-0 overflow-y-auto overscroll-contain">
        <div className="mx-auto w-full max-w-3xl px-4 sm:px-6 py-4 sm:py-6 space-y-4">

          {/* Empty state */}
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center min-h-[50vh] text-center space-y-5 px-2">
              <div className="flex h-14 w-14 sm:h-16 sm:w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-500/20 to-purple-500/20 border border-cyan-500/10">
                <Lightbulb className="h-7 w-7 sm:h-8 sm:w-8 text-cyan-400" />
              </div>

              <div className="space-y-1.5">
                <h2 className="text-lg sm:text-xl font-semibold text-zinc-200">
                  {mode === "general" && "Ask me about cyber safety"}
                  {mode === "india_news" && "India Cybersecurity News"}
                  {mode === "quiz_gen" && "Generate Cybersecurity Quizzes"}
                </h2>
                <p className="text-xs sm:text-sm text-zinc-400 max-w-sm mx-auto">
                  {mode === "general" &&
                    "UPI fraud, phishing, deepfakes — I'm your Indian cybersecurity guide."}
                  {mode === "india_news" &&
                    "AI-curated threat intelligence relevant to India."}
                  {mode === "quiz_gen" &&
                    "I'll create quiz questions on any Indian cybersecurity topic."}
                </p>
              </div>

              {/* Quick prompts — 2 per row on mobile */}
              <div className="grid grid-cols-2 sm:flex sm:flex-wrap gap-2 justify-center w-full max-w-sm sm:max-w-lg">
                {QUICK_PROMPTS[mode].map((p) => (
                  <button
                    key={p}
                    onClick={() => sendMessage(p)}
                    className="px-3 py-2 text-xs rounded-full border border-zinc-700 text-zinc-300 hover:border-cyan-500/50 hover:text-cyan-300 transition-colors text-left sm:text-center leading-tight"
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Messages */}
          {messages.map((m, i) => (
            <ChatMessage key={i} message={m} />
          ))}

          {/* Loading */}
          {isLoading && (
            <div className="flex items-center gap-2 text-zinc-400">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span className="text-sm">Thinking…</span>
            </div>
          )}

          {/* Fact card */}
          {facts.length > 0 && messages.length > 0 && (
            <div className="p-3 rounded-lg bg-cyan-500/5 border border-cyan-500/10">
              <p className="text-xs font-medium text-cyan-400 mb-1">
                💡 Did you know?
              </p>
              <p className="text-xs text-zinc-400">{facts[0]}</p>
            </div>
          )}

          <div ref={endRef} />
        </div>
      </div>

      {/* ── Sticky input ── */}
      <div className="flex-none border-t border-zinc-800/50">
        <div className="mx-auto w-full max-w-3xl px-3 sm:px-6 py-3">
          {messages.length > 0 && (
            <div className="flex justify-center mb-2">
              <button
                onClick={clearChat}
                className="text-[11px] text-zinc-500 hover:text-zinc-300 transition-colors px-3 py-1 rounded-full border border-zinc-800 hover:border-zinc-700"
              >
                ↻ Clear conversation
              </button>
            </div>
          )}

          <PromptBox
            ref={promptRef}
            onSend={sendMessage}
            isLoading={isLoading}
            tools={CYBER_TOOLS}
            onToolSelect={handleToolSelect}
            showTools={true}
            showAttach={false}
            placeholder={PLACEHOLDERS[mode]}
            footerText="For emergencies call 1930 or visit cybercrime.gov.in"
          />
        </div>
      </div>
    </div>
  );
}