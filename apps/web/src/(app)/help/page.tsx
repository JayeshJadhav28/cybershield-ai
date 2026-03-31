'use client';

import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { PageHeader } from '@/components/shared/page-header';
import {
  HelpCircle,
  ChevronDown,
  ChevronUp,
  Phone,
  Globe,
  Shield,
  Mail,
  ExternalLink,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

/* ------------------------------------------------------------------ */
/*  FAQ data                                                           */
/* ------------------------------------------------------------------ */
const FAQS = [
  {
    q: 'What is CyberShield AI?',
    a: 'CyberShield AI is an India-first, multi-modal AI platform that detects deepfake audio/video and phishing attempts (email, URL, QR) in real time, provides explainable risk scores, and includes a gamified cyber-awareness training hub.',
  },
  {
    q: 'Is my uploaded data stored permanently?',
    a: 'No. Uploaded media files (audio, video, QR images) are processed temporarily and auto-deleted after analysis. Only the analysis results and risk scores are stored for authenticated users — never the original content.',
  },
  {
    q: 'Can I use CyberShield AI without creating an account?',
    a: 'Yes. Email, URL, QR, audio, and video analyses all work without login. However, creating a free account lets you save analysis history, track quiz progress, and earn badges.',
  },
  {
    q: 'How accurate are the detection results?',
    a: 'Our phishing detection targets ≥90% precision and ≥85% recall. Deepfake audio targets AUC-ROC ≥0.85 and video ≥0.80. Results should be treated as risk indicators — always verify independently before acting.',
  },
  {
    q: 'What file formats and sizes are supported?',
    a: 'Email: text input. URL: text input. QR: PNG/JPG/WebP ≤5MB. Audio: WAV/MP3/OGG/M4A/FLAC ≤10MB, ≤30s. Video: MP4/AVI/MOV/WebM ≤50MB, ≤60s.',
  },
  {
    q: 'How does the scoring engine work?',
    a: 'Each analyzer produces a probability score. The scoring engine applies configurable weights, adds rule-based adjustments (blocklisted domains, urgency language, etc.), and maps the final 0-100 score to Safe (<30), Suspicious (30-69), or Dangerous (≥70).',
  },
  {
    q: 'What are the quiz badges?',
    a: 'Earn Bronze (≥50%), Silver (≥70%), or Gold (≥90%) badges per quiz category. Badges are visible in your profile and quiz history.',
  },
  {
    q: 'Where can I report cyber fraud?',
    a: 'Report cyber crimes at cybercrime.gov.in or call the national helpline 1930. These services are available 24x7 for immediate assistance.',
  },
];

/* ------------------------------------------------------------------ */
/*  FAQ accordion item                                                 */
/* ------------------------------------------------------------------ */
function FaqItem({ q, a }: { q: string; a: string }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border-b border-zinc-800/60 last:border-0">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between gap-4 py-4 text-left"
      >
        <span className="text-sm font-medium text-zinc-200">{q}</span>
        {open ? (
          <ChevronUp className="h-4 w-4 shrink-0 text-zinc-500" />
        ) : (
          <ChevronDown className="h-4 w-4 shrink-0 text-zinc-500" />
        )}
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            style={{ overflow: 'hidden' }}
          >
            <p className="pb-4 text-sm leading-relaxed text-zinc-400">{a}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Helpline card                                                      */
/* ------------------------------------------------------------------ */
const HELPLINES = [
  {
    icon: Phone,
    title: 'Cyber Crime Helpline',
    value: '1930',
    href: 'tel:1930',
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10',
    desc: '24x7 helpline for financial cyber fraud',
  },
  {
    icon: Globe,
    title: 'National Cyber Crime Portal',
    value: 'cybercrime.gov.in',
    href: 'https://cybercrime.gov.in',
    color: 'text-cyan-400',
    bg: 'bg-cyan-500/10',
    desc: 'Report all types of cyber crimes online',
  },
  {
    icon: Shield,
    title: 'CERT-In',
    value: 'cert-in.org.in',
    href: 'https://www.cert-in.org.in',
    color: 'text-blue-400',
    bg: 'bg-blue-500/10',
    desc: 'Security advisories and incident response',
  },
  {
    icon: Mail,
    title: 'Contact Us',
    value: 'support@cybershield.ai',
    href: 'mailto:support@cybershield.ai',
    color: 'text-purple-400',
    bg: 'bg-purple-500/10',
    desc: 'Questions about CyberShield AI',
  },
];

/* ------------------------------------------------------------------ */
/*  Page                                                               */
/* ------------------------------------------------------------------ */
export default function HelpPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <PageHeader
        title="Help & Support"
        description="Frequently asked questions and emergency helpline contacts."
        icon={HelpCircle}
      />

      {/* Helpline cards */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {HELPLINES.map((h) => (
          <a key={h.title} href={h.href} target="_blank" rel="noopener noreferrer">
            <Card className="group h-full border-zinc-800/60 bg-zinc-900/70 transition-all hover:border-zinc-700 hover:bg-zinc-900/90">
              <CardContent className="flex items-start gap-3 p-5">
                <div className={cn('flex h-10 w-10 shrink-0 items-center justify-center rounded-xl', h.bg)}>
                  <h.icon className={cn('h-5 w-5', h.color)} />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-semibold text-zinc-200 group-hover:text-white">
                    {h.title}
                  </p>
                  <p className="mt-0.5 font-mono text-xs text-cyan-400">{h.value}</p>
                  <p className="mt-1 text-[11px] text-zinc-500">{h.desc}</p>
                </div>
                <ExternalLink className="mt-1 h-3.5 w-3.5 shrink-0 text-zinc-700 group-hover:text-zinc-500" />
              </CardContent>
            </Card>
          </a>
        ))}
      </div>

      {/* FAQ */}
      <Card className="border-zinc-800/60 bg-zinc-900/70 backdrop-blur-sm">
        <CardContent className="px-6 py-2">
          {FAQS.map((faq) => (
            <FaqItem key={faq.q} q={faq.q} a={faq.a} />
          ))}
        </CardContent>
      </Card>

      <div className="rounded-lg border border-zinc-800/40 bg-zinc-900/40 px-4 py-3 text-center text-xs text-zinc-500">
        🔒 CyberShield AI is aligned with Cyber Surakshit Bharat, ISEA, and Cyber Aware Digital Naagrik initiatives.
      </div>
    </div>
  );
}