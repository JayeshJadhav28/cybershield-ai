"use client";

import Link from "next/link";
import { Clock, ChevronRight, Shield } from "lucide-react";
import { SCENARIOS } from "@/lib/scenarios-data";
import { PageHeader } from "@/components/shared/page-header";

const difficultyColors = {
  Easy: "text-green-400 bg-green-400/10 border-green-400/20",
  Medium: "text-amber-400 bg-amber-400/10 border-amber-400/20",
  Hard: "text-red-400 bg-red-400/10 border-red-400/20",
};

export default function ScenariosPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Scenario Simulations"
        description="Interactive simulations to test your response to real-world cyber threats"
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {SCENARIOS.map((scenario) => (
          <Link
            key={scenario.id}
            href={`/awareness/scenarios/${scenario.id}`}
            className="group flex flex-col rounded-xl border border-zinc-800 bg-zinc-900/50 p-5 transition-all hover:border-cyan-500/30 hover:bg-zinc-900"
          >
            {/* Icon + category */}
            <div className="flex items-start justify-between mb-4">
              <span className="text-3xl">{scenario.icon}</span>
              <span
                className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-medium ${
                  difficultyColors[scenario.difficulty]
                }`}
              >
                {scenario.difficulty}
              </span>
            </div>

            {/* Title */}
            <h3 className="text-sm font-semibold text-zinc-100 mb-1.5 group-hover:text-cyan-400 transition-colors">
              {scenario.title}
            </h3>

            {/* Description */}
            <p className="text-xs text-zinc-400 leading-relaxed mb-4 flex-1">
              {scenario.description}
            </p>

            {/* Footer */}
            <div className="flex items-center justify-between pt-3 border-t border-zinc-800/50">
              <div className="flex items-center gap-3">
                <span className="inline-flex items-center gap-1 text-[10px] text-zinc-500">
                  <Clock className="h-3 w-3" />
                  {scenario.estimated_time_minutes} min
                </span>
                <span className="inline-flex items-center gap-1 text-[10px] text-zinc-500">
                  <Shield className="h-3 w-3" />
                  {scenario.category}
                </span>
              </div>
              <ChevronRight className="h-4 w-4 text-zinc-600 group-hover:text-cyan-400 transition-colors" />
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}