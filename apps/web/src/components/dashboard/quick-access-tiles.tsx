'use client';

import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import {
  Mail,
  Link2,
  Mic,
  Video,
  GraduationCap,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';

/* ------------------------------------------------------------------ */
/*  Tile definitions                                                   */
/* ------------------------------------------------------------------ */
const tiles = [
  {
    title: 'Email Analyzer',
    description: 'Check if an email is phishing',
    href: '/analyze/email',
    icon: Mail,
    gradient: 'from-cyan-500/20 to-cyan-600/5',
    borderHover: 'hover:border-cyan-500/40',
    iconColor: 'text-cyan-400',
    glowColor: 'group-hover:shadow-cyan-500/10',
  },
  {
    title: 'URL / QR Analyzer',
    description: 'Verify links and QR codes',
    href: '/analyze/url',
    icon: Link2,
    gradient: 'from-blue-500/20 to-blue-600/5',
    borderHover: 'hover:border-blue-500/40',
    iconColor: 'text-blue-400',
    glowColor: 'group-hover:shadow-blue-500/10',
  },
  {
    title: 'Audio Analyzer',
    description: 'Detect deepfake voice clips',
    href: '/analyze/audio',
    icon: Mic,
    gradient: 'from-purple-500/20 to-purple-600/5',
    borderHover: 'hover:border-purple-500/40',
    iconColor: 'text-purple-400',
    glowColor: 'group-hover:shadow-purple-500/10',
  },
  {
    title: 'Video Analyzer',
    description: 'Spot manipulated video',
    href: '/analyze/video',
    icon: Video,
    gradient: 'from-rose-500/20 to-rose-600/5',
    borderHover: 'hover:border-rose-500/40',
    iconColor: 'text-rose-400',
    glowColor: 'group-hover:shadow-rose-500/10',
  },
  {
    title: 'Awareness & Quizzes',
    description: 'Test your cyber-safety knowledge',
    href: '/awareness/quizzes',
    icon: GraduationCap,
    gradient: 'from-amber-500/20 to-amber-600/5',
    borderHover: 'hover:border-amber-500/40',
    iconColor: 'text-amber-400',
    glowColor: 'group-hover:shadow-amber-500/10',
  },
] as const;

/* ------------------------------------------------------------------ */
/*  Exported component                                                 */
/* ------------------------------------------------------------------ */
export function QuickAccessTiles() {
  return (
    <div className="space-y-3">
      <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-400">
        Quick Analysis
      </h2>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
        {tiles.map((tile, i) => (
          <motion.div
            key={tile.href}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4, delay: 0.3 + i * 0.07 }}
          >
            <Link href={tile.href}>
              <Card
                className={cn(
                  'group relative cursor-pointer overflow-hidden border-zinc-800/60 bg-zinc-900/70 backdrop-blur-sm',
                  'transition-all duration-300',
                  tile.borderHover,
                  tile.glowColor,
                  'hover:shadow-lg',
                )}
              >
                {/* gradient overlay */}
                <div
                  className={cn(
                    'pointer-events-none absolute inset-0 bg-gradient-to-br opacity-0 transition-opacity duration-300 group-hover:opacity-100',
                    tile.gradient,
                  )}
                />

                <CardContent className="relative flex flex-col items-center gap-3 p-5 text-center">
                  <div
                    className={cn(
                      'flex h-11 w-11 items-center justify-center rounded-xl bg-zinc-800/80 transition-transform duration-300 group-hover:scale-110',
                    )}
                  >
                    <tile.icon className={cn('h-5 w-5', tile.iconColor)} />
                  </div>

                  <div>
                    <p className="text-sm font-semibold text-zinc-200 transition-colors group-hover:text-white">
                      {tile.title}
                    </p>
                    <p className="mt-0.5 text-xs text-zinc-500 transition-colors group-hover:text-zinc-400">
                      {tile.description}
                    </p>
                  </div>
                </CardContent>
              </Card>
            </Link>
          </motion.div>
        ))}
      </div>
    </div>
  );
}