"use client";

import { useEffect, useRef, useState } from "react";
import { motion, useInView } from "framer-motion";
import GlareHover from "@/components/ui/glare-hover";

interface StatItemProps {
  value: string;
  label: string;
  delay: number;
}

function AnimatedStat({ value, label, delay }: StatItemProps) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });
  const [displayed, setDisplayed] = useState("0");

  useEffect(() => {
    if (!isInView) return;
    const numericMatch = value.match(/[\d.]+/);
    if (!numericMatch) { setDisplayed(value); return; }
    const target = parseFloat(numericMatch[0]);
    const suffix = value.replace(numericMatch[0], "");
    const duration = 2000;
    const start = Date.now();
    const timer = setInterval(() => {
      const elapsed = Date.now() - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = target * eased;
      setDisplayed(
        (target >= 100 ? current.toFixed(1) : current < 10 ? current.toFixed(0) : current.toFixed(1)) + suffix
      );
      if (progress >= 1) clearInterval(timer);
    }, 16);
    return () => clearInterval(timer);
  }, [isInView, value]);

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 20 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.6, delay }}
    >
      <GlareHover
        background="#111118"
        borderColor="#2a2a3a"
        borderRadius="12px"
        glareColor="#06b6d4"
        glareOpacity={0.2}
        className="p-6"
      >
        <div className="text-left w-full">
          <div className="text-3xl lg:text-4xl font-bold font-mono text-cyan-400 mb-1">
            {displayed}
          </div>
          <div className="text-sm text-zinc-500">{label}</div>
        </div>
      </GlareHover>
    </motion.div>
  );
}

export function StatsSection() {
  const stats = [
    { value: "128.4k", label: "Emails Scanned" },
    { value: "24.6k", label: "Threats Flagged" },
    { value: "3s", label: "Avg Detection Time" },
    { value: "74%", label: "Awareness Score Lift" },
  ];

  return (
    <section className="relative py-16 px-6">
      <div className="mx-auto max-w-7xl">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {stats.map((stat, i) => (
            <AnimatedStat key={stat.label} {...stat} delay={i * 0.1} />
          ))}
        </div>
      </div>
    </section>
  );
}