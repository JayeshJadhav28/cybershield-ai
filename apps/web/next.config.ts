import type { NextConfig } from "next";

// ─── ML model file extensions that must NEVER be bundled in the frontend ──────
const ML_MODEL_EXTENSIONS = ["pt", "pkl", "h5", "onnx", "bin", "safetensors", "npy", "npz"];

// ─── Heavy ML / inference packages — must stay on the server and never be
//     bundled into client-side JS. Listed here as a safety net so the build
//     fails fast if they are accidentally installed. ─────────────────────────
const ML_EXTERNAL_PACKAGES = [
  "@tensorflow/tfjs-node",
  "@tensorflow/tfjs",
  "onnxruntime-node",
  "onnxruntime-web",
  "torch",
  "ml5",
  "brain.js",
  "synaptic",
  "natural",
  "compromise",
];

const nextConfig: NextConfig = {
  // Enable React strict mode for development
  reactStrictMode: true,

  // ── Prevent heavy ML packages from being bundled (safety net) ─────────────
  serverExternalPackages: ML_EXTERNAL_PACKAGES,

  // ── Stop large model/dataset files from being traced into .next/ output ───
  // This is the primary safeguard against build freezes caused by large files.
  outputFileTracingExcludes: {
    "*": [
      `**/*.{${ML_MODEL_EXTENSIONS.join(",")}}`,
      "**/models/**",
      "**/datasets/**",
      "**/data/**",
      "**/notebooks/**",
    ],
  },

  // Image optimization
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**",
      },
    ],
  },

  // Environment variables available at build time
  env: {
    NEXT_PUBLIC_APP_NAME: "CyberShield AI",
    NEXT_PUBLIC_APP_VERSION: "1.0.0",
  },

  // Proxy API calls in development
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}/:path*`,
      },
    ];
  },

  // Security headers
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=()",
          },
        ],
      },
    ];
  },

  // ── Webpack: reject any model file type that enters the module graph ───────
  webpack(config) {
    config.module.rules.push({
      test: new RegExp(`\\.(${ML_MODEL_EXTENSIONS.join("|")})$`),
      use: "null-loader",
    });
    return config;
  },
};

export default nextConfig;