"use client";

import { motion, useInView } from "framer-motion";
import DecryptedText from "@/components/ui/decrypted-text";
import { useRef } from "react";
import { PlayStoreButton } from "@/components/ui/play-store-button";
import { AppStoreButton } from "@/components/ui/app-store-button";
import { ChromeExtensionButton } from "@/components/ui/chrome-extension-button";
import { Smartphone, Monitor, Shield } from "lucide-react";

export function DownloadSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section className="relative py-24 px-6" ref={ref}>
      <div className="mx-auto max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <div className="text-3xl lg:text-4xl font-bold text-white mb-4 flex flex-wrap items-center justify-center gap-1">
            <DecryptedText
              text="Get CyberShield "
              className=""
              animateOn="view"
              speed={30}
              sequential
            />
            <span className="text-cyan-400">
              <DecryptedText
                text="Everywhere"
                className=""
                animateOn="view"
                speed={30}
                sequential
              />
            </span>
          </div>
          <p className="text-zinc-400 text-lg max-w-xl mx-auto">
            Protect yourself on every device — mobile, desktop, and browser.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          {/* Mobile */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="rounded-xl border border-zinc-800 bg-zinc-950/80 p-8 text-center hover:border-cyan-500/30 transition-colors group"
          >
            <div className="h-14 w-14 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform">
              <Smartphone className="h-7 w-7 text-cyan-400" />
            </div>
            <h3 className="text-white font-semibold text-lg mb-2">Mobile App</h3>
            <p className="text-zinc-500 text-sm mb-6">
              Scan QR codes, verify calls, and take quizzes on the go.
            </p>
            <div className="space-y-3">
              <AppStoreButton className="w-full justify-center" />
              <PlayStoreButton className="w-full justify-center" />
            </div>
          </motion.div>

          {/* Browser Extension */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="rounded-xl border border-zinc-800 bg-zinc-950/80 p-8 text-center hover:border-purple-500/30 transition-colors group relative overflow-hidden"
          >
            {/* Popular badge */}
            <div className="absolute top-4 right-4 text-[10px] font-mono text-cyan-400 bg-cyan-500/10 border border-cyan-500/20 rounded-full px-2 py-0.5">
              Popular
            </div>
            <div className="h-14 w-14 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform">
              <Monitor className="h-7 w-7 text-purple-400" />
            </div>
            <h3 className="text-white font-semibold text-lg mb-2">
              Browser Extension
            </h3>
            <p className="text-zinc-500 text-sm mb-6">
              Real-time URL scanning and email warnings right in your browser.
            </p>
            <ChromeExtensionButton className="w-full justify-center" />
          </motion.div>

          {/* Web Platform */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="rounded-xl border border-zinc-800 bg-zinc-950/80 p-8 text-center hover:border-green-500/30 transition-colors group"
          >
            <div className="h-14 w-14 rounded-2xl bg-green-500/10 border border-green-500/20 flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform">
              <Shield className="h-7 w-7 text-green-400" />
            </div>
            <h3 className="text-white font-semibold text-lg mb-2">
              Web Platform
            </h3>
            <p className="text-zinc-500 text-sm mb-6">
              Full dashboard, detailed reports, and team management features.
            </p>
            <a
              href="/signup"
              className="inline-flex items-center justify-center w-full h-12 rounded-md bg-cyan-500 hover:bg-cyan-600 text-black font-semibold text-sm transition-colors"
            >
              Open Web App — Free
            </a>
          </motion.div>
        </div>
      </div>
    </section>
  );
}