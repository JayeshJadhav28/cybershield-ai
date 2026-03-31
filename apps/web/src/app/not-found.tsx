"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Glitchy404 } from "@/components/ui/glitchy-404";
import { Shield, ArrowLeft, Home } from "lucide-react";
import LetterGlitch from "@/components/ui/letter-glitch";

export default function NotFound() {
  return (
    <div className="relative min-h-screen bg-[#0a0a0f] flex flex-col items-center justify-center overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 z-0 opacity-10">
        <LetterGlitch
          glitchColors={["#ef4444", "#f59e0b", "#06b6d4"]}
          glitchSpeed={80}
          outerVignette={true}
          smooth={true}
        />
      </div>

      <div className="relative z-10 flex flex-col items-center text-center px-6">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 mb-12">
          <Shield className="h-8 w-8 text-cyan-400" />
          <span className="text-xl font-bold">
            <span className="text-white">Cyber</span>
            <span className="text-cyan-400">Shield</span>
          </span>
        </Link>

        {/* Glitchy 404 */}
        <div className="mb-8">
          <Glitchy404 width={500} height={140} color="#06b6d4" />
        </div>

        {/* Message */}
        <h2 className="text-2xl font-bold text-white mb-3">
          Page Not Found
        </h2>
        <p className="text-zinc-500 max-w-md mb-8">
          The page you&apos;re looking for doesn&apos;t exist or has been moved.
          It might have been a phishing attempt. 😉
        </p>

        {/* Actions */}
        <div className="flex gap-4">
          <Link href="/">
            <Button className="bg-cyan-500 hover:bg-cyan-600 text-black font-semibold gap-2">
              <Home className="h-4 w-4" />
              Back to Home
            </Button>
          </Link>
          <Button
            variant="outline"
            className="border-zinc-700 text-zinc-400 gap-2"
            onClick={() => window.history.back()}
          >
            <ArrowLeft className="h-4 w-4" />
            Go Back
          </Button>
        </div>

        {/* Helpline */}
        <p className="mt-12 text-xs text-zinc-700">
          Suspect a real cyber threat? Report at{" "}
          <a
            href="https://cybercrime.gov.in"
            className="text-cyan-600 hover:text-cyan-500 underline"
          >
            cybercrime.gov.in
          </a>{" "}
          or call <span className="text-white font-bold">1930</span>
        </p>
      </div>
    </div>
  );
}