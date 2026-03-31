"use client";

import { Fragment } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { Menu } from "lucide-react";
import { cn } from "@/lib/utils";
import { useSidebar } from "@/providers/sidebar-provider";
import { Button } from "@/components/ui/button";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";

/* ── Path → Label mapping ── */
const PATH_LABELS: Record<string, string> = {
  dashboard: "Dashboard",
  analyze: "Analyze",
  email: "Email",
  url: "URL / QR",
  audio: "Audio",
  video: "Video",
  awareness: "Awareness",
  quizzes: "Quizzes",
  scenarios: "Scenarios",
  resources: "Resources",
  reports: "Reports",
  analyses: "Analyses",
  admin: "Admin",
  metrics: "Metrics",
  content: "Content",
  help: "Help & Support",
};

function generateBreadcrumbs(pathname: string) {
  const segments = pathname.split("/").filter(Boolean);
  return segments.map((seg, idx) => ({
    label: PATH_LABELS[seg] || seg.charAt(0).toUpperCase() + seg.slice(1).replace(/-/g, " "),
    href: "/" + segments.slice(0, idx + 1).join("/"),
    isLast: idx === segments.length - 1,
  }));
}

export function AppTopbar() {
  const pathname = usePathname();
  const { setMobileOpen, isCollapsed } = useSidebar();
  const crumbs = generateBreadcrumbs(pathname);

  return (
    <header
      className={cn(
        "sticky top-0 z-30 flex h-14 items-center gap-4 border-b border-border",
        "bg-background/80 backdrop-blur-xl px-4 lg:px-6"
      )}
    >
      {/* Mobile hamburger */}
      <Button
        variant="ghost"
        size="icon"
        className="lg:hidden shrink-0"
        onClick={() => setMobileOpen(true)}
      >
        <Menu className="h-5 w-5" />
        <span className="sr-only">Open navigation</span>
      </Button>

      {/* Breadcrumbs */}
      <Breadcrumb className="flex-1">
        <BreadcrumbList>
          {crumbs.map((crumb, idx) => (
            <Fragment key={crumb.href}>
              {idx > 0 && <BreadcrumbSeparator />}
              <BreadcrumbItem>
                {crumb.isLast ? (
                  <BreadcrumbPage>{crumb.label}</BreadcrumbPage>
                ) : (
                  <BreadcrumbLink asChild>
                    <Link href={crumb.href}>{crumb.label}</Link>
                  </BreadcrumbLink>
                )}
              </BreadcrumbItem>
            </Fragment>
          ))}
        </BreadcrumbList>
      </Breadcrumb>

      {/* Right side placeholder for Phase 2 (search, notifications) */}
      <div className="flex items-center gap-2">
        {/* Future: search, notifications bell */}
      </div>
    </header>
  );
}