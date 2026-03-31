"use client";

import { useState, useCallback } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, ArrowRight, Loader2, Mail, KeyRound } from "lucide-react";
import { toast } from "sonner";

import { useAuth } from "@/hooks/use-auth";
import { ApiError } from "@/lib/api";
import { emailSchema, otpSchema } from "@/lib/validators";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { OtpInput } from "./otp-input";
import { CountdownTimer } from "./countdown-timer";

type Step = "email" | "otp";

const emailFormSchema = z.object({ email: emailSchema });
type EmailFormData = z.infer<typeof emailFormSchema>;

export function SignInForm() {
  const { requestOtp, login } = useAuth();

  const [step, setStep] = useState<Step>("email");
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [otpError, setOtpError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [canResend, setCanResend] = useState(false);
  const [resendRunning, setResendRunning] = useState(false);

  const form = useForm<EmailFormData>({
    resolver: zodResolver(emailFormSchema),
    defaultValues: { email: "" },
  });

  /* ── Step 1: Request OTP ── */
  const handleEmailSubmit = useCallback(
    async (data: EmailFormData) => {
      setIsLoading(true);
      try {
        const otpResponse = await requestOtp(data.email, "login");
        setEmail(data.email);
        setStep("otp");
        setCanResend(false);
        setResendRunning(true);
        toast.success("OTP sent!", {
          description: otpResponse.message,
        });
        if (process.env.NODE_ENV === "development" && otpResponse.dev_otp) {
          // Helpful local fallback when backend logs are not visible in current terminal.
          console.info("DEV OTP:", otpResponse.dev_otp);
          toast.info(`DEV OTP: ${otpResponse.dev_otp}`);
        }
      } catch (err) {
        if (err instanceof ApiError) {
          if (err.status === 429) {
            toast.error("Too many requests", {
              description: err.message,
            });
          } else {
            toast.error("Failed to send OTP", {
              description: err.message,
            });
          }
        } else {
          toast.error("Something went wrong", {
            description: "Please try again.",
          });
        }
      } finally {
        setIsLoading(false);
      }
    },
    [requestOtp]
  );

  /* ── Step 2: Verify OTP ── */
  const handleOtpSubmit = useCallback(async () => {
    // Validate OTP format
    const result = otpSchema.safeParse(otp);
    if (!result.success) {
      setOtpError(result.error.errors[0].message);
      return;
    }

    setOtpError("");
    setIsLoading(true);
    try {
      await login(email, otp);
      toast.success("Welcome back!", {
        description: "You've been signed in successfully.",
      });
    } catch (err) {
      if (err instanceof ApiError) {
        setOtpError(err.message);
        if (err.status !== 401) {
          toast.error("Verification failed", {
            description: err.message,
          });
        }
      } else {
        toast.error("Something went wrong");
      }
      setOtp("");
    } finally {
      setIsLoading(false);
    }
  }, [email, otp, login]);

  /* ── Resend OTP ── */
  const handleResend = useCallback(async () => {
    setIsLoading(true);
    try {
      const otpResponse = await requestOtp(email, "login");
      setOtp("");
      setOtpError("");
      setCanResend(false);
      setResendRunning(true);
      toast.success("OTP resent!", {
        description: otpResponse.message,
      });
      if (process.env.NODE_ENV === "development" && otpResponse.dev_otp) {
        console.info("DEV OTP:", otpResponse.dev_otp);
        toast.info(`DEV OTP: ${otpResponse.dev_otp}`);
      }
    } catch (err) {
      if (err instanceof ApiError) {
        toast.error("Failed to resend", { description: err.message });
      }
    } finally {
      setIsLoading(false);
    }
  }, [email, requestOtp]);

  /* ── Auto-submit when 6 digits entered ── */
  const handleOtpChange = useCallback(
    (value: string) => {
      setOtp(value);
      setOtpError("");
      if (value.length === 6) {
        // Small delay so user sees the last digit fill in
        setTimeout(() => {
          const result = otpSchema.safeParse(value);
          if (result.success) {
            handleOtpSubmit();
          }
        }, 150);
      }
    },
    [handleOtpSubmit]
  );

  // Need to update handleOtpSubmit dependency — using direct approach instead
  const handleOtpChangeDirect = (value: string) => {
    setOtp(value);
    setOtpError("");
  };

  return (
    <AnimatePresence mode="wait">
      {step === "email" ? (
        <motion.div
          key="email-step"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.3 }}
        >
          <form
            onSubmit={form.handleSubmit(handleEmailSubmit)}
            className="space-y-4"
          >
            <div className="space-y-2">
              <Label htmlFor="email" className="text-sm">
                Email Address
              </Label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  autoComplete="email"
                  autoFocus
                  disabled={isLoading}
                  className="pl-10 h-11"
                  {...form.register("email")}
                />
              </div>
              {form.formState.errors.email && (
                <p className="text-xs text-destructive">
                  {form.formState.errors.email.message}
                </p>
              )}
            </div>

            <Button
              type="submit"
              className="w-full h-11 bg-primary hover:bg-primary/90 font-semibold"
              disabled={isLoading}
            >
              {isLoading ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <ArrowRight className="mr-2 h-4 w-4" />
              )}
              {isLoading ? "Sending OTP…" : "Continue with Email"}
            </Button>
          </form>

          <div className="mt-4 text-center">
            <p className="text-xs text-muted-foreground">
              We&apos;ll send a 6-digit code to your email.
              <br />
              No password needed.
            </p>
          </div>
        </motion.div>
      ) : (
        <motion.div
          key="otp-step"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 20 }}
          transition={{ duration: 0.3 }}
          className="space-y-5"
        >
          {/* Back button */}
          <button
            type="button"
            onClick={() => {
              setStep("email");
              setOtp("");
              setOtpError("");
            }}
            className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            Change email
          </button>

          <div className="text-center space-y-1">
            <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
              <KeyRound className="h-5 w-5 text-primary" />
            </div>
            <p className="text-sm text-muted-foreground mt-3">
              Enter the 6-digit code sent to
            </p>
            <p className="text-sm font-medium font-mono">{email}</p>
          </div>

          {/* OTP Input */}
          <OtpInput
            value={otp}
            onChange={handleOtpChangeDirect}
            disabled={isLoading}
            error={!!otpError}
            autoFocus
          />

          {otpError && (
            <p className="text-xs text-destructive text-center">{otpError}</p>
          )}

          {/* Verify button */}
          <Button
            onClick={handleOtpSubmit}
            className="w-full h-11 bg-primary hover:bg-primary/90 font-semibold"
            disabled={isLoading || otp.length < 6}
          >
            {isLoading ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <ArrowRight className="mr-2 h-4 w-4" />
            )}
            {isLoading ? "Verifying…" : "Verify & Sign In"}
          </Button>

          {/* Resend */}
          <div className="text-center text-xs text-muted-foreground">
            {canResend ? (
              <button
                type="button"
                onClick={handleResend}
                disabled={isLoading}
                className="text-primary hover:underline disabled:opacity-50"
              >
                Resend code
              </button>
            ) : (
              <span>
                Resend code in{" "}
                <CountdownTimer
                  seconds={60}
                  running={resendRunning}
                  onComplete={() => {
                    setCanResend(true);
                    setResendRunning(false);
                  }}
                />
              </span>
            )}
          </div>

        </motion.div>
      )}
    </AnimatePresence>
  );
}