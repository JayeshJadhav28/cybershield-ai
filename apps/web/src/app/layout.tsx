import type { Metadata, Viewport } from "next";
import { Inter, Space_Grotesk, JetBrains_Mono } from "next/font/google";
import { ThemeProvider } from "@/providers/theme-provider";
import { QueryProvider } from "@/providers/query-provider";
import { AuthProvider } from "@/providers/auth-provider";
import { Toaster } from "@/components/ui/sonner";
import "./globals.css";

/* ── Font Loading (self-hosted via next/font) ── */
const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-space-grotesk",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains-mono",
  display: "swap",
});

/* ── Metadata ── */
export const metadata: Metadata = {
  title: {
    default: "CyberShield AI — Detect Deepfakes & Phishing in Real Time",
    template: "%s | CyberShield AI",
  },
  description:
    "India-first AI platform that detects deepfake audio/video and phishing attempts in real time, with explainable risk scores and gamified cyber-awareness training.",
  keywords: [
    "deepfake detection",
    "phishing detection",
    "cyber security",
    "AI security",
    "UPI fraud",
    "QR scam",
    "cyber awareness",
    "India",
  ],
  authors: [{ name: "CyberShield AI" }],
  openGraph: {
    type: "website",
    locale: "en_IN",
    url: "https://cybershield.ai",
    title: "CyberShield AI — Detect Deepfakes & Phishing",
    description:
      "Multi-modal AI platform for real-time cyber threat detection and awareness.",
    siteName: "CyberShield AI",
    images: [{ url: "/images/og-image.png", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "CyberShield AI",
    description: "Detect deepfakes & phishing in real time.",
    images: ["/images/og-image.png"],
  },
  icons: {
    icon: [
      { url: "/publiccybershieldai/favicon.ico" },
      { url: "/publiccybershieldai/apple-icon.png", rel: "apple-touch-icon", sizes: "180x180" },
      { url: "/publiccybershieldai/icon0.svg", rel: "icon", type: "image/svg+xml" },
      { url: "/publiccybershieldai/icon1.png", rel: "icon", type: "image/png", sizes: "32x32" },
    ],
  },
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#ffffff" },
    { media: "(prefers-color-scheme: dark)", color: "#0a0a0f" },
  ],
  width: "device-width",
  initialScale: 1,
};

/* ── Root Layout ── */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${inter.variable} ${spaceGrotesk.variable} ${jetbrainsMono.variable}`}
    >
      <head>
        <meta name="apple-mobile-web-app-title" content="CyberShield" />
        <link rel="icon" href="/publiccybershieldai/favicon.ico" type="image/x-icon" />
        <link rel="apple-touch-icon" sizes="180x180" href="/publiccybershieldai/apple-icon.png" />
        <link rel="icon" type="image/svg+xml" href="/publiccybershieldai/icon0.svg" />
        <link rel="icon" type="image/png" sizes="32x32" href="/publiccybershieldai/icon1.png" />
        <link rel="manifest" href="/publiccybershieldai/manifest.json" />
      </head>
      <body className="min-h-screen font-sans antialiased">
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          disableTransitionOnChange
        >
          <QueryProvider>
            <AuthProvider>
              {children}
              <Toaster
                position="bottom-right"
                toastOptions={{
                  classNames: {
                    toast: "bg-card border-border text-foreground",
                    title: "text-foreground",
                    description: "text-muted-foreground",
                  },
                }}
              />
            </AuthProvider>
          </QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}