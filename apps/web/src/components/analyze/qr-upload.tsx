'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  QrCode,
  Upload,
  Loader2,
  Scan,
  X,
  RotateCcw,
  Image as ImageIcon,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';
import { api } from '@/lib/api';
import type { AnalysisResult } from './result-card';
import { DemoSamplePicker } from './demo-sample-picker';

/* ── Constants ── */
const ACCEPT = {
  'image/png': ['.png'],
  'image/jpeg': ['.jpg', '.jpeg'],
  'image/webp': ['.webp'],
};
const MAX_SIZE = 5 * 1024 * 1024;

/* ── Props ── */
interface QrUploadProps {
  onResult: (result: AnalysisResult) => void;
  onReset: () => void;
}

/* ── Component ── */
export function QrUpload({ onResult, onReset }: QrUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const onDrop = useCallback((accepted: File[], rejected: any[]) => {
    if (rejected.length) {
      const err = rejected[0].errors?.[0];
      toast.error(
        err?.code === 'file-too-large'
          ? 'Image must be ≤ 5 MB'
          : 'Only PNG, JPG, or WebP images are accepted',
      );
      return;
    }
    const f = accepted[0];
    setFile(f);
    setPreview(URL.createObjectURL(f));
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPT,
    maxSize: MAX_SIZE,
    multiple: false,
  });

  async function handleAnalyze() {
    if (!file) return;
    setIsLoading(true);
    try {
      const result = await api.analyzeQr(file);
      onResult(result as AnalysisResult);
    } catch (err: any) {
      toast.error(err?.message ?? 'QR analysis failed.');
    } finally {
      setIsLoading(false);
    }
  }

  function handleReset() {
    setFile(null);
    if (preview) URL.revokeObjectURL(preview);
    setPreview(null);
    onReset();
  }

  return (
    <Card className="border-zinc-800/60 bg-zinc-900/70 backdrop-blur-sm">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-zinc-400">
            <QrCode className="h-4 w-4 text-indigo-500" />
            Upload QR Code Image
          </CardTitle>
          <div className="flex items-center gap-2">
            <DemoSamplePicker
              filterType="qr"
              onSelect={(s) => {
                if (s.file_url) {
                  toast.info('Demo QR: fetch from ' + s.file_url);
                }
              }}
            />
            <Button
              variant="ghost"
              size="sm"
              onClick={handleReset}
              className="h-7 gap-1.5 text-xs text-zinc-500 hover:text-zinc-300"
            >
              <RotateCcw className="h-3 w-3" />
              Reset
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Drop zone */}
        <div
          {...getRootProps()}
          className={cn(
            'relative flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-8 transition-all duration-200',
            isDragActive
              ? 'border-indigo-500/60 bg-indigo-500/5'
              : 'border-zinc-700/60 bg-zinc-800/20 hover:border-zinc-600 hover:bg-zinc-800/40',
          )}
        >
          <input {...getInputProps()} />

          {preview ? (
            <div className="relative">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={preview}
                alt="QR preview"
                className="max-h-48 max-w-full rounded-lg object-contain"
              />
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  handleReset();
                }}
                className="absolute -right-2 -top-2 rounded-full bg-zinc-800 p-1 text-zinc-400 shadow-md hover:text-zinc-200"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-3 text-center">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-indigo-500/10">
                {isDragActive ? (
                  <Upload className="h-7 w-7 animate-bounce text-indigo-400" />
                ) : (
                  <QrCode className="h-7 w-7 text-indigo-400" />
                )}
              </div>
              <div>
                <p className="text-sm font-medium text-zinc-300">
                  {isDragActive
                    ? 'Drop the image here'
                    : 'Drag & drop a QR code image'}
                </p>
                <p className="mt-1 text-xs text-zinc-500">or click to browse</p>
              </div>
              <div className="flex gap-1.5">
                {['PNG', 'JPG', 'WebP'].map((f) => (
                  <Badge
                    key={f}
                    variant="outline"
                    className="border-zinc-700 text-[10px] text-zinc-500"
                  >
                    {f}
                  </Badge>
                ))}
                <Badge
                  variant="outline"
                  className="border-zinc-700 text-[10px] text-zinc-500"
                >
                  ≤ 5 MB
                </Badge>
              </div>
            </div>
          )}
        </div>

        {/* File info bar */}
        {file && (
          <div className="flex items-center gap-2 rounded-lg border border-zinc-800 bg-zinc-800/40 px-3 py-2 text-xs text-zinc-400">
            <ImageIcon className="h-3.5 w-3.5 shrink-0" />
            <span className="truncate">{file.name}</span>
            <span className="ml-auto shrink-0 text-zinc-500">
              {(file.size / 1024).toFixed(0)} KB
            </span>
          </div>
        )}

        {/* Analyze button */}
        <Button
          disabled={!file || isLoading}
          onClick={handleAnalyze}
          className="w-full gap-2 bg-indigo-600 text-white hover:bg-indigo-500 disabled:opacity-50"
          data-testid="analyze-button"
        >
          {isLoading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Decoding QR…
            </>
          ) : (
            <>
              <Scan className="h-4 w-4" />
              Analyze QR Code
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
}