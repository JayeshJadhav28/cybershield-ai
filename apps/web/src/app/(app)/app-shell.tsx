"use client";

import { useSidebar } from "@/providers/sidebar-provider";
import { AppTopbar } from "@/components/layout/app-topbar";
import { ErrorBoundary } from "@/components/shared/error-boundary";
import { cn } from "@/lib/utils";

export function AppShell({ children }: { children: React.ReactNode }) {
  const { isCollapsed } = useSidebar();

  return (
    <div
      className={cn(
        "min-h-screen transition-all duration-300 ease-in-out",
        "lg:pl-64",
        isCollapsed && "lg:pl-[72px]"
      )}
    >
      <AppTopbar />
      <main className="p-4 lg:p-6">
        <ErrorBoundary>{children}</ErrorBoundary>
      </main>
    </div>
  );
}