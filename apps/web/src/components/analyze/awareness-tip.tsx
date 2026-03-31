'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ExternalLink, BookOpen, Lightbulb } from 'lucide-react';
import Link from 'next/link';
import { motion } from 'framer-motion';

interface AwarenessTipProps {
  tip: string;
}

export function AwarenessTip({ tip }: AwarenessTipProps) {
  if (!tip) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.2 }}
    >
      <Card className="border border-cyan-500/15 bg-cyan-950/8 overflow-hidden">
        {/* Subtle top accent */}
        <div className="h-px w-full bg-gradient-to-r from-transparent via-cyan-500/30 to-transparent" />

        <CardContent className="px-5 py-4">
          <div className="flex items-start gap-3">
            {/* Icon */}
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-cyan-500/10 border border-cyan-500/20">
              <Lightbulb className="h-4 w-4 text-cyan-400" />
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <p className="text-[11px] font-semibold text-cyan-400 uppercase tracking-wider mb-1">
                Safety Tip
              </p>
              <p className="text-sm text-zinc-300 leading-relaxed">
                {tip}
              </p>

              {/* Actions */}
              <div className="flex flex-wrap items-center gap-2 mt-3">
                <Button
                  variant="outline"
                  size="sm"
                  className="h-7 text-[11px] border-zinc-700 text-zinc-400 hover:text-zinc-200 hover:border-zinc-600 hover:bg-zinc-800/50 gap-1.5"
                  asChild
                >
                  <Link href="/awareness/resources">
                    <BookOpen className="h-3 w-3" />
                    Learn More
                  </Link>
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="h-7 text-[11px] border-zinc-700 text-zinc-400 hover:text-zinc-200 hover:border-zinc-600 hover:bg-zinc-800/50 gap-1.5"
                  asChild
                >
                  <a
                    href="https://cybercrime.gov.in"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <ExternalLink className="h-3 w-3" />
                    Report to Cyber Crime Portal
                  </a>
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}