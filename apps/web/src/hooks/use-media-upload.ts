'use client';

import { useState, useCallback, useRef, useEffect } from 'react';

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */
export interface MediaMeta {
  name: string;
  size: number;
  type: string;
  duration?: number;
  objectUrl: string;
}

export interface UseMediaUploadOptions {
  maxDuration?: number; // seconds — 0 = unlimited
  onDurationError?: (actual: number, max: number) => void;
}

export interface UseMediaUploadReturn {
  file: File | null;
  meta: MediaMeta | null;
  isValidating: boolean;
  error: string | null;
  setFile: (f: File | null) => void;
  reset: () => void;
}

/* ------------------------------------------------------------------ */
/*  Helper: extract duration from audio/video                          */
/* ------------------------------------------------------------------ */
function extractDuration(file: File): Promise<number> {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const isAudio = file.type.startsWith('audio');
    const el = isAudio
      ? new Audio()
      : document.createElement('video');

    el.preload = 'metadata';

    el.onloadedmetadata = () => {
      URL.revokeObjectURL(url);
      if (el.duration === Infinity || Number.isNaN(el.duration)) {
        resolve(0);
      } else {
        resolve(el.duration);
      }
    };

    el.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error('Cannot read media metadata'));
    };

    el.src = url;
  });
}

/* ------------------------------------------------------------------ */
/*  Hook                                                               */
/* ------------------------------------------------------------------ */
export function useMediaUpload(
  opts: UseMediaUploadOptions = {},
): UseMediaUploadReturn {
  const { maxDuration = 0, onDurationError } = opts;

  const [file, setFileState] = useState<File | null>(null);
  const [meta, setMeta] = useState<MediaMeta | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const objectUrlRef = useRef<string | null>(null);

  /* Cleanup object URL on unmount */
  useEffect(() => {
    return () => {
      if (objectUrlRef.current) URL.revokeObjectURL(objectUrlRef.current);
    };
  }, []);

  const setFile = useCallback(
    async (f: File | null) => {
      // Cleanup previous
      if (objectUrlRef.current) {
        URL.revokeObjectURL(objectUrlRef.current);
        objectUrlRef.current = null;
      }

      if (!f) {
        setFileState(null);
        setMeta(null);
        setError(null);
        return;
      }

      setIsValidating(true);
      setError(null);
      setFileState(f);

      try {
        let duration = 0;

        if (
          f.type.startsWith('audio') ||
          f.type.startsWith('video')
        ) {
          duration = await extractDuration(f);

          if (maxDuration > 0 && duration > maxDuration) {
            const msg = `File exceeds maximum duration of ${maxDuration}s (actual: ${duration.toFixed(1)}s)`;
            setError(msg);
            onDurationError?.(duration, maxDuration);
            setFileState(null);
            setMeta(null);
            setIsValidating(false);
            return;
          }
        }

        const objectUrl = URL.createObjectURL(f);
        objectUrlRef.current = objectUrl;

        setMeta({
          name: f.name,
          size: f.size,
          type: f.type,
          duration: duration || undefined,
          objectUrl,
        });
      } catch (err: any) {
        setError(err?.message ?? 'Failed to read file metadata');
        setFileState(null);
        setMeta(null);
      } finally {
        setIsValidating(false);
      }
    },
    [maxDuration, onDurationError],
  );

  const reset = useCallback(() => {
    setFile(null);
  }, [setFile]);

  return { file, meta, isValidating, error, setFile, reset };
}