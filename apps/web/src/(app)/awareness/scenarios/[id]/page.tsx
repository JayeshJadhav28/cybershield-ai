'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ScenarioChat, type Scenario } from '@/components/awareness/scenario-chat';
import { PageHeader } from '@/components/shared/page-header';
import { LoadingSpinner } from '@/components/shared/loading-spinner';
import { Button } from '@/components/ui/button';
import { MessageSquare, ArrowLeft } from 'lucide-react';
import { api } from '@/lib/api';

/* Fallback scenario data for when API is offline */
const FALLBACK: Scenario = {
  id: 'fallback-1',
  title: 'The Fake KYC Call',
  steps: [
    {
      step: 1,
      role: 'caller',
      message:
        'Hello, this is Rajesh from SBI customer care. We\'ve noticed your KYC documents have expired. Your account will be frozen in 24 hours if not updated.',
      type: 'message',
    },
    {
      step: 2,
      type: 'choice',
      prompt: 'What do you do?',
      options: [
        'Ask them to send you an OTP to verify your identity',
        'Tell them you\'ll visit the branch directly to update KYC',
        'Share your Aadhaar number and PAN to update KYC quickly',
        'Hang up and call the official SBI helpline to verify',
      ],
      correct_index: 3,
      feedback: {
        '0': '❌ Never ask for or share OTPs over phone calls. Banks send OTPs only for transactions you initiate.',
        '1': '⚠️ Visiting the branch is safe, but the best immediate action is to verify the call through official channels first.',
        '2': '❌ Never share personal documents over phone. This is exactly what scammers want.',
        '3': '✅ Correct! Always hang up and call the bank\'s official helpline number to verify any such claims.',
      },
    },
    {
      step: 3,
      role: 'caller',
      message:
        'Sir, if you don\'t update now, your account will be permanently closed. I\'m calling from the official department.',
      type: 'message',
    },
    {
      step: 4,
      type: 'choice',
      prompt: 'The caller is pressuring you. What\'s your next move?',
      options: [
        'Give in and share your details to be safe',
        'Stay firm, hang up, and report the number at cybercrime.gov.in',
        'Ask for their employee ID to verify',
        'Put them on hold while you check with a friend',
      ],
      correct_index: 1,
      feedback: {
        '0': '❌ Scammers thrive on urgency. Never give in to pressure tactics.',
        '1': '✅ Perfect! You stayed firm and know to report at cybercrime.gov.in or call 1930.',
        '2': '⚠️ Scammers can give fake IDs. Independently verifying via official channels is better.',
        '3': '⚠️ Checking is good, but the best action is to hang up immediately and verify independently.',
      },
    },
  ],
};

export default function ActiveScenarioPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [scenario, setScenario] = useState<Scenario | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    api
      .request<Scenario>(`/awareness/scenarios/${id}`)
      .then((res) => {
        if (!cancelled) setScenario(res);
      })
      .catch(() => {
        /* Offline fallback */
        if (!cancelled) setScenario(FALLBACK);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, [id]);

  if (loading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <LoadingSpinner label="Loading scenario…" />
      </div>
    );
  }

  if (!scenario) {
    return (
      <div className="space-y-4">
        <PageHeader title="Scenario Not Found" icon={MessageSquare} />
        <Button
          variant="outline"
          onClick={() => router.push('/awareness/scenarios')}
          className="gap-1.5"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Scenarios
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push('/awareness/scenarios')}
          className="gap-1 text-zinc-400 hover:text-zinc-200"
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </Button>
      </div>

      <PageHeader
        title={scenario.title}
        icon={MessageSquare}
      />

      <ScenarioChat
        scenario={scenario}
        onComplete={() => router.push('/awareness/scenarios')}
      />
    </div>
  );
}