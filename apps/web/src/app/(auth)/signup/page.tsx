import Link from "next/link";
import { AuthCard } from "@/components/auth/auth-card";
import { SignUpForm } from "@/components/auth/sign-up-form";

export const metadata = { title: "Sign Up — CyberShield AI" };

export default function SignUpPage() {
  return (
    <AuthCard
      title="Create Account"
      description="Join CyberShield AI — protect yourself from cyber threats"
      footer={
        <>
          Already have an account?{" "}
          <Link
            href="/signin"
            className="text-cyan-400 hover:text-cyan-300 font-medium transition-colors"
          >
            Sign in
          </Link>
        </>
      }
    >
      <SignUpForm />
    </AuthCard>
  );
}