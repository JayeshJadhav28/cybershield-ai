'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { PageHeader } from '@/components/shared/page-header';
import { LoadingSpinner } from '@/components/shared/loading-spinner';
import {
  MessageSquare,
  ArrowRight,
  Phone,
  Mail,
  Clock,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';
import { api } from '@/lib/api';

interface ScenarioSummary {
  id: string;
  title: string;
  description: string;
  category: string;
  scenario_type: string;
  estimated_time_minutes?: number;
}

const TYPE_ICONS: Record<string, React.ElementType> = {
  chat: MessageSquare,
  call: Phone,
  email: Mail,
};

const CATEGORY_COLORS: Record<string, string> = {
  kyc_otp: 'border-amber-500/30 text-amber-400',
  phishing: 'border-red-500/30 text-red-400',
  deepfake: 'border-purple-500/30 text-purple-400',
  upi_qr: 'border-blue-500/30 text-blue-400',
};

/* Fallback scenarios if API is unreachable */
const FALLBACK_SCENARIOS: ScenarioSummary[] = [
  {
    id: 'fallback-1',
    title: 'The Fake KYC Call',
    description:
      'A caller claims to be from your bank and says your KYC is expiring. Navigate this scenario to learn the right responses.',
    category: 'kyc_otp',
    scenario_type: 'chat',
    estimated_time_minutes: 5,
  },
  {
    id: 'fallback-2',
    title: 'Phishing Email at Work',
    description:
      'You receive an email at your office asking you to reset your corporate credentials. Can you spot the red flags?',
    category: 'phishing',
    scenario_type: 'email',
    estimated_time_minutes: 4,
  },
];

export default function ScenariosPage() {
  const [scenarios, setScenarios] = useState<ScenarioSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    api
      .request<{ scenarios: ScenarioSummary[] }>('/awareness/scenarios')
      .then((res) => {
        if (!cancelled) setScenarios(res.scenarios ?? []);
      })
      .catch(() => {
        if (!cancelled) setScenarios(FALLBACK_SCENARIOS);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <LoadingSpinner label="Loading scenarios…" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Scenario Simulations"
        description="Experience realistic cyber-scam scenarios and practise safe responses."
        icon={MessageSquare}
      />

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {scenarios.map((s, i) => {
          const TypeIcon = TYPE_ICONS[s.scenario_type] ?? MessageSquare;
          return (
            <motion.div
              key={s.id}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: i * 0.1 }}
            >
              <Card className="group h-full border-zinc-800/60 bg-zinc-900/70 backdrop-blur-sm transition-all hover:border-zinc-700">
                <CardContent className="flex h-full flex-col p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-zinc-800/80">
                      <TypeIcon className="h-5 w-5 text-cyan-400" />
                    </div>
                    <div className="flex gap-1.5">
                      <Badge
                        variant="outline"
                        className={cn(
                          'text-[10px]',
                          CATEGORY_COLORS[s.category] ??
                            'border-zinc-700 text-zinc-500',
                        )}
                      >
                        {s.category.replace(/_/g, ' ')}
                      </Badge>
                    </div>
                  </div>

                  <h3 className="mt-4 text-base font-semibold text-zinc-200">
                    {s.title}
                  </h3>
                  <p className="mt-2 flex-1 text-xs leading-relaxed text-zinc-500">
                    {s.description}
                  </p>

                  <div className="mt-4 flex items-center justify-between">
                    {s.estimated_time_minutes && (
                      <span className="flex items-center gap-1 text-[11px] text-zinc-500">
                        <Clock className="h-3 w-3" />
                        ~{s.estimated_time_minutes} min
                      </span>
                    )}
                    <Link href={`/awareness/scenarios/${s.id}`}>
                      <Button
                        size="sm"
                        className="gap-1.5 bg-cyan-600 text-white hover:bg-cyan-500"
                      >
                        Play
                        <ArrowRight className="h-3.5 w-3.5" />
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}