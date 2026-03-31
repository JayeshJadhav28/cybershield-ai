import Link from "next/link";
import { AuthCard } from "@/components/auth/auth-card";
import { SignInForm } from "@/components/auth/sign-in-form";

export const metadata = { title: "Sign In — CyberShield AI" };

export default function SignInPage() {
  return (
    <AuthCard
      title="Welcome Back"
      description="Sign in to your CyberShield AI account"
      footer={
        <>
          Don&apos;t have an account?{" "}
          <Link
            href="/signup"
            className="text-cyan-400 hover:text-cyan-300 font-medium transition-colors"
          >
            Create one
          </Link>
        </>
      }
    >
      <SignInForm />
    </AuthCard>
  );
}