import type { NextConfig } from "next";

const ML_MODEL_EXTENSIONS = ["pt", "pkl", "h5", "onnx", "bin", "safetensors", "npy", "npz"];

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
  reactStrictMode: true,

  // ✅ ADD THIS — skips ESLint warnings during Vercel build
  eslint: {
    ignoreDuringBuilds: true,
  },

  serverExternalPackages: ML_EXTERNAL_PACKAGES,

  outputFileTracingExcludes: {
    "*": [
      `**/*.{${ML_MODEL_EXTENSIONS.join(",")}}`,
      "**/models/**",
      "**/datasets/**",
      "**/data/**",
      "**/notebooks/**",
    ],
  },

  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**",
      },
    ],
  },

  env: {
    NEXT_PUBLIC_APP_NAME: "CyberShield AI",
    NEXT_PUBLIC_APP_VERSION: "1.0.0",
  },

  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}/:path*`,
      },
    ];
  },

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

  webpack(config) {
    config.module.rules.push({
      test: new RegExp(`\\.(${ML_MODEL_EXTENSIONS.join("|")})$`),
      use: "null-loader",
    });
    return config;
  },
};

export default nextConfig;