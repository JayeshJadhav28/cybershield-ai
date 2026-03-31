"use client";

import { motion, useInView } from "framer-motion";
import BorderGlow from "@/components/ui/border-glow";
import DecryptedText from "@/components/ui/decrypted-text";
import { useRef } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ExternalLink, Phone, Landmark } from "lucide-react";

export function CtaSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section className="relative py-24 px-6" ref={ref}>
      <div className="mx-auto max-w-7xl">
        <BorderGlow className="rounded-2xl" borderRadius={36}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6 }}
            className="bg-gradient-to-br from-cyan-500/5 via-zinc-950 to-purple-500/5 p-10 lg:p-16 rounded-2xl"
          >
          <DecryptedText
            text="Secure People, Not Just Devices."
            className="text-3xl lg:text-4xl font-bold text-white mb-4"
            animateOn="view"
            speed={30}
            sequential
          />
          <p className="text-zinc-400 text-lg mb-8 max-w-xl">
            Deploy AI threat analysis and cyber awareness training in one
            workflow.
          </p>

          <div className="flex flex-wrap gap-4 mb-10">
            <Link href="/dashboard">
              <Button
                size="lg"
                className="bg-cyan-500 hover:bg-cyan-600 text-black font-semibold shadow-lg shadow-cyan-500/25"
              >
                Go To Dashboard
              </Button>
            </Link>
            <Link href="/help">
              <Button
                size="lg"
                variant="outline"
                className="border-zinc-700 text-zinc-300"
              >
                View Help Resources
              </Button>
            </Link>
          </div>

          {/* Govt resources */}
          <div className="grid sm:grid-cols-3 gap-4">
            {[
              {
                icon: Landmark,
                label: "cybercrime.gov.in",
                href: "https://cybercrime.gov.in",
              },
              {
                icon: Phone,
                label: "Helpline: 1930",
                href: "tel:1930",
              },
              {
                icon: Landmark,
                label: "CERT-In advisories",
                href: "https://www.cert-in.org.in",
              },
            ].map((resource) => (
              <a
                key={resource.label}
                href={resource.href}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-3 p-4 rounded-xl border border-zinc-800 bg-zinc-900/50 hover:bg-zinc-800/50 transition-colors group"
              >
                <resource.icon className="h-5 w-5 text-zinc-500 group-hover:text-cyan-400 transition-colors" />
                <span className="text-sm text-zinc-400 group-hover:text-zinc-300 transition-colors">
                  {resource.label}
                </span>
                <ExternalLink className="h-3 w-3 text-zinc-600 ml-auto" />
              </a>
            ))}
          </div>
          </motion.div>
        </BorderGlow>
      </div>
    </section>
  );
}