"use client";

import { ImageIcon } from "lucide-react";
import { ImageUpload } from "@/components/analyze/image-upload";

export default function ImageAnalyzePage() {
  return (
    <div className="max-w-2xl mx-auto py-6 px-4">
      {/* ── Page Header ── */}
      <div className="mb-6">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-cyan-500/10 border border-cyan-500/20">
            <ImageIcon className="h-5 w-5 text-cyan-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-zinc-100">Image Analyzer</h1>
            <p className="text-zinc-400 text-sm mt-0.5">
              Upload a face image to detect AI-generated or manipulated content.
            </p>
          </div>
        </div>
      </div>

      <ImageUpload />
    </div>
  );
}