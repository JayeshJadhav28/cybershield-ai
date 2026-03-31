'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

/* ------------------------------------------------------------------ */
/*  Recharts – dynamic import guard                                    */
/* ------------------------------------------------------------------ */
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */
export interface ThreatDistribution {
  safe: number;
  suspicious: number;
  dangerous: number;
}

/* ------------------------------------------------------------------ */
/*  Constants                                                          */
/* ------------------------------------------------------------------ */
const COLORS: Record<string, string> = {
  safe: '#22c55e',
  suspicious: '#f59e0b',
  dangerous: '#ef4444',
};

const LABEL_TEXT: Record<string, string> = {
  safe: 'Safe',
  suspicious: 'Suspicious',
  dangerous: 'Dangerous',
};

/* ------------------------------------------------------------------ */
/*  Custom tooltip                                                     */
/* ------------------------------------------------------------------ */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;
  const d = payload[0];
  return (
    <div className="rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-xs shadow-xl">
      <span style={{ color: d.payload.fill }} className="font-semibold">
        {LABEL_TEXT[d.name] ?? d.name}
      </span>
      <span className="ml-2 text-zinc-300">{d.value} analyses</span>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Legend                                                             */
/* ------------------------------------------------------------------ */
function Legend({ data }: { data: { name: string; value: number }[] }) {
  const total = data.reduce((s, d) => s + d.value, 0) || 1;
  return (
    <div className="flex flex-col gap-2.5">
      {data.map((d) => {
        const pct = Math.round((d.value / total) * 100);
        return (
          <div key={d.name} className="flex items-center gap-2.5">
            <span
              className="h-2.5 w-2.5 shrink-0 rounded-full"
              style={{ backgroundColor: COLORS[d.name] }}
            />
            <span className="flex-1 text-sm text-zinc-400">
              {LABEL_TEXT[d.name]}
            </span>
            <span className="font-mono text-sm font-medium text-zinc-200">
              {d.value}
            </span>
            <span className="w-10 text-right font-mono text-xs text-zinc-500">
              {pct}%
            </span>
          </div>
        );
      })}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Empty state                                                        */
/* ------------------------------------------------------------------ */
function EmptyChart() {
  return (
    <div className="flex h-full min-h-[160px] flex-col items-center justify-center text-center">
      <div className="mb-2 h-20 w-20 rounded-full border-4 border-dashed border-zinc-800" />
      <p className="text-xs text-zinc-500">
        Run analyses to see your threat distribution
      </p>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Exported component                                                 */
/* ------------------------------------------------------------------ */
export function ThreatChart({
  distribution,
}: {
  distribution: ThreatDistribution;
}) {
  const total =
    distribution.safe + distribution.suspicious + distribution.dangerous;

  const data = [
    { name: 'safe', value: distribution.safe },
    { name: 'suspicious', value: distribution.suspicious },
    { name: 'dangerous', value: distribution.dangerous },
  ].filter((d) => d.value > 0);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.4 }}
    >
      <Card className="border-zinc-800/60 bg-zinc-900/70 backdrop-blur-sm">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-semibold uppercase tracking-wider text-zinc-400">
            Threat Distribution
          </CardTitle>
        </CardHeader>
        <CardContent>
          {total === 0 ? (
            <EmptyChart />
          ) : (
            <div className="flex flex-col items-center gap-6 sm:flex-row">
              {/* Chart */}
              <div className="relative h-[180px] w-[180px] shrink-0">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={data}
                      cx="50%"
                      cy="50%"
                      innerRadius={52}
                      outerRadius={80}
                      paddingAngle={3}
                      dataKey="value"
                      stroke="none"
                      animationBegin={200}
                      animationDuration={900}
                    >
                      {data.map((entry) => (
                        <Cell
                          key={entry.name}
                          fill={COLORS[entry.name]}
                          className="outline-none"
                        />
                      ))}
                    </Pie>
                    <Tooltip content={<CustomTooltip />} />
                  </PieChart>
                </ResponsiveContainer>
                {/* center label */}
                <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
                  <span className="font-mono text-2xl font-bold text-zinc-100">
                    {total}
                  </span>
                  <span className="text-[10px] uppercase tracking-wider text-zinc-500">
                    Total
                  </span>
                </div>
              </div>

              {/* Legend */}
              <div className="flex-1">
                <Legend data={data} />
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}