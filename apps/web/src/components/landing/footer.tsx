"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Shield, ChevronRight, ExternalLink } from "lucide-react";
import { FlickeringGrid } from "@/components/ui/flickering-grid";

const footerLinks = [
  {
    title: "Platform",
    links: [
      { label: "Email Analyzer", href: "/analyze/email" },
      { label: "URL / QR Scanner", href: "/analyze/url" },
      { label: "Audio Deepfake", href: "/analyze/audio" },
      { label: "Video Deepfake", href: "/analyze/video" },
    ],
  },
  {
    title: "Awareness",
    links: [
      { label: "Quizzes", href: "/awareness/quizzes" },
      { label: "Scenarios", href: "/awareness/scenarios" },
      { label: "Resources", href: "/awareness/resources" },
      { label: "AI Assistant", href: "/assistant" },
    ],
  },
  {
    title: "Resources",
    links: [
      {
        label: "Cyber Crime Portal",
        href: "https://cybercrime.gov.in",
        external: true,
      },
      {
        label: "CERT-In",
        href: "https://www.cert-in.org.in",
        external: true,
      },
      {
        label: "Helpline 1930",
        href: "tel:1930",
        external: true,
      },
      { label: "Help & FAQs", href: "/help" },
    ],
  },
];

function useMediaQuery(query: string) {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    const mql = window.matchMedia(query);
    const handler = () => setMatches(mql.matches);
    handler();
    mql.addEventListener("change", handler);
    return () => mql.removeEventListener("change", handler);
  }, [query]);

  return matches;
}

export function Footer() {
  const isMobile = useMediaQuery("(max-width: 768px)");

  return (
    <footer className="w-full bg-[#0a0a0f] border-t border-zinc-800/50">
      {/* ── Main content ── */}
      <div className="mx-auto max-w-7xl px-6 pt-16 pb-8">
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-12">
          {/* Brand column */}
          <div className="flex flex-col items-start gap-5 max-w-xs">
            <Link href="/" className="flex items-center gap-2">
              <Shield className="h-7 w-7 text-cyan-400" />
              <span className="text-lg font-bold">
                <span className="text-white">Cyber</span>
                <span className="text-cyan-400">Shield</span>
              </span>
            </Link>

            <p className="text-sm text-zinc-400 leading-relaxed">
              India&apos;s multi-modal AI platform for deepfake detection,
              phishing analysis, and cyber awareness — aligned with Cyber
              Surakshit Bharat and ISEA initiatives.
            </p>

            {/* Helpline badge */}
            <div className="flex items-center gap-2 rounded-lg border border-cyan-500/20 bg-cyan-500/5 px-3 py-2">
              <div className="h-2 w-2 rounded-full bg-cyan-400 animate-pulse" />
              <span className="text-xs text-cyan-400 font-medium">
                Cyber Crime Helpline: 1930
              </span>
            </div>
          </div>

          {/* Link columns */}
          <div className="flex flex-col sm:flex-row gap-10 sm:gap-16 md:gap-20">
            {footerLinks.map((column) => (
              <ul key={column.title} className="flex flex-col gap-3">
                <li className="mb-1 text-sm font-semibold text-white">
                  {column.title}
                </li>
                {column.links.map((link) => (
                  <li key={link.label}>
                    <Link
                      href={link.href}
                      {...("external" in link && link.external
                        ? { target: "_blank", rel: "noopener noreferrer" }
                        : {})}
                      className="group inline-flex items-center gap-1.5 text-sm text-zinc-400 hover:text-white transition-colors"
                    >
                      {link.label}
                      {"external" in link && link.external ? (
                        <ExternalLink className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                      ) : (
                        <ChevronRight className="h-3 w-3 opacity-0 translate-x-0 group-hover:opacity-100 group-hover:translate-x-0.5 transition-all" />
                      )}
                    </Link>
                  </li>
                ))}
              </ul>
            ))}
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-12 pt-6 border-t border-zinc-800/50 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-zinc-500">
            © {new Date().getFullYear()} CyberShield AI. All rights reserved.
          </p>
          <div className="flex items-center gap-6">
            <Link
              href="#"
              className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors"
            >
              Privacy Policy
            </Link>
            <Link
              href="#"
              className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors"
            >
              Terms of Service
            </Link>
            <Link
              href="https://cybercrime.gov.in"
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors"
            >
              Report Cyber Crime
            </Link>
          </div>
        </div>
      </div>

      {/* ── Flickering grid section ── */}
      <div className="w-full h-48 md:h-64 relative mt-4">
        <div className="absolute inset-0 bg-gradient-to-t from-transparent to-[#0a0a0f] z-10 from-40%" />
        <div className="absolute inset-0 mx-6">
          <FlickeringGrid
            text={isMobile ? "CyberShield" : "CyberShield AI"}
            fontSize={isMobile ? 50 : 90}
            fontWeight={700}
            className="h-full w-full"
            squareSize={2}
            gridGap={isMobile ? 2 : 3}
            color="#22d3ee"
            maxOpacity={0.25}
            flickerChance={0.1}
          />
        </div>
      </div>
    </footer>
  );
}