"use client";

import { motion, useInView } from "framer-motion";
import DecryptedText from "@/components/ui/decrypted-text";
import BorderGlow from "@/components/ui/border-glow";
import { useRef, useState } from "react";
import { CheckCircle, AlertTriangle } from "lucide-react";

const options = [
  "Reply immediately and click the refund link",
  "Verify sender domain and call official support number",
  "Forward to teammates without checking",
  "Download attachment to inspect manually",
];

export function AwarenessPreview() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });
  const [selected, setSelected] = useState<number | null>(null);

  return (
    <section id="awareness" className="relative py-24 px-6" ref={ref}>
      <div className="mx-auto max-w-7xl">
        <div className="grid lg:grid-cols-2 gap-12 items-center">

          {/* Left - Info */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.8 }}
          >
            <DecryptedText
              text="Awareness Preview"
              className="text-3xl lg:text-4xl font-bold text-white mb-4"
              animateOn="view"
              speed={30}
              sequential
            />
            <div className="mb-8">
              <DecryptedText
                text="Turn every detection event into a teachable moment with guided quizzes and scam-scenario drills."
                className="text-zinc-400 text-lg mb-2 leading-relaxed"
                animateOn="view"
                speed={12}
                sequential
              />
            </div>
            <ul className="space-y-3">
              {[
                "Context-aware hints tied to real attack patterns",
                "Instant feedback with why/why-not explanation",
                "Team leaderboards and progress history",
              ].map((item) => (
                <li key={item} className="flex items-center gap-3 text-zinc-400">
                  <CheckCircle className="h-5 w-5 text-cyan-500 shrink-0" />
                  {item}
                </li>
              ))}
            </ul>
          </motion.div>

          {/* Right - Quiz mockup wrapped in BorderGlow */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <BorderGlow
              backgroundColor="#09090f"
              borderRadius={16}
              glowColor="186 100 50"
              colors={["#06b6d4", "#3b82f6", "#8b5cf6"]}
              glowRadius={48}
              glowIntensity={0.9}
              coneSpread={28}
              fillOpacity={0.35}
              edgeSensitivity={25}
              className="w-full"
            >
              <div className="p-6">
                <h3 className="text-white font-semibold mb-4">
                  Mock Quiz: What should you do first?
                </h3>

                {/* Phishing scenario */}
                <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg p-3 mb-4 flex items-start gap-2">
                  <AlertTriangle className="h-5 w-5 text-amber-400 shrink-0 mt-0.5" />
                  <p className="text-sm text-amber-200">
                    &quot;Your KYC will be suspended today. Click here to verify
                    now.&quot;
                  </p>
                </div>

                {/* Options */}
                <div className="space-y-2">
                  {options.map((option, i) => {
                    const isCorrect = i === 1;
                    const isSelected = selected === i;
                    return (
                      <button
                        key={i}
                        onClick={() => setSelected(i)}
                        className={`w-full text-left text-sm p-3 rounded-lg border transition-all ${
                          isSelected && isCorrect
                            ? "border-green-500/50 bg-green-500/10 text-green-300"
                            : isSelected && !isCorrect
                            ? "border-red-500/50 bg-red-500/10 text-red-300"
                            : "border-zinc-800 bg-zinc-900/50 text-zinc-400 hover:border-zinc-700 hover:bg-zinc-800/50"
                        }`}
                      >
                        {option}
                      </button>
                    );
                  })}
                </div>

                {selected !== null && (
                  <motion.p
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`mt-4 text-sm ${
                      selected === 1 ? "text-green-400" : "text-red-400"
                    }`}
                  >
                    {selected === 1
                      ? "✅ Correct! Always verify through official channels."
                      : "❌ Risky choice. The safest action is to verify the sender domain and contact official support directly."}
                  </motion.p>
                )}
              </div>
            </BorderGlow>
          </motion.div>

        </div>
      </div>
    </section>
  );
}