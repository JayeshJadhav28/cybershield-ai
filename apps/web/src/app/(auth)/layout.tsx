import { CyberMatrixBg } from "@/components/ui/cyber-matrix-bg";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="relative min-h-screen bg-[#00040f] flex items-center justify-center overflow-hidden">
      {/* Cyan-tinted matrix background */}
      <CyberMatrixBg />

      {/* Dark overlay so card stays readable */}
      <div className="absolute inset-0 z-[1] bg-black/50" />

      {/* Subtle radial cyan glow behind the card */}
      <div
        className="absolute inset-0 z-[2] pointer-events-none"
        style={{
          background:
            "radial-gradient(ellipse 60% 50% at 50% 50%, rgba(34,211,238,0.06) 0%, transparent 70%)",
        }}
      />

      {/* Centered card */}
      <div className="relative z-10 w-full max-w-md mx-auto px-4 py-8">
        {children}
      </div>
    </div>
  );
}