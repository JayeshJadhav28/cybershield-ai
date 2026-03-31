"use client";

import { motion, useInView, useMotionValue, useSpring } from "framer-motion";
import type { SpringOptions } from "framer-motion";
import { useRef, useState } from "react";
import {
  Mail, QrCode, AudioWaveform, Video, ShieldCheck, Radar, Fingerprint, Bot,
} from "lucide-react";
import DecryptedText from "@/components/ui/decrypted-text";

/* ─── Tilt spring config (mirrors TiltedCard) ─── */
const SPRING: SpringOptions = { damping: 30, stiffness: 100, mass: 2 };

/* ─── Reusable tilt wrapper ──────────────────────
   Wraps any children with the 3-D tilt + scale-on-hover
   behaviour extracted from TiltedCard.
──────────────────────────────────────────────── */
function TiltWrapper({
  children,
  className = "",
  rotateAmplitude = 12,
  scaleOnHover = 1.04,
}: {
  children: React.ReactNode;
  className?: string;
  rotateAmplitude?: number;
  scaleOnHover?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [lastY, setLastY] = useState(0);

  const rotateX = useSpring(useMotionValue(0), SPRING);
  const rotateY = useSpring(useMotionValue(0), SPRING);
  const scale    = useSpring(1, SPRING);

  function handleMouse(e: React.MouseEvent<HTMLDivElement>) {
    if (!ref.current) return;
    const rect    = ref.current.getBoundingClientRect();
    const offsetX = e.clientX - rect.left  - rect.width  / 2;
    const offsetY = e.clientY - rect.top   - rect.height / 2;
    rotateX.set((offsetY / (rect.height / 2)) * -rotateAmplitude);
    rotateY.set((offsetX / (rect.width  / 2)) *  rotateAmplitude);
    setLastY(offsetY);
  }

  function handleMouseEnter() { scale.set(scaleOnHover); }

  function handleMouseLeave() {
    scale.set(1);
    rotateX.set(0);
    rotateY.set(0);
  }

  return (
    /* perspective wrapper — must be a plain div, NOT motion.div */
    <div
      ref={ref}
      className="w-full h-full [perspective:800px]"
      onMouseMove={handleMouse}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <motion.div
        className={`w-full h-full [transform-style:preserve-3d] ${className}`}
        style={{ rotateX, rotateY, scale }}
      >
        {children}
      </motion.div>
    </div>
  );
}

/* ─── Feature data ───────────────────────────── */
const features = [
  { icon: Mail,          title: "Email Phishing Analysis",  desc: "Header anomalies, urgency language, spoofed sender detection." },
  { icon: QrCode,        title: "URL & QR Inspection",      desc: "Homograph, redirect chain and suspicious path fingerprinting." },
  { icon: AudioWaveform, title: "Audio Deepfake Signals",   desc: "Spectral artifacts and voice-clone confidence scoring." },
  { icon: Video,         title: "Video Deepfake Detection", desc: "Frame inconsistency, lip-sync and temporal anomaly checks." },
  { icon: ShieldCheck,   title: "Explainable Risk Output",  desc: "Readable rationale and confidence bands for every verdict." },
  { icon: Radar,         title: "Live Threat Radar",        desc: "Track trending scam patterns targeting your organization." },
  { icon: Fingerprint,   title: "Identity Safeguards",      desc: "Profile-level baseline behavior and impersonation warnings." },
  { icon: Bot,           title: "AI Co-Pilot Guidance",     desc: "Suggested next steps for containment and user response." },
];

/* ─── Section ────────────────────────────────── */
export function FeaturesSection() {
  const ref      = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section id="features" className="relative py-24 px-6" ref={ref}>
      <div className="mx-auto max-w-7xl">

        {/* Heading */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="mb-16"
        >
          <DecryptedText
            text="Feature Stack"
            className="text-3xl lg:text-4xl font-bold text-white mb-4"
            animateOn="view"
            speed={30}
            sequential
          />
          <div>
            <DecryptedText
              text="Built for threat detection, fast triage, and practical cyber behavior change."
              className="text-zinc-400 text-lg max-w-xl"
              animateOn="view"
              speed={12}
              sequential
            />
          </div>
        </motion.div>

        {/* Grid */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: i * 0.08 }}
              /* Full height so TiltWrapper fills the stagger container */
              className="h-full"
            >
              <TiltWrapper>
                {/* Card face — translateZ lifts it toward the viewer */}
                <div className="
                  w-full h-full p-6
                  rounded-[12px]
                  bg-[#111118]
                  border border-[#2a2a3a]
                  [transform:translateZ(20px)]
                  transition-colors duration-300
                  hover:border-cyan-500/40
                  hover:bg-[#13131f]
                ">
                  {/* Icon */}
                  <div className="
                    h-10 w-10 rounded-lg
                    bg-cyan-500/10 border border-cyan-500/20
                    flex items-center justify-center mb-4
                    [transform:translateZ(10px)]
                  ">
                    <feature.icon className="h-5 w-5 text-cyan-400" />
                  </div>

                  {/* Text */}
                  <h3 className="text-white font-semibold mb-2 [transform:translateZ(6px)]">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-zinc-500 leading-relaxed">
                    {feature.desc}
                  </p>

                  {/* Subtle cyan top-edge glow, elevated above the card face */}
                  <div
                    aria-hidden
                    className="
                      pointer-events-none
                      absolute inset-x-0 top-0 h-px
                      bg-gradient-to-r from-transparent via-cyan-500/40 to-transparent
                      rounded-t-[12px]
                      opacity-0 group-hover:opacity-100
                      [transform:translateZ(25px)]
                    "
                  />
                </div>
              </TiltWrapper>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}