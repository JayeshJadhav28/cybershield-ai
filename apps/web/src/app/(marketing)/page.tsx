import { HeroSection } from "@/components/landing/hero-section";
import { StatsSection } from "@/components/landing/stats-section";
import { FeaturesSection } from "@/components/landing/features-section";
import { GlobeSection } from "@/components/landing/globe-section";
import { HowItWorksSection } from "@/components/landing/how-it-works";
import { AwarenessPreview } from "@/components/landing/awareness-preview";
import { DownloadSection } from "@/components/landing/download-section";
import { CtaSection } from "@/components/landing/cta-section";

export default function LandingPage() {
  return (
    <main className="bg-[#0a0a0f] min-h-screen">
      <HeroSection />
      <StatsSection />
      <FeaturesSection />
      <GlobeSection />
      <HowItWorksSection />
      <AwarenessPreview />
      <DownloadSection />
      <CtaSection />
    </main>
  );
}