import type { ReactNode } from "react";
import Noise from "@/components/ui/noise";

export default function AnalyzeLayout({ children }: { children: ReactNode }) {
  return (
    <div className="relative min-h-full">
      {/* Noise grain background */}
      <Noise
        patternSize={250}
        patternRefreshInterval={3}
        patternAlpha={12}
      />

      {/* Page content — above the noise */}
      <div className="relative z-10 mx-auto max-w-3xl">
        {children}
      </div>
    </div>
  );
}