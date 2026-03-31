'use client';

import { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  Video,
  Loader2,
  Scan,
  RotateCcw,
  Play,
  Pause,
  FileVideo,
  AlertCircle,
  X,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';
import { api } from '@/lib/api';
import { FileDropzone } from './file-dropzone';
import { DemoSamplePicker, type DemoSample } from './demo-sample-picker';
import { useMediaUpload } from '@/hooks/use-media-upload';
import type { AnalysisResult } from './result-card';
import { motion } from 'framer-motion';

/* ------------------------------------------------------------------ */
/*  Constants                                                          */
/* ------------------------------------------------------------------ */
const ACCEPT = {
  'video/mp4': ['.mp4'],
  'video/x-msvideo': ['.avi'],
  'video/quicktime': ['.mov'],
  'video/webm': ['.webm'],
};
const MAX_SIZE = 50 * 1024 * 1024; // 50 MB
const MAX_DURATION = 60; // seconds

/* ------------------------------------------------------------------ */
/*  Video preview                                                      */
/* ------------------------------------------------------------------ */
function VideoPreview({
  objectUrl,
  isAnalyzing,
  onRemove,
}: {
  objectUrl: string;
  isAnalyzing: boolean;
  onRemove: () => void;
}) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [playing, setPlaying] = useState(false);

  function toggle() {
    const v = videoRef.current;
    if (!v) return;
    if (playing) {
      v.pause();
      setPlaying(false);
    } else {
      v.play();
      setPlaying(true);
    }
  }

  return (
    <div className="relative overflow-hidden rounded-xl border border-zinc-800 bg-zinc-950/60">
      {/* Remove button */}
      {!isAnalyzing && (
        <button
          type="button"
          onClick={onRemove}
          className="absolute right-2 top-2 z-10 rounded-full bg-zinc-900/80 p-1.5 text-zinc-400 transition hover:text-zinc-200"
        >
          <X className="h-4 w-4" />
        </button>
      )}

      {/* Video element */}
      <video
        ref={videoRef}
        src={objectUrl}
        className="max-h-64 w-full object-contain"
        onEnded={() => setPlaying(false)}
        muted
        playsInline
      />

      {/* Scanning overlay */}
      {isAnalyzing && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-zinc-950/70 backdrop-blur-sm">
          <div className="relative h-16 w-16">
            <div className="absolute inset-0 animate-ping rounded-full border-2 border-rose-500/40" />
            <div className="absolute inset-0 flex items-center justify-center">
              <Scan className="h-8 w-8 animate-pulse text-rose-400" />
            </div>
          </div>
          <p className="mt-3 text-sm font-medium text-rose-300">
            Analyzing frames…
          </p>
        </div>
      )}

      {/* Play toggle bar */}
      {!isAnalyzing && (
        <div className="absolute bottom-0 inset-x-0 flex items-center gap-2 bg-gradient-to-t from-zinc-950/90 to-transparent px-3 py-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={toggle}
            className="h-7 gap-1 text-xs text-zinc-300 hover:text-white"
            type="button"
          >
            {playing ? (
              <Pause className="h-3.5 w-3.5" />
            ) : (
              <Play className="h-3.5 w-3.5" />
            )}
            {playing ? 'Pause' : 'Play'}
          </Button>
        </div>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Frame analysis progress (shown during analysis)                    */
/* ------------------------------------------------------------------ */
function FrameProgress({
  framesAnalyzed,
  totalFrames,
}: {
  framesAnalyzed: number;
  totalFrames: number;
}) {
  const pct = totalFrames > 0 ? Math.round((framesAnalyzed / totalFrames) * 100) : 0;
  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-xs text-zinc-400">
        <span>Frame analysis progress</span>
        <span className="font-mono">
          {framesAnalyzed}/{totalFrames}
        </span>
      </div>
      <Progress value={pct} className="h-1.5 bg-zinc-800" />
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Props                                                              */
/* ------------------------------------------------------------------ */
interface VideoUploadProps {
  onResult: (result: AnalysisResult) => void;
  onReset: () => void;
}

/* ------------------------------------------------------------------ */
/*  Exported component                                                 */
/* ------------------------------------------------------------------ */
export function VideoUpload({ onResult, onReset }: VideoUploadProps) {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [fakeProgress, setFakeProgress] = useState({ done: 0, total: 0 });

  const { file, meta, isValidating, error, setFile, reset } =
    useMediaUpload({
      maxDuration: MAX_DURATION,
      onDurationError: (actual, max) =>
        toast.error(
          `Video exceeds maximum duration of ${max}s (actual: ${actual.toFixed(1)}s). Please upload a shorter clip.`,
        ),
    });

  function handleReset() {
    reset();
    setFakeProgress({ done: 0, total: 0 });
    onReset();
  }

  async function handleAnalyze() {
    if (!file) return;
    setIsAnalyzing(true);

    /* Simulate frame progress updates for UX */
    const estimatedFrames = Math.ceil((meta?.duration ?? 10));
    setFakeProgress({ done: 0, total: estimatedFrames });

    const progressInterval = setInterval(() => {
      setFakeProgress((prev) => {
        if (prev.done >= prev.total) return prev;
        return { ...prev, done: prev.done + 1 };
      });
    }, 800);

    try {
      const result = await api.analyzeVideo(file);
      clearInterval(progressInterval);
      setFakeProgress({ done: estimatedFrames, total: estimatedFrames });
      onResult(result as AnalysisResult);
    } catch (err: any) {
      toast.error(err?.message ?? 'Video analysis failed.');
    } finally {
      clearInterval(progressInterval);
      setIsAnalyzing(false);
    }
  }

  /* Demo handler */
  function handleDemo(sample: DemoSample) {
    if (sample.file_url) {
      toast.info(`Demo sample: ${sample.title}`);
    }
  }

  return (
    <Card className="border-zinc-800/60 bg-zinc-900/70 backdrop-blur-sm">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-semibold uppercase tracking-wider text-zinc-400">
            Upload Video
          </CardTitle>
          <div className="flex items-center gap-2">
            {/* <DemoSamplePicker filterType="video" onSelect={handleDemo} /> */}
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
        {/* Drop zone or preview */}
        {!meta ? (
          <FileDropzone
            accept={ACCEPT}
            maxSize={MAX_SIZE}
            icon={Video}
            title="Drag & drop a video file"
            subtitle="or click to browse"
            formatLabels={['MP4', 'AVI', 'MOV', 'WebM']}
            sizeLabel="≤ 50 MB · ≤ 60s"
            onFileAccepted={(f) => setFile(f)}
            disabled={isValidating}
          />
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-3"
          >
            {/* Video preview */}
            <VideoPreview
              objectUrl={meta.objectUrl}
              isAnalyzing={isAnalyzing}
              onRemove={handleReset}
            />

            {/* Frame progress during analysis */}
            {isAnalyzing && fakeProgress.total > 0 && (
              <FrameProgress
                framesAnalyzed={fakeProgress.done}
                totalFrames={fakeProgress.total}
              />
            )}

            {/* File meta */}
            <div className="flex items-center gap-2 rounded-lg border border-zinc-800 bg-zinc-800/40 px-3 py-2 text-xs text-zinc-400">
              <FileVideo className="h-3.5 w-3.5 shrink-0 text-rose-400" />
              <span className="truncate font-medium">{meta.name}</span>
              <span className="ml-auto shrink-0">
                {(meta.size / 1024 / 1024).toFixed(1)} MB
              </span>
              {meta.duration !== undefined && (
                <Badge
                  variant="outline"
                  className="ml-1 border-zinc-700 text-[10px] text-zinc-500"
                >
                  {meta.duration.toFixed(1)}s
                </Badge>
              )}
            </div>
          </motion.div>
        )}

        {/* Error */}
        {error && (
          <div className="flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-xs text-red-400">
            <AlertCircle className="h-3.5 w-3.5 shrink-0" />
            {error}
          </div>
        )}

        {/* Analyze button */}
        <Button
          disabled={!file || isAnalyzing || isValidating || !!error}
          onClick={handleAnalyze}
          className="w-full gap-2 bg-rose-600 text-white hover:bg-rose-500"
          data-testid="analyze-button"
        >
          {isAnalyzing ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Analyzing Video…
            </>
          ) : isValidating ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Validating…
            </>
          ) : (
            <>
              <Scan className="h-4 w-4" />
              Detect Deepfake
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
}