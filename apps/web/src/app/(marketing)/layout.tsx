import Link from "next/link";
import { Header } from "@/components/landing/header";
import { Shield } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PlayStoreButton } from "@/components/ui/play-store-button";
import { AppStoreButton } from "@/components/ui/app-store-button";
import { Footer } from "@/components/landing/footer";

function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b border-zinc-800/50 bg-[#0a0a0f]/80 backdrop-blur-xl">
      <div className="mx-auto max-w-7xl px-6 flex items-center justify-between h-16">
        <Link href="/" className="flex items-center gap-2">
          <Shield className="h-7 w-7 text-cyan-400" />
          <span className="text-lg font-bold">
            <span className="text-white">Cyber</span>
            <span className="text-cyan-400">Shield</span>
          </span>
        </Link>

        <div className="hidden md:flex items-center gap-8">
          <a href="#features" className="text-sm text-zinc-400 hover:text-white transition-colors">
            Features
          </a>
          <a href="#how-it-works" className="text-sm text-zinc-400 hover:text-white transition-colors">
            How It Works
          </a>
          <a href="#awareness" className="text-sm text-zinc-400 hover:text-white transition-colors">
            Awareness
          </a>
        </div>

        <div className="flex items-center gap-3">
          <Link href="/signin">
            <Button variant="ghost" className="text-zinc-400 hover:text-white">
              Sign In
            </Button>
          </Link>
          <Link href="/signup">
            <Button className="bg-cyan-500 hover:bg-cyan-600 text-black font-semibold text-sm">
              Get Started →
            </Button>
          </Link>
        </div>
      </div>
    </nav>
  );
}

function MarketingFooter() {
  return (
    <footer className="border-t border-zinc-800 bg-[#0a0a0f]">
      <div className="mx-auto max-w-7xl px-6 py-16">
        <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-12">
          {/* Brand */}
          <div className="lg:col-span-2">
            <Link href="/" className="flex items-center gap-2 mb-4">
              <Shield className="h-6 w-6 text-cyan-400" />
              <span className="text-lg font-bold">
                <span className="text-white">Cyber</span>
                <span className="text-cyan-400">Shield</span>
              </span>
            </Link>
            <p className="text-sm text-zinc-500 mb-6 max-w-xs">
              India-first AI platform for real-time deepfake & phishing
              detection with gamified cyber-awareness training.
            </p>
            <div className="flex gap-2">
              <AppStoreButton className="text-xs h-10" />
              <PlayStoreButton className="text-xs h-10" />
            </div>
          </div>

          {/* Product */}
          <div>
            <h4 className="text-white font-semibold mb-4">Product</h4>
            <ul className="space-y-2">
              {["Email Analyzer", "URL / QR Analyzer", "Audio Deepfake", "Video Deepfake"].map((item) => (
                <li key={item}>
                  <Link href="/analyze/email" className="text-sm text-zinc-500 hover:text-zinc-300 transition-colors">
                    {item}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Learn */}
          <div>
            <h4 className="text-white font-semibold mb-4">Learn</h4>
            <ul className="space-y-2">
              {["Quizzes", "Scenarios", "Resources"].map((item) => (
                <li key={item}>
                  <Link href={`/awareness/${item.toLowerCase()}`} className="text-sm text-zinc-500 hover:text-zinc-300 transition-colors">
                    {item}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Report */}
          <div>
            <h4 className="text-white font-semibold mb-4">Report Cyber Crime</h4>
            <ul className="space-y-2">
              <li>
                <a href="https://cybercrime.gov.in" target="_blank" rel="noopener noreferrer" className="text-sm text-zinc-500 hover:text-zinc-300 transition-colors">
                  cybercrime.gov.in ↗
                </a>
              </li>
              <li className="text-sm text-zinc-500">
                Helpline: <span className="text-white font-bold">1930</span>
              </li>
              <li>
                <a href="https://www.cert-in.org.in" target="_blank" rel="noopener noreferrer" className="text-sm text-zinc-500 hover:text-zinc-300 transition-colors">
                  CERT-In ↗
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-zinc-800 mt-12 pt-8 flex flex-col sm:flex-row justify-between items-center gap-4">
          <p className="text-xs text-zinc-600">
            © 2024 CyberShield AI. Aligned with Cyber Surakshit Bharat & ISEA
            initiatives.
          </p>
          <div className="flex items-center gap-6">
            <Link href="/help" className="text-xs text-zinc-600 hover:text-zinc-400 transition-colors">
              Help
            </Link>
            <span className="text-xs text-zinc-700">•</span>
            <span className="text-xs text-zinc-700">v1.0.0</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default function MarketingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <Header />
      <main>{children}</main>
      <Footer />
    </>
  );
}