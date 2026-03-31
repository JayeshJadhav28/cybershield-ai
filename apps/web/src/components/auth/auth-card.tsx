"use client";

import Link from "next/link";
import { Shield } from "lucide-react";

interface AuthCardProps {
  title: string;
  description: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
}

export function AuthCard({
  title,
  description,
  children,
  footer,
}: AuthCardProps) {
  return (
    <div className="relative">
      {/* ── Outer diffuse glow ── */}
      <div
        className="absolute -inset-3 rounded-2xl blur-2xl"
        style={{
          background:
            "linear-gradient(135deg, rgba(34,211,238,0.18), rgba(59,130,246,0.12), rgba(34,211,238,0.18))",
          animation: "card-glow-pulse 4s ease-in-out infinite",
        }}
      />

      {/* ── Thin border glow ── */}
      <div
        className="absolute -inset-px rounded-2xl"
        style={{
          background:
            "linear-gradient(135deg, rgba(34,211,238,0.55), rgba(59,130,246,0.40), rgba(99,102,241,0.30), rgba(34,211,238,0.55))",
          animation: "card-glow-pulse 4s ease-in-out infinite 0.6s",
        }}
      />

      {/* ── Card body ── */}
      <div className="relative rounded-2xl bg-[#00040f]/90 backdrop-blur-2xl border border-cyan-500/10 p-6 sm:p-8">

        {/* Logo + heading */}
        <div className="text-center mb-6">
          <Link href="/" className="inline-flex items-center gap-2 mb-4">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-cyan-400/10 border border-cyan-400/20">
              <Shield className="h-5 w-5 text-cyan-400" />
            </div>
            <span className="text-lg font-bold tracking-tight text-white">
              CyberShield{" "}
              <span className="text-cyan-400">AI</span>
            </span>
          </Link>

          <h1 className="text-xl font-semibold text-white">{title}</h1>
          <p className="text-sm text-slate-400 mt-1">{description}</p>
        </div>

        {/* Form slot */}
        {children}

        {/* Footer */}
        {footer && (
          <div className="mt-6 pt-4 border-t border-white/[0.05] text-center text-sm text-slate-400">
            {footer}
          </div>
        )}
      </div>

      <style>{`
        @keyframes card-glow-pulse {
          0%, 100% { opacity: 0.5; }
          50%       { opacity: 1;   }
        }
      `}</style>
    </div>
  );
}