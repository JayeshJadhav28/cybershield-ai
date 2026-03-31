'use client';

import { PageHeader } from '@/components/shared/page-header';
import { ResourceCard } from '@/components/awareness/resource-card';
import {
  BookOpen,
  Shield,
  Phone,
  Globe,
  FileWarning,
  Smartphone,
  KeyRound,
  Video,
  Mic,
  QrCode,
} from 'lucide-react';
import { motion } from 'framer-motion';

const RESOURCES = [
  {
    title: 'National Cyber Crime Reporting Portal',
    description:
      'Report cyber crimes online including financial fraud, identity theft, and social media scams.',
    category: 'Report',
    icon: Globe,
    iconColor: 'text-cyan-400',
    href: 'https://cybercrime.gov.in',
    tags: ['India', 'Official', 'Report'],
  },
  {
    title: 'Cyber Crime Helpline — 1930',
    description:
      'Call 1930 to report cyber fraud. Available 24x7 for immediate assistance with financial cyber crimes.',
    category: 'Helpline',
    icon: Phone,
    iconColor: 'text-emerald-400',
    href: 'tel:1930',
    tags: ['India', 'Emergency', '24x7'],
  },
  {
    title: 'CERT-In Advisories',
    description:
      'Stay updated with the latest cyber security advisories from the Indian Computer Emergency Response Team.',
    category: 'Advisory',
    icon: Shield,
    iconColor: 'text-blue-400',
    href: 'https://www.cert-in.org.in',
    tags: ['Government', 'Alerts'],
  },
  {
    title: 'How Phishing Works',
    description:
      'Understand the anatomy of phishing attacks — from email spoofing to credential harvesting. Learn the red flags to watch for.',
    category: 'Learn',
    icon: FileWarning,
    iconColor: 'text-amber-400',
    href: 'https://www.cert-in.org.in/PDF/CSA_Booklet.pdf',
    tags: ['Phishing', 'Email', 'Beginner'],
  },
  {
    title: 'UPI & QR Code Safety',
    description:
      'Learn how scammers tamper with QR codes, create fake payment requests, and impersonate merchants via UPI.',
    category: 'Learn',
    icon: QrCode,
    iconColor: 'text-indigo-400',
    href: 'https://www.nipl.com/uploads/BHIM_UPI_Brand_Guidelines_321f409c10.pdf',
    tags: ['UPI', 'QR', 'India'],
  },
  {
    title: 'Deepfake Audio Detection',
    description:
      'Understand how AI-generated voices work and learn to spot spectral artifacts and unnatural prosody in audio clips.',
    category: 'Learn',
    icon: Mic,
    iconColor: 'text-purple-400',
    href: 'https://www.freepressjournal.in/mumbai/cert-in-issues-advisory-on-ai-powered-deepfakes-warns-citizens-of-scammers-using-realistic-videos',
    tags: ['Deepfake', 'Audio', 'AI'],
  },
  {
    title: 'Deepfake Video Detection',
    description:
      'Learn about facial manipulation techniques, temporal inconsistencies, and visual artifacts in AI-generated videos.',
    category: 'Learn',
    icon: Video,
    iconColor: 'text-rose-400',
    href: 'https://www.cnbctv18.com/personal-finance/sbi-warns-of-deepfake-scams-what-they-are-and-how-to-stay-safe-ws-l-19819092.htm',
    tags: ['Deepfake', 'Video', 'AI'],
  },
  {
    title: 'KYC Fraud Prevention',
    description:
      'Banks never ask for KYC updates via phone or email links. Learn how KYC scams work and how to protect yourself.',
    category: 'Learn',
    icon: KeyRound,
    iconColor: 'text-orange-400',
    href: 'https://ibsintelligence.com/ibsi-news/rbi-issues-warning-on-kyc-fraud-urges-vigilance-and-direct-bank-contact/',
    tags: ['KYC', 'OTP', 'Bank'],
  },
  {
    title: 'Safe Digital Payments',
    description:
      'Best practices for UPI, net banking, and card payments. Never share OTP, PIN, or CVV with anyone.',
    category: 'Best Practices',
    icon: Smartphone,
    iconColor: 'text-teal-400',
    href: 'https://www.linkedin.com/pulse/digital-payment-safety-tips-per-rbi-guidelines-getepay-oij5c',
    tags: ['UPI', 'Banking', 'Safety'],
  },
];

export default function ResourcesPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Learning Resources"
        description="Educational resources and external links to stay safe in the digital world."
        icon={BookOpen}
      />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {RESOURCES.map((r, i) => (
          <motion.div
            key={r.title}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: i * 0.05 }}
          >
            <ResourceCard {...r} />
          </motion.div>
        ))}
      </div>

      {/* Footer info */}
      <div className="rounded-lg border border-zinc-800/40 bg-zinc-900/40 px-4 py-3 text-center text-xs text-zinc-500">
        🛡️ Aligned with{' '}
        <span className="font-medium text-zinc-400">Cyber Surakshit Bharat</span>,{' '}
        <span className="font-medium text-zinc-400">ISEA</span>, and{' '}
        <span className="font-medium text-zinc-400">Cyber Aware Digital Naagrik</span>{' '}
        initiatives.
      </div>
    </div>
  );
}