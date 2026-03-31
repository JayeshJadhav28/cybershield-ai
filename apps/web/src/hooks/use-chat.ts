"use client";

import { useState, useCallback } from "react";
import type { Message } from "@/components/assistant/chat-message";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface UseChatOpts {
  mode: string;
}

export function useChat({ mode }: UseChatOpts) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [facts, setFacts] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(
    async (content: string) => {
      const userMsg: Message = { role: "user", content };
      setMessages((prev) => [...prev, userMsg]);
      setIsLoading(true);
      setError(null);

      try {
        const history = [...messages, userMsg].map((m) => ({
          role: m.role,
          content: m.content,
        }));

        const res = await fetch(`${API}/assistant/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ messages: history, mode }),
        });

        if (!res.ok) throw new Error(`API ${res.status}`);

        const data = await res.json();

        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: data.reply },
        ]);
        if (data.facts?.length) setFacts(data.facts);
      } catch (err: any) {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content:
              "⚠️ Couldn't reach the assistant. Check your connection.\n\n" +
              "Report cyber fraud at **cybercrime.gov.in** or call **1930**.",
          },
        ]);
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    },
    [messages, mode],
  );

  const clearChat = useCallback(() => {
    setMessages([]);
    setFacts([]);
    setError(null);
  }, []);

  return { messages, sendMessage, isLoading, clearChat, facts, error };
}