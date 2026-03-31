"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Shield, Sparkles, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import LetterGlitch from "@/components/ui/letter-glitch";
import BorderGlow from "@/components/ui/border-glow";
import DecryptedText from "@/components/ui/decrypted-text";

const terminalLines = [
  { text: "$ analyze --type email --source inbox-293.eml", delay: 0 },
  { text: "Parsing sender: support@paytm-secur1ty.in", delay: 800 },
  { text: "DKIM mismatch: TRUE", delay: 1400 },
  { text: "Urgency markers: 4 (high)", delay: 2000 },
  { text: "Credential harvest intent: 0.91", delay: 2600 },
];

export function HeroSection() {
  const [visibleLines, setVisibleLines] = useState(0);
  const [typingText, setTypingText] = useState("");
  const verdictRef = useRef(false);

  useEffect(() => {
    const timers: NodeJS.Timeout[] = [];
    terminalLines.forEach((line, i) => {
      timers.push(setTimeout(() => setVisibleLines(i + 1), line.delay));
    });
    timers.push(
      setTimeout(() => {
        verdictRef.current = true;
        setTypingText("Verdict: HIGH RISK PHISHING • Confidence 96.2%");
      }, 3400)
    );
    return () => timers.forEach(clearTimeout);
  }, []);

  return (
    <section className="relative min-h-[100vh] flex items-center overflow-hidden">
      {/* LetterGlitch Background */}
      <div className="absolute inset-0 z-0 opacity-20">
        <LetterGlitch
          glitchColors={["#06b6d4", "#3b82f6", "#8b5cf6"]}
          glitchSpeed={60}
          outerVignette={true}
          centerVignette={false}
          smooth={true}
        />
      </div>

      {/* Gradient overlay */}
      <div className="absolute inset-0 z-[1] bg-gradient-to-b from-[#0a0a0f]/60 via-transparent to-[#0a0a0f]" />

      <div className="relative z-10 mx-auto max-w-7xl px-6 py-10 lg:py-20 w-full">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left content */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          >
            {/* Badge */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
              className="inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-4 py-1.5 text-sm text-cyan-400 mb-8"
            >
              <Sparkles className="h-4 w-4" />
              India-First AI Platform for Cyber Defense & Awareness
            </motion.div>

            {/* Heading with DecryptedText */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight leading-[1.1] mb-6">
              {/* "Detect " — plain white, decrypts first */}
              <DecryptedText
                text="Detect "
                animateOn="view"
                sequential
                revealDirection="start"
                speed={40}
                className="text-white"
                encryptedClassName="text-zinc-600"
                parentClassName="inline"
              />

              {/* "Cyber Threats" — gradient, decrypts with slight delay via sequential */}
              <DecryptedText
                text="Cyber Threats"
                animateOn="view"
                sequential
                revealDirection="start"
                speed={35}
                className="bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500 bg-clip-text text-transparent"
                encryptedClassName="text-zinc-600"
                parentClassName="inline"
              />

              <br />

              {/* "Before People Fall For Them." — plain white, last line */}
              <DecryptedText
                text="Before People Fall For Them."
                animateOn="view"
                sequential
                revealDirection="start"
                speed={30}
                className="text-white"
                encryptedClassName="text-zinc-600"
                parentClassName="inline"
              />
            </h1>

            {/* Subtitle */}
            <p className="text-lg text-zinc-400 max-w-xl mb-8 leading-relaxed">
              Real-time phishing and deepfake detection, paired with gamified
              cyber-awareness workflows tailored for Indian users, businesses, and
              institutions.
            </p>

            {/* CTAs */}
            <div className="flex flex-wrap gap-4 mb-8">
              <Link href="/signin">
                <Button
                  size="lg"
                  className="bg-cyan-500 hover:bg-cyan-600 text-black font-semibold px-6 shadow-lg shadow-cyan-500/25 transition-all hover:shadow-cyan-500/40 hover:scale-105"
                >
                  Start Threat Scan
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link href="/awareness/quizzes">
                <Button
                  size="lg"
                  variant="outline"
                  className="border-zinc-700 hover:bg-zinc-800/50 text-zinc-300 px-6 transition-all hover:scale-105"
                >
                  Try Awareness Quiz
                </Button>
              </Link>
            </div>

            {/* Feature pills */}
            <div className="flex flex-wrap gap-3">
              {["Govt Resource Linked", "Human-Readable Explainability", "Multi-Modal Detection"].map(
                (pill) => (
                  <span
                    key={pill}
                    className="text-xs text-zinc-500 border border-zinc-800 rounded-full px-3 py-1.5 bg-zinc-900/50"
                  >
                    {pill}
                  </span>
                )
              )}
            </div>
          </motion.div>

          {/* Right - Terminal */}
          <motion.div
            initial={{ opacity: 0, x: 40 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="hidden lg:block"
          >
            <BorderGlow className="rounded-xl" borderRadius={20}>
              <div className="rounded-xl border border-zinc-800 bg-zinc-950/80 backdrop-blur-xl shadow-2xl shadow-cyan-500/5 overflow-hidden">
                {/* Terminal header */}
                <div className="flex items-center gap-2 px-4 py-3 border-b border-zinc-800">
                  <div className="h-3 w-3 rounded-full bg-red-500/80" />
                  <div className="h-3 w-3 rounded-full bg-yellow-500/80" />
                  <div className="h-3 w-3 rounded-full bg-green-500/80" />
                  <span className="ml-3 text-xs text-zinc-500 font-mono">
                    analysis-terminal
                  </span>
                </div>
                {/* Terminal body */}
                <div className="p-5 font-mono text-sm space-y-2 min-h-[220px]">
                  {terminalLines.slice(0, visibleLines).map((line, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      className={
                        i === 0
                          ? "text-zinc-300"
                          : line.text.includes("TRUE") || line.text.includes("high")
                          ? "text-amber-400"
                          : "text-zinc-400"
                      }
                    >
                      {line.text}
                    </motion.div>
                  ))}
                  {typingText && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="mt-3 border border-red-500/40 bg-red-500/10 rounded-md px-3 py-2 text-red-400 font-semibold"
                    >
                      {typingText}
                    </motion.div>
                  )}
                </div>
              </div>
            </BorderGlow>
          </motion.div>
        </div>
      </div>
    </section>
  );
}