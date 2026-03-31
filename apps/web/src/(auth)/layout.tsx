import type { Metadata } from "next";
import Link from "next/link";
import { Shield } from "lucide-react";
import { CyberMatrixBg } from "@/components/ui/cyber-matrix-bg";

export const metadata: Metadata = {
  title: {
    template: "%s | CyberShield AI",
    default: "Authentication | CyberShield AI",
  },
};

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="relative min-h-screen bg-black flex items-center justify-center overflow-hidden">
      {/* Matrix background */}
      <CyberMatrixBg />

      {/* Content layer — sits above the grid */}
      <div className="relative z-10 w-full max-w-md mx-auto px-4 py-8">
        {children}
      </div>
    </div>
  );
}
