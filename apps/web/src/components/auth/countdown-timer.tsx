"use client";

import { useEffect, useState, useCallback } from "react";

interface CountdownTimerProps {
  seconds: number;
  onComplete: () => void;
  running: boolean;
}

export function CountdownTimer({
  seconds,
  onComplete,
  running,
}: CountdownTimerProps) {
  const [remaining, setRemaining] = useState(seconds);

  useEffect(() => {
    if (!running) {
      setRemaining(seconds);
      return;
    }

    setRemaining(seconds);

    const interval = setInterval(() => {
      setRemaining((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          onComplete();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [seconds, running, onComplete]);

  if (!running || remaining <= 0) return null;

  const mins = Math.floor(remaining / 60);
  const secs = remaining % 60;

  return (
    <span className="tabular-nums text-muted-foreground">
      {mins > 0 && `${mins}:`}
      {secs.toString().padStart(mins > 0 ? 2 : 1, "0")}s
    </span>
  );
}