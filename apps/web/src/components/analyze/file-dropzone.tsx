'use client';

import { useCallback } from 'react';
import { useDropzone, type Accept, type FileRejection } from 'react-dropzone';
import { Badge } from '@/components/ui/badge';
import { Upload } from 'lucide-react';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

/* ------------------------------------------------------------------ */
/*  Props                                                              */
/* ------------------------------------------------------------------ */
export interface FileDropzoneProps {
  accept: Accept;
  maxSize: number; // bytes
  icon?: React.ElementType;
  title?: string;
  subtitle?: string;
  formatLabels?: string[];
  sizeLabel?: string;
  onFileAccepted: (file: File) => void;
  disabled?: boolean;
  className?: string;
  children?: React.ReactNode;
}

/* ------------------------------------------------------------------ */
/*  Component                                                          */
/* ------------------------------------------------------------------ */
export function FileDropzone({
  accept,
  maxSize,
  icon: Icon = Upload,
  title = 'Drag & drop a file',
  subtitle = 'or click to browse',
  formatLabels = [],
  sizeLabel,
  onFileAccepted,
  disabled = false,
  className,
  children,
}: FileDropzoneProps) {
  const onDrop = useCallback(
    (accepted: File[], rejected: FileRejection[]) => {
      if (rejected.length) {
        const err = rejected[0].errors?.[0];
        if (err?.code === 'file-too-large') {
          toast.error(`File exceeds maximum size of ${Math.round(maxSize / 1024 / 1024)} MB`);
        } else if (err?.code === 'file-invalid-type') {
          toast.error('Unsupported file format');
        } else {
          toast.error(err?.message ?? 'File rejected');
        }
        return;
      }
      if (accepted[0]) onFileAccepted(accepted[0]);
    },
    [maxSize, onFileAccepted],
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    maxSize,
    multiple: false,
    disabled,
  });

  return (
    <div
      {...getRootProps()}
      className={cn(
        'relative flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-8 transition-all duration-200',
        isDragActive
          ? 'border-cyan-500/60 bg-cyan-500/5'
          : 'border-zinc-700/60 bg-zinc-800/20 hover:border-zinc-600 hover:bg-zinc-800/40',
        disabled && 'pointer-events-none opacity-50',
        className,
      )}
    >
      <input {...getInputProps()} />

      {children || (
        <div className="flex flex-col items-center gap-3 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-zinc-800/80">
            {isDragActive ? (
              <Upload className="h-7 w-7 animate-bounce text-cyan-400" />
            ) : (
              <Icon className="h-7 w-7 text-zinc-400" />
            )}
          </div>
          <div>
            <p className="text-sm font-medium text-zinc-300">
              {isDragActive ? 'Drop the file here' : title}
            </p>
            <p className="mt-1 text-xs text-zinc-500">{subtitle}</p>
          </div>
          {(formatLabels.length > 0 || sizeLabel) && (
            <div className="flex flex-wrap justify-center gap-1.5">
              {formatLabels.map((f) => (
                <Badge
                  key={f}
                  variant="outline"
                  className="border-zinc-700 text-[10px] text-zinc-500"
                >
                  {f}
                </Badge>
              ))}
              {sizeLabel && (
                <Badge
                  variant="outline"
                  className="border-zinc-700 text-[10px] text-zinc-500"
                >
                  {sizeLabel}
                </Badge>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}