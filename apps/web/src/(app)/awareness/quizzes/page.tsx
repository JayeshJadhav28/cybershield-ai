'use client';

import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { PageHeader } from '@/components/shared/page-header';
import {
  GraduationCap,
  ShieldAlert,
  QrCode,
  KeyRound,
  ArrowRight,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';

const CATEGORIES = [
  {
    slug: 'deepfake',
    title: 'Deepfake Detection',
    description:
      'Learn to identify AI-generated audio and video. Understand how deepfakes are created and the telltale signs.',
    icon: ShieldAlert,
    iconColor: 'text-purple-400',
    iconBg: 'bg-purple-500/10',
    gradient: 'from-purple-500/20 to-purple-600/5',
    questions: 10,
    difficulty: 'Medium',
  },
  {
    slug: 'upi_qr',
    title: 'UPI & QR Scams',
    description:
      'Spot fraudulent QR codes, fake UPI payment requests, and merchant scams common across India.',
    icon: QrCode,
    iconColor: 'text-blue-400',
    iconBg: 'bg-blue-500/10',
    gradient: 'from-blue-500/20 to-blue-600/5',
    questions: 10,
    difficulty: 'Easy',
  },
  {
    slug: 'phishing',
    title: 'KYC & OTP Phishing',
    description:
      'Recognize phishing emails, fake KYC update calls, and OTP scams targeting bank customers.',
    icon: KeyRound,
    iconColor: 'text-amber-400',
    iconBg: 'bg-amber-500/10',
    gradient: 'from-amber-500/20 to-amber-600/5',
    questions: 10,
    difficulty: 'Easy–Medium',
  },
] as const;

export default function QuizzesPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Cyber Awareness Quizzes"
        description="Test your knowledge and earn badges. Each quiz has 10 questions with immediate feedback."
        icon={GraduationCap}
      />

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {CATEGORIES.map((cat, i) => {
          const Icon = cat.icon;
          return (
            <motion.div
              key={cat.slug}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: i * 0.1 }}
            >
              <Card className="group h-full border-zinc-800/60 bg-zinc-900/70 backdrop-blur-sm transition-all hover:border-zinc-700">
                <div
                  className={cn(
                    'pointer-events-none absolute inset-0 rounded-xl bg-gradient-to-br opacity-0 transition-opacity group-hover:opacity-100',
                    cat.gradient,
                  )}
                />
                <CardContent className="relative flex h-full flex-col p-6">
                  <div
                    className={cn(
                      'flex h-12 w-12 items-center justify-center rounded-xl',
                      cat.iconBg,
                    )}
                  >
                    <Icon className={cn('h-6 w-6', cat.iconColor)} />
                  </div>

                  <h3 className="mt-4 text-base font-semibold text-zinc-200">
                    {cat.title}
                  </h3>
                  <p className="mt-2 flex-1 text-xs leading-relaxed text-zinc-500">
                    {cat.description}
                  </p>

                  <div className="mt-4 flex items-center gap-2">
                    <Badge
                      variant="outline"
                      className="border-zinc-700 text-[10px] text-zinc-500"
                    >
                      {cat.questions} Questions
                    </Badge>
                    <Badge
                      variant="outline"
                      className="border-zinc-700 text-[10px] text-zinc-500"
                    >
                      {cat.difficulty}
                    </Badge>
                  </div>

                  <Link href={`/awareness/quizzes/${cat.slug}`} className="mt-4">
                    <Button className="w-full gap-1.5 bg-cyan-600 text-white hover:bg-cyan-500">
                      Start Quiz
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>

      {/* Badge thresholds info */}
      <div className="rounded-lg border border-zinc-800/40 bg-zinc-900/40 p-4 text-center text-xs text-zinc-500">
        🥉 Bronze ≥ 50% · 🥈 Silver ≥ 70% · 🥇 Gold ≥ 90%
      </div>
    </div>
  );
}