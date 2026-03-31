'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Mic,
  Loader2,
  Scan,
  RotateCcw,
  Play,
  Pause,
  FileAudio,
  AlertCircle,
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
  'audio/wav': ['.wav'],
  'audio/mpeg': ['.mp3'],
  'audio/ogg': ['.ogg'],
  'audio/x-m4a': ['.m4a'],
  'audio/mp4': ['.m4a'],
  'audio/flac': ['.flac'],
};
const MAX_SIZE = 10 * 1024 * 1024; // 10 MB
const MAX_DURATION = 30; // seconds

/* ------------------------------------------------------------------ */
/*  Waveform visualiser                                                */
/* ------------------------------------------------------------------ */
function WaveformVisualiser({
  objectUrl,
  isAnalyzing,
}: {
  objectUrl: string;
  isAnalyzing: boolean;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const animRef = useRef<number>(0);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioCtx, setAudioCtx] = useState<AudioContext | null>(null);
  const sourceCreated = useRef(false);

  /* Draw static bars when not playing */
  const drawStatic = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const { width, height } = canvas;
    ctx.clearRect(0, 0, width, height);

    const bars = 60;
    const barW = width / bars - 1;

    for (let i = 0; i < bars; i++) {
      const h = isAnalyzing
        ? Math.random() * height * 0.8 + height * 0.1
        : Math.sin(i * 0.3) * height * 0.25 + height * 0.35;

      ctx.fillStyle = isAnalyzing
        ? `rgba(6, 182, 212, ${0.4 + Math.random() * 0.4})`
        : 'rgba(113, 113, 122, 0.4)';

      ctx.fillRect(
        i * (barW + 1),
        (height - h) / 2,
        barW,
        h,
      );
    }
  }, [isAnalyzing]);

  /* Animate while analyzing (no audio playback) */
  useEffect(() => {
    if (!isAnalyzing) return;

    let running = true;
    const tick = () => {
      if (!running) return;
      drawStatic();
      animRef.current = requestAnimationFrame(tick);
    };
    tick();

    return () => {
      running = false;
      cancelAnimationFrame(animRef.current);
    };
  }, [isAnalyzing, drawStatic]);

  /* Draw static waveform on mount */
  useEffect(() => {
    drawStatic();
  }, [drawStatic]);

  /* Live visualise while playing */
  const drawLive = useCallback(() => {
    const canvas = canvasRef.current;
    const analyser = analyserRef.current;
    if (!canvas || !analyser) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const bufLen = analyser.frequencyBinCount;
    const data = new Uint8Array(bufLen);

    const tick = () => {
      analyser.getByteFrequencyData(data);
      const { width, height } = canvas;
      ctx.clearRect(0, 0, width, height);

      const bars = 60;
      const step = Math.floor(bufLen / bars);
      const barW = width / bars - 1;

      for (let i = 0; i < bars; i++) {
        const val = data[i * step] / 255;
        const h = val * height * 0.85 + 2;

        ctx.fillStyle = `rgba(6, 182, 212, ${0.3 + val * 0.7})`;
        ctx.fillRect(
          i * (barW + 1),
          (height - h) / 2,
          barW,
          h,
        );
      }

      animRef.current = requestAnimationFrame(tick);
    };
    tick();
  }, []);

  /* Play / pause toggle */
  function togglePlay() {
    if (!audioRef.current) {
      const audio = new Audio(objectUrl);
      audioRef.current = audio;

      audio.onended = () => {
        setIsPlaying(false);
        cancelAnimationFrame(animRef.current);
        drawStatic();
      };
    }

    const audio = audioRef.current;

    if (isPlaying) {
      audio.pause();
      setIsPlaying(false);
      cancelAnimationFrame(animRef.current);
      drawStatic();
    } else {
      // Create context + analyser on first play (needs user gesture)
      if (!audioCtx) {
        const ctx = new AudioContext();
        const analyser = ctx.createAnalyser();
        analyser.fftSize = 256;

        if (!sourceCreated.current) {
          const source = ctx.createMediaElementSource(audio);
          source.connect(analyser);
          analyser.connect(ctx.destination);
          sourceCreated.current = true;
        }

        analyserRef.current = analyser;
        setAudioCtx(ctx);
      }

      audio.play();
      setIsPlaying(true);
      drawLive();
    }
  }

  /* Cleanup */
  useEffect(() => {
    return () => {
      cancelAnimationFrame(animRef.current);
      audioRef.current?.pause();
      audioCtx?.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="space-y-3">
      <div className="relative overflow-hidden rounded-lg border border-zinc-800 bg-zinc-950/60 p-2">
        <canvas
          ref={canvasRef}
          width={500}
          height={80}
          className="h-20 w-full"
        />
      </div>

      {!isAnalyzing && (
        <Button
          variant="outline"
          size="sm"
          onClick={togglePlay}
          className="gap-1.5 border-zinc-700 text-xs text-zinc-400 hover:text-zinc-200"
          type="button"
        >
          {isPlaying ? (
            <>
              <Pause className="h-3 w-3" />
              Pause
            </>
          ) : (
            <>
              <Play className="h-3 w-3" />
              Preview
            </>
          )}
        </Button>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Props                                                              */
/* ------------------------------------------------------------------ */
interface AudioUploadProps {
  onResult: (result: AnalysisResult) => void;
  onReset: () => void;
}

/* ------------------------------------------------------------------ */
/*  Exported component                                                 */
/* ------------------------------------------------------------------ */
export function AudioUpload({ onResult, onReset }: AudioUploadProps) {
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const { file, meta, isValidating, error, setFile, reset } =
    useMediaUpload({
      maxDuration: MAX_DURATION,
      onDurationError: (actual, max) =>
        toast.error(
          `Audio exceeds maximum duration of ${max}s (actual: ${actual.toFixed(1)}s). Please upload a shorter clip.`,
        ),
    });

  function handleReset() {
    reset();
    onReset();
  }

  async function handleAnalyze() {
    if (!file) return;
    setIsAnalyzing(true);
    try {
      const result = await api.analyzeAudio(file);
      onResult(result as AnalysisResult);
    } catch (err: any) {
      toast.error(err?.message ?? 'Audio analysis failed.');
    } finally {
      setIsAnalyzing(false);
    }
  }

  /* Demo handler */
  function handleDemo(sample: DemoSample) {
    if (sample.file_url) {
      toast.info(`Demo sample: ${sample.title} — would fetch ${sample.file_url}`);
    }
  }

  return (
    <Card className="border-zinc-800/60 bg-zinc-900/70 backdrop-blur-sm">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-semibold uppercase tracking-wider text-zinc-400">
            Upload Audio
          </CardTitle>
          <div className="flex items-center gap-2">
              {/* <DemoSamplePicker filterType="audio" onSelect={handleDemo} /> */}
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
            icon={Mic}
            title="Drag & drop an audio file"
            subtitle="or click to browse"
            formatLabels={['WAV', 'MP3', 'OGG', 'M4A', 'FLAC']}
            sizeLabel="≤ 10 MB · ≤ 30s"
            onFileAccepted={(f) => setFile(f)}
            disabled={isValidating}
          />
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-3"
          >
            {/* Waveform */}
            <WaveformVisualiser
              objectUrl={meta.objectUrl}
              isAnalyzing={isAnalyzing}
            />

            {/* File meta */}
            <div className="flex items-center gap-2 rounded-lg border border-zinc-800 bg-zinc-800/40 px-3 py-2 text-xs text-zinc-400">
              <FileAudio className="h-3.5 w-3.5 shrink-0 text-purple-400" />
              <span className="truncate font-medium">{meta.name}</span>
              <span className="ml-auto shrink-0">
                {(meta.size / 1024).toFixed(0)} KB
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
          className="w-full gap-2 bg-purple-600 text-white hover:bg-purple-500"
          data-testid="analyze-button"
        >
          {isAnalyzing ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Analyzing Audio…
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