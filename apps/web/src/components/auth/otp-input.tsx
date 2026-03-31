"use client";

import {
  useRef,
  useState,
  useCallback,
  useEffect,
  type KeyboardEvent,
  type ClipboardEvent,
} from "react";
import { cn } from "@/lib/utils";

interface OtpInputProps {
  length?: number;
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  autoFocus?: boolean;
  error?: boolean;
}

export function OtpInput({
  length = 6,
  value,
  onChange,
  disabled = false,
  autoFocus = true,
  error = false,
}: OtpInputProps) {
  const inputsRef = useRef<(HTMLInputElement | null)[]>([]);
  const [activeIndex, setActiveIndex] = useState(0);

  // Split value into array
  const digits = value.split("").concat(Array(length).fill("")).slice(0, length);

  // Auto-focus first input on mount
  useEffect(() => {
    if (autoFocus && inputsRef.current[0]) {
      inputsRef.current[0].focus();
    }
  }, [autoFocus]);

  const focusInput = useCallback(
    (index: number) => {
      const clamped = Math.max(0, Math.min(index, length - 1));
      inputsRef.current[clamped]?.focus();
      setActiveIndex(clamped);
    },
    [length]
  );

  const handleChange = useCallback(
    (index: number, char: string) => {
      if (!/^\d$/.test(char) && char !== "") return;

      const newDigits = [...digits];
      newDigits[index] = char;
      const newValue = newDigits.join("").slice(0, length);
      onChange(newValue);

      if (char && index < length - 1) {
        focusInput(index + 1);
      }
    },
    [digits, length, onChange, focusInput]
  );

  const handleKeyDown = useCallback(
    (index: number, e: KeyboardEvent<HTMLInputElement>) => {
      if (e.key === "Backspace") {
        e.preventDefault();
        if (digits[index]) {
          handleChange(index, "");
        } else if (index > 0) {
          focusInput(index - 1);
          handleChange(index - 1, "");
        }
      } else if (e.key === "ArrowLeft" && index > 0) {
        e.preventDefault();
        focusInput(index - 1);
      } else if (e.key === "ArrowRight" && index < length - 1) {
        e.preventDefault();
        focusInput(index + 1);
      } else if (e.key === "Delete") {
        e.preventDefault();
        handleChange(index, "");
      }
    },
    [digits, length, focusInput, handleChange]
  );

  const handlePaste = useCallback(
    (e: ClipboardEvent<HTMLInputElement>) => {
      e.preventDefault();
      const pasted = e.clipboardData
        .getData("text/plain")
        .replace(/\D/g, "")
        .slice(0, length);

      if (pasted.length > 0) {
        onChange(pasted);
        focusInput(Math.min(pasted.length, length - 1));
      }
    },
    [length, onChange, focusInput]
  );

  return (
    <div className="flex items-center justify-center gap-2 sm:gap-3">
      {Array.from({ length }).map((_, idx) => (
        <input
          key={idx}
          ref={(el) => {
            inputsRef.current[idx] = el;
          }}
          type="text"
          inputMode="numeric"
          autoComplete="one-time-code"
          maxLength={1}
          value={digits[idx] || ""}
          disabled={disabled}
          aria-label={`Digit ${idx + 1} of ${length}`}
          className={cn(
            "h-12 w-10 sm:h-14 sm:w-12 rounded-lg border-2 bg-background text-center text-lg sm:text-xl font-mono font-bold",
            "transition-all duration-200 outline-none",
            "focus:ring-2 focus:ring-primary/40 focus:border-primary",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            error
              ? "border-destructive/60 focus:border-destructive focus:ring-destructive/40"
              : digits[idx]
                ? "border-primary/50"
                : "border-border",
            activeIndex === idx && !disabled && "border-primary shadow-glow-cyan"
          )}
          onChange={(e) => {
            const char = e.target.value.slice(-1);
            handleChange(idx, char);
          }}
          onKeyDown={(e) => handleKeyDown(idx, e)}
          onPaste={handlePaste}
          onFocus={() => setActiveIndex(idx)}
        />
      ))}
    </div>
  );
}