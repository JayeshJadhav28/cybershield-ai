"use client";

import { useState, useCallback } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowLeft,
  ArrowRight,
  Loader2,
  Mail,
  KeyRound,
  User,
} from "lucide-react";
import { toast } from "sonner";

import { useAuth } from "@/hooks/use-auth";
import { ApiError } from "@/lib/api";
import { emailSchema, otpSchema } from "@/lib/validators";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { OtpInput } from "./otp-input";
import { CountdownTimer } from "./countdown-timer";

type Step = "details" | "otp";

const signUpFormSchema = z.object({
  email: emailSchema,
  displayName: z
    .string()
    .min(2, "Name must be at least 2 characters")
    .max(100, "Name must be 100 characters or less"),
});
type SignUpFormData = z.infer<typeof signUpFormSchema>;

export function SignUpForm() {
  const { requestOtp, signup } = useAuth();

  const [step, setStep] = useState<Step>("details");
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [otpError, setOtpError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [canResend, setCanResend] = useState(false);
  const [resendRunning, setResendRunning] = useState(false);

  const form = useForm<SignUpFormData>({
    resolver: zodResolver(signUpFormSchema),
    defaultValues: { email: "", displayName: "" },
  });

  /* ── Step 1: Request OTP ── */
  const handleDetailsSubmit = useCallback(
    async (data: SignUpFormData) => {
      setIsLoading(true);
      try {
        const otpResponse = await requestOtp(data.email, "signup");
        setEmail(data.email);
        setStep("otp");
        setCanResend(false);
        setResendRunning(true);
        toast.success("OTP sent!", {
          description: otpResponse.message,
        });
        if (process.env.NODE_ENV === "development" && otpResponse.dev_otp) {
          console.info("DEV OTP:", otpResponse.dev_otp);
          toast.info(`DEV OTP: ${otpResponse.dev_otp}`);
        }
      } catch (err) {
        if (err instanceof ApiError) {
          if (err.status === 429) {
            toast.error("Too many requests", { description: err.message });
          } else {
            toast.error("Failed to send OTP", { description: err.message });
          }
        } else {
          toast.error("Something went wrong");
        }
      } finally {
        setIsLoading(false);
      }
    },
    [requestOtp]
  );

  /* ── Step 2: Verify OTP ── */
  const handleOtpSubmit = useCallback(async () => {
    const result = otpSchema.safeParse(otp);
    if (!result.success) {
      setOtpError(result.error.errors[0].message);
      return;
    }

    setOtpError("");
    setIsLoading(true);
    try {
      await signup(email, otp);
      toast.success("Account created!", {
        description: "Welcome to CyberShield AI.",
      });
    } catch (err) {
      if (err instanceof ApiError) {
        setOtpError(err.message);
        if (err.status !== 401) {
          toast.error("Verification failed", { description: err.message });
        }
      } else {
        toast.error("Something went wrong");
      }
      setOtp("");
    } finally {
      setIsLoading(false);
    }
  }, [email, otp, signup]);

  /* ── Resend OTP ── */
  const handleResend = useCallback(async () => {
    setIsLoading(true);
    try {
      const otpResponse = await requestOtp(email, "signup");
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

  const handleOtpChange = (value: string) => {
    setOtp(value);
    setOtpError("");
  };

  return (
    <AnimatePresence mode="wait">
      {step === "details" ? (
        <motion.div
          key="details-step"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.3 }}
        >
          <form
            onSubmit={form.handleSubmit(handleDetailsSubmit)}
            className="space-y-4"
          >
            {/* Name */}
            <div className="space-y-2">
              <Label htmlFor="displayName" className="text-sm">
                Full Name
              </Label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="displayName"
                  type="text"
                  placeholder="Your name"
                  autoComplete="name"
                  autoFocus
                  disabled={isLoading}
                  className="pl-10 h-11"
                  {...form.register("displayName")}
                />
              </div>
              {form.formState.errors.displayName && (
                <p className="text-xs text-destructive">
                  {form.formState.errors.displayName.message}
                </p>
              )}
            </div>

            {/* Email */}
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
              {isLoading ? "Sending OTP…" : "Create Account"}
            </Button>
          </form>

          <div className="mt-4 text-center">
            <p className="text-xs text-muted-foreground">
              We&apos;ll send a verification code to your email.
              <br />
              No password needed — ever.
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
          {/* Back */}
          <button
            type="button"
            onClick={() => {
              setStep("details");
              setOtp("");
              setOtpError("");
            }}
            className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            Back to details
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
            onChange={handleOtpChange}
            disabled={isLoading}
            error={!!otpError}
            autoFocus
          />

          {otpError && (
            <p className="text-xs text-destructive text-center">{otpError}</p>
          )}

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
            {isLoading ? "Verifying…" : "Verify & Create Account"}
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