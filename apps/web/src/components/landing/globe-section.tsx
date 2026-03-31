"use client"

import { motion, useInView } from "framer-motion"
import DecryptedText from "@/components/ui/decrypted-text"
import { useRef, useState, useEffect } from "react"
import { GlobeAttack } from "@/components/ui/globe-attack"
import { AlertTriangle, Shield, Activity, TrendingUp } from "lucide-react"

function LiveCounter({ label, baseValue }: { label: string; baseValue: number }) {
  const [value, setValue] = useState(baseValue)

  useEffect(() => {
    const interval = setInterval(() => {
      setValue((v) => v + Math.floor(Math.random() * 5) + 1)
    }, 2000 + Math.random() * 3000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="flex items-center gap-2 text-sm">
      <span className="relative flex h-2 w-2">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75" />
        <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500" />
      </span>
      <span className="font-mono text-red-400 font-semibold tabular-nums">
        {value.toLocaleString()}
      </span>
      <span className="text-zinc-500">{label}</span>
    </div>
  )
}

export function GlobeSection() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-100px" })

  return (
    <section className="relative py-24 px-6 overflow-hidden" ref={ref}>
      {/* Background glow */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/2 left-1/4 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-red-500/5 rounded-full blur-[120px]" />
      </div>

      <div className="mx-auto max-w-7xl relative z-10">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left - Globe */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={isInView ? { opacity: 1, scale: 1 } : {}}
            transition={{ duration: 1, ease: "easeOut" }}
            className="max-w-[520px] mx-auto lg:mx-0"
          >
            <GlobeAttack className="w-full" speed={0.002} />
          </motion.div>

          {/* Right - Info */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.3 }}
          >
            <div className="inline-flex items-center gap-2 rounded-full border border-red-500/30 bg-red-500/10 px-3 py-1 text-xs text-red-400 mb-6 font-mono">
              <span className="relative flex h-1.5 w-1.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-red-500" />
              </span>
              LIVE THREAT INTELLIGENCE
            </div>

            <div className="text-3xl lg:text-4xl font-bold text-white mb-4 flex flex-wrap items-center gap-1">
              <DecryptedText
                text="Cyber Threats Targeting "
                className=""
                animateOn="view"
                speed={30}
                sequential
              />
              <span className="text-red-400">INDIA</span>
              <DecryptedText
                text="," 
                className=""
                animateOn="view"
                speed={30}
                sequential
              />
            </div>

            <p className="text-zinc-400 text-lg mb-8 leading-relaxed">
              India faces a 175% surge in phishing attacks on its financial
              sector. Our platform monitors threats in real-time across email,
              voice, video and payment channels.
            </p>

            {/* Live counters */}
            <div className="grid grid-cols-2 gap-3 mb-8 p-4 rounded-xl border border-zinc-800/50 bg-zinc-950/50">
              <LiveCounter label="phishing attempts" baseValue={12847} />
              <LiveCounter label="deepfake scans" baseValue={3291} />
              <LiveCounter label="URLs blocked" baseValue={8456} />
              <LiveCounter label="users protected" baseValue={24102} />
            </div>

            {/* Info cards */}
            <div className="space-y-3">
              {[
                {
                  icon: AlertTriangle,
                  color: "red",
                  title: "350M+ UPI users at risk",
                  desc: "AI-generated scams target mobile payment users daily",
                },
                {
                  icon: Shield,
                  color: "cyan",
                  title: "Aligned with CERT-In",
                  desc: "Integrated with cybercrime.gov.in and helpline 1930",
                },
                {
                  icon: Activity,
                  color: "orange",
                  title: "Real-time monitoring",
                  desc: "Track deepfake and phishing campaigns as they emerge",
                },
              ].map((item, i) => (
                <motion.div
                  key={item.title}
                  initial={{ opacity: 0, x: 20 }}
                  animate={isInView ? { opacity: 1, x: 0 } : {}}
                  transition={{ duration: 0.5, delay: 0.5 + i * 0.1 }}
                  className="flex gap-4 p-4 rounded-xl border border-zinc-800 bg-zinc-900/50 hover:bg-zinc-800/50 transition-colors group"
                >
                  <div
                    className={`h-10 w-10 rounded-lg flex items-center justify-center shrink-0 transition-transform group-hover:scale-110 ${
                      item.color === "red"
                        ? "bg-red-500/10 border border-red-500/20"
                        : item.color === "cyan"
                        ? "bg-cyan-500/10 border border-cyan-500/20"
                        : "bg-orange-500/10 border border-orange-500/20"
                    }`}
                  >
                    <item.icon
                      className={`h-5 w-5 ${
                        item.color === "red"
                          ? "text-red-400"
                          : item.color === "cyan"
                          ? "text-cyan-400"
                          : "text-orange-400"
                      }`}
                    />
                  </div>
                  <div>
                    <h4 className="text-white font-semibold text-sm">
                      {item.title}
                    </h4>
                    <p className="text-zinc-500 text-sm">{item.desc}</p>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Source attribution */}
            <div className="mt-6 flex items-center gap-2 text-[11px] text-zinc-600 font-mono">
              <TrendingUp className="h-3 w-3" />
              Data simulated from CERT-In & PhishTank reports • Updated every 15min
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}