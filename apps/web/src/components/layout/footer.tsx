import Link from "next/link";
import { Shield } from "lucide-react";
import { EXTERNAL_LINKS } from "@/lib/constants";

export function Footer() {
  return (
    <footer className="border-t border-border bg-background">
      <div className="container py-12">
        <div className="grid gap-8 md:grid-cols-4">
          {/* Brand */}
          <div className="space-y-3">
            <Link href="/" className="flex items-center gap-2">
              <Shield className="h-6 w-6 text-cs-cyan" />
              <span className="font-display font-bold text-lg">
                <span className="text-cs-cyan">Cyber</span>Shield
              </span>
            </Link>
            <p className="text-sm text-muted-foreground leading-relaxed">
              India-first AI platform for real-time deepfake & phishing
              detection with gamified cyber-awareness training.
            </p>
          </div>

          {/* Product */}
          <div className="space-y-3">
            <h4 className="text-sm font-semibold">Product</h4>
            <nav className="flex flex-col gap-2 text-sm text-muted-foreground">
              <Link href="/analyze/email" className="hover:text-foreground transition-colors">Email Analyzer</Link>
              <Link href="/analyze/url" className="hover:text-foreground transition-colors">URL / QR Analyzer</Link>
              <Link href="/analyze/audio" className="hover:text-foreground transition-colors">Audio Deepfake</Link>
              <Link href="/analyze/video" className="hover:text-foreground transition-colors">Video Deepfake</Link>
            </nav>
          </div>

          {/* Learn */}
          <div className="space-y-3">
            <h4 className="text-sm font-semibold">Learn</h4>
            <nav className="flex flex-col gap-2 text-sm text-muted-foreground">
              <Link href="/awareness/quizzes" className="hover:text-foreground transition-colors">Quizzes</Link>
              <Link href="/awareness/scenarios" className="hover:text-foreground transition-colors">Scenarios</Link>
              <Link href="/awareness/resources" className="hover:text-foreground transition-colors">Resources</Link>
            </nav>
          </div>

          {/* Government Resources */}
          <div className="space-y-3">
            <h4 className="text-sm font-semibold">Report Cyber Crime</h4>
            <nav className="flex flex-col gap-2 text-sm text-muted-foreground">
              <a
                href={EXTERNAL_LINKS.cyberCrimePortal}
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-foreground transition-colors"
              >
                cybercrime.gov.in ↗
              </a>
              <span>Helpline: <strong className="text-foreground">{EXTERNAL_LINKS.cyberCrimeHelpline}</strong></span>
              <a
                href={EXTERNAL_LINKS.certIn}
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-foreground transition-colors"
              >
                CERT-In ↗
              </a>
            </nav>
          </div>
        </div>

        <div className="mt-10 flex flex-col items-center justify-between gap-4 border-t border-border pt-6 md:flex-row">
          <p className="text-xs text-muted-foreground">
            © {new Date().getFullYear()} CyberShield AI. Aligned with Cyber
            Surakshit Bharat & ISEA initiatives.
          </p>
          <div className="flex gap-4 text-xs text-muted-foreground">
            <Link href="/help" className="hover:text-foreground transition-colors">Help</Link>
            <span>•</span>
            <span>v1.0.0</span>
          </div>
        </div>
      </div>
    </footer>
  );
}