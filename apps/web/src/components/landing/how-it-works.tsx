"use client";

import { motion, useInView } from "framer-motion";
import DecryptedText from "@/components/ui/decrypted-text";
import { useRef } from "react";
import { Play, Cpu, Eye, CheckCircle } from "lucide-react";
import GlareHover from "@/components/ui/glare-hover";

const steps = [
  { icon: Play, number: "01", title: "Submit Signal", desc: "Paste email text, upload media, or scan a QR/URL." },
  { icon: Cpu, number: "02", title: "AI Triage", desc: "Models evaluate authenticity, intent, and threat level." },
  { icon: Eye, number: "03", title: "Human-Readable Verdict", desc: "Get confidence, reasons, and a risk grade instantly." },
  { icon: CheckCircle, number: "04", title: "Take Action", desc: "Report, block, notify users, and train teams proactively." },
];

export function HowItWorksSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section id="how-it-works" className="relative py-24 px-6" ref={ref}>
      <div className="mx-auto max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="mb-16"
        >
          <DecryptedText
            text="How It Works"
            className="text-3xl lg:text-4xl font-bold text-white mb-4"
            animateOn="view"
            speed={30}
            sequential
          />
          <div className="mb-8">
            <DecryptedText
              text="See how CyberShield analyzes signals, explains risks, and guides you to take the safest action."
              className="text-zinc-400 text-lg mb-2 leading-relaxed"
              animateOn="view"
              speed={12}
              sequential
            />
          </div>
        </motion.div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {steps.map((step, i) => (
            <motion.div
              key={step.title}
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: i * 0.12 }}
            >
              <GlareHover
                background="#111118"
                borderColor="#2a2a3a"
                borderRadius="12px"
                glareColor="#8b5cf6"
                glareOpacity={0.15}
                className="p-6 h-full"
              >
                <div className="w-full">
                  <div className="flex items-center justify-between mb-4">
                    <div className="h-10 w-10 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
                      <step.icon className="h-5 w-5 text-cyan-400" />
                    </div>
                    <span className="text-xs font-mono text-zinc-600">
                      {step.number}
                    </span>
                  </div>
                  <h3 className="text-white font-semibold mb-2">{step.title}</h3>
                  <p className="text-sm text-zinc-500 leading-relaxed">
                    {step.desc}
                  </p>
                </div>
              </GlareHover>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}