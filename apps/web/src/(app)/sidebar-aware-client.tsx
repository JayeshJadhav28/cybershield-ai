"use client";

import { useSidebar } from "@/providers/sidebar-provider";
import { cn } from "@/lib/utils";

export function SidebarAwareClient({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isCollapsed } = useSidebar();

  return (
    <div
      className={cn(
        "transition-all duration-300",
        // Override the parent's lg:pl-64 by using negative margin + own padding
        // Actually handled by parent, but we need to re-render to reflect collapse
      )}
      style={{
        // On lg+, the parent has lg:pl-64; we adjust via a CSS variable approach
        // Simpler: re-set paddingLeft on the parent via this wrapper
      }}
    >
      <style>{`
        @media (min-width: 1024px) {
          .app-shell-content {
            padding-left: ${isCollapsed ? "72px" : "256px"};
            transition: padding-left 300ms ease-in-out;
          }
        }
      `}</style>
      <div className="app-shell-content">{children}</div>
    </div>
  );
}