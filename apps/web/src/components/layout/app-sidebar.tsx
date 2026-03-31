"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  BookOpen,
  ChevronDown,
  HelpCircle,
  LayoutDashboard,
  Link as LinkIcon,
  LogOut,
  Mail,
  MessageSquare,
  Mic,
  Moon,
  PanelLeftClose,
  PanelLeftOpen,
  Settings,
  Shield,
  FileText,
  Trophy,
  Video,
  Sun,
  Image as ImageIcon,
  Bot,
} from "lucide-react";
import { useTheme } from "next-themes";
import { cn } from "@/lib/utils";
import { useSidebar } from "@/providers/sidebar-provider";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Sheet, SheetContent, SheetTitle } from "@/components/ui/sheet";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { getInitials } from "@/lib/utils";

/* ── Nav Config ── */
interface NavItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
}

interface NavGroup {
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  items: NavItem[];
  requireAuth?: boolean;
  requireRole?: string[];
}

const NAV_GROUPS: NavGroup[] = [
  {
    label: "Analyze",
    icon: Shield,
    items: [
      { label: "Email", href: "/analyze/email", icon: Mail },
      { label: "URL / QR", href: "/analyze/url", icon: LinkIcon },
      { label: "Audio", href: "/analyze/audio", icon: Mic },
      { label: "Image", href: "/analyze/image", icon: ImageIcon },
      { label: "Video", href: "/analyze/video", icon: Video },
    ],
  },
  {
    label: "Awareness",
    icon: BookOpen,
    items: [
      { label: "Quizzes", href: "/awareness/quizzes", icon: HelpCircle },
      { label: "Scenarios", href: "/awareness/scenarios", icon: MessageSquare },
      { label: "Resources", href: "/awareness/resources", icon: BookOpen },
    ],
  },
  // Assistant removed from NAV_GROUPS (will be added as a flat link below)
  {
    label: "Reports",
    icon: FileText,
    requireAuth: true,
    items: [
      { label: "Analyses", href: "/reports/analyses", icon: FileText },
      { label: "Quiz History", href: "/reports/quizzes", icon: Trophy },
    ],
  },
  {
    label: "Admin",
    icon: Settings,
    requireAuth: true,
    requireRole: ["admin", "org_admin"],
    items: [
      { label: "Metrics", href: "/admin/metrics", icon: BarChart3 },
      { label: "Content", href: "/admin/content", icon: Settings },
    ],
  },
];

/* ── Sidebar Content (shared desktop & mobile) ── */
function SidebarContent({
  collapsed,
  onNavigate,
}: {
  collapsed: boolean;
  onNavigate?: () => void;
}) {
  const pathname = usePathname();
  const { theme, setTheme } = useTheme();
  const { user, isAuthenticated, logout } = useAuth();
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  // Auto-expand the group containing the current path
  useEffect(() => {
    for (const group of NAV_GROUPS) {
      if (group.items.some((item) => pathname.startsWith(item.href))) {
        setExpanded((prev) => ({ ...prev, [group.label]: true }));
      }
    }
  }, [pathname]);

  const toggleGroup = (label: string) => {
    if (collapsed) return;
    setExpanded((prev) => ({ ...prev, [label]: !prev[label] }));
  };

  const isActive = (href: string) => pathname === href || pathname.startsWith(href + "/");

  const renderNavItem = (item: NavItem, indent = false) => {
    const active = isActive(item.href);
    const Icon = item.icon;

    const content = (
      <Link
        href={item.href}
        onClick={onNavigate}
        className={cn(
          "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-200",
          indent && !collapsed && "ml-4",
          active
            ? "bg-primary/10 text-primary border-l-2 border-primary"
            : "text-muted-foreground hover:text-foreground hover:bg-accent",
          collapsed && "justify-center px-2"
        )}
      >
        <Icon className={cn("h-4 w-4 shrink-0", active && "text-primary")} />
        {!collapsed && <span className="truncate">{item.label}</span>}
      </Link>
    );

    if (collapsed) {
      return (
        <Tooltip key={item.href} delayDuration={0}>
          <TooltipTrigger asChild>{content}</TooltipTrigger>
          <TooltipContent side="right" sideOffset={10}>
            {item.label}
          </TooltipContent>
        </Tooltip>
      );
    }

    return <div key={item.href}>{content}</div>;
  };

  const renderGroup = (group: NavGroup) => {
    if (group.requireAuth && !isAuthenticated) return null;
    if (group.requireRole && (!user || !group.requireRole.includes(user.role))) return null;

    const isGroupActive = group.items.some((i) => isActive(i.href));
    const isExpanded = expanded[group.label] || false;
    const Icon = group.icon;

    if (collapsed) {
      // In collapsed mode, show the first item's link on the group icon
      const firstActiveItem = group.items.find((i) => isActive(i.href));
      const targetHref = firstActiveItem?.href || group.items[0]?.href || "#";

      return (
        <Tooltip key={group.label} delayDuration={0}>
          <TooltipTrigger asChild>
            <Link
              href={targetHref}
              onClick={onNavigate}
              className={cn(
                "flex items-center justify-center rounded-lg px-2 py-2 transition-all duration-200",
                isGroupActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:text-foreground hover:bg-accent"
              )}
            >
              <Icon className="h-4 w-4" />
            </Link>
          </TooltipTrigger>
          <TooltipContent side="right" sideOffset={10}>
            {group.label}
          </TooltipContent>
        </Tooltip>
      );
    }

    return (
      <div key={group.label} className="space-y-0.5">
        <button
          onClick={() => toggleGroup(group.label)}
          className={cn(
            "flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-200",
            isGroupActive
              ? "text-foreground"
              : "text-muted-foreground hover:text-foreground hover:bg-accent"
          )}
        >
          <Icon className={cn("h-4 w-4 shrink-0", isGroupActive && "text-primary")} />
          <span className="flex-1 truncate text-left">{group.label}</span>
          <ChevronDown
            className={cn(
              "h-3.5 w-3.5 transition-transform duration-200",
              isExpanded && "rotate-180"
            )}
          />
        </button>
        <div
          className={cn(
            "grid transition-all duration-200",
            isExpanded ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0"
          )}
        >
          <div className="overflow-hidden space-y-0.5">
            {group.items.map((item) => renderNavItem(item, true))}
          </div>
        </div>
      </div>
    );
  };

  return (
    <TooltipProvider delayDuration={0}>
      <div className="flex h-full flex-col">
        {/* ── Header ── */}
        <div className={cn(
          "flex h-14 items-center border-b border-sidebar-border shrink-0",
          collapsed ? "justify-center px-2" : "px-4 gap-3"
        )}>
          <Link href="/dashboard" onClick={onNavigate} className="flex items-center gap-2.5 group">
            <div className="relative">
              <Shield className="h-7 w-7 text-cs-cyan transition-transform group-hover:scale-110" />
              <div className="absolute inset-0 bg-cs-cyan/20 blur-xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
            {!collapsed && (
              <span className="font-display text-base font-bold tracking-tight">
                <span className="text-cs-cyan">Cyber</span>
                <span className="text-foreground">Shield</span>
              </span>
            )}
          </Link>
        </div>

        {/* ── Navigation ── */}
        <nav className="flex-1 overflow-y-auto px-2 py-3 space-y-1">
          {/* Dashboard (standalone) */}
          {renderNavItem({
            label: "Dashboard",
            href: "/dashboard",
            icon: LayoutDashboard,
          })}

          {/* Assistant (flat link) */}
          {renderNavItem({
            label: "Assistant",
            href: "/assistant",
            icon: Bot,
          })}

          <Separator className="my-2 bg-sidebar-border" />

          {/* Groups */}
          {NAV_GROUPS.map(renderGroup)}

          <Separator className="my-2 bg-sidebar-border" />

          {/* Help */}
          {renderNavItem({
            label: "Help",
            href: "/help",
            icon: HelpCircle,
          })}
        </nav>

        {/* ── Footer ── */}
        <div className="shrink-0 border-t border-sidebar-border p-2 space-y-1">
          {/* Theme Toggle (commented out)
          {collapsed ? (
            <Tooltip delayDuration={0}>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="w-full h-9"
                  onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                >
                  <Sun className="h-4 w-4 hidden dark:block" />
                  <Moon className="h-4 w-4 block dark:hidden" />
                </Button>
              </TooltipTrigger>
              <TooltipContent side="right" sideOffset={10}>
                Toggle theme
              </TooltipContent>
            </Tooltip>
          ) : (
            <Button
              variant="ghost"
              size="sm"
              className="w-full justify-start gap-3 px-3 text-muted-foreground"
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            >
              <Sun className="h-4 w-4 hidden dark:block" />
              <Moon className="h-4 w-4 block dark:hidden" />
              <span className="hidden dark:inline">Light Mode</span>
              <span className="inline dark:hidden">Dark Mode</span>
            </Button>
          )}
          */}

          {/* User Menu */}
          {isAuthenticated && user ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button
                  className={cn(
                    "flex w-full items-center gap-3 rounded-lg px-2 py-2 text-sm transition-colors",
                    "hover:bg-accent text-foreground",
                    collapsed && "justify-center"
                  )}
                >
                  <Avatar className="h-7 w-7">
                    <AvatarFallback className="bg-primary/20 text-primary text-xs">
                      {getInitials(user.display_name || user.email)}
                    </AvatarFallback>
                  </Avatar>
                  {!collapsed && (
                    <div className="flex-1 text-left truncate">
                      <p className="text-xs font-medium truncate">
                        {user.display_name || user.email}
                      </p>
                      <p className="text-[10px] text-muted-foreground truncate">
                        {user.email}
                      </p>
                    </div>
                  )}
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent
                align={collapsed ? "center" : "end"}
                side={collapsed ? "right" : "top"}
                sideOffset={8}
                className="w-56"
              >
                <div className="px-2 py-1.5">
                  <p className="text-sm font-medium">{user.display_name || "User"}</p>
                  <p className="text-xs text-muted-foreground">{user.email}</p>
                </div>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={() => {
                    logout();
                    onNavigate?.();
                  }}
                  className="text-destructive focus:text-destructive"
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  Sign Out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <div className={cn("flex gap-1", collapsed ? "flex-col" : "flex-row")}>
              {collapsed ? (
                <Tooltip delayDuration={0}>
                  <TooltipTrigger asChild>
                    <Button variant="ghost" size="icon" className="w-full h-9" asChild>
                      <Link href="/signin" onClick={onNavigate}>
                        <LogOut className="h-4 w-4 rotate-180" />
                      </Link>
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent side="right" sideOffset={10}>
                    Sign In
                  </TooltipContent>
                </Tooltip>
              ) : (
                <>
                  <Button variant="ghost" size="sm" className="flex-1" asChild>
                    <Link href="/signin" onClick={onNavigate}>Sign In</Link>
                  </Button>
                  <Button
                    size="sm"
                    className="flex-1 bg-cs-cyan hover:bg-cs-cyan/90 text-black"
                    asChild
                  >
                    <Link href="/signup" onClick={onNavigate}>Sign Up</Link>
                  </Button>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </TooltipProvider>
  );
}

/* ── Main Component ── */
export function AppSidebar() {
  const { isCollapsed, isMobileOpen, setMobileOpen, toggleCollapsed } = useSidebar();

  return (
    <>
      {/* Desktop Sidebar */}
      <aside
        className={cn(
          "hidden lg:flex fixed left-0 top-0 z-40 h-screen flex-col",
          "bg-sidebar border-r border-sidebar-border",
          "transition-all duration-300 ease-in-out",
          isCollapsed ? "w-[72px]" : "w-64"
        )}
      >
        <SidebarContent collapsed={isCollapsed} />

        {/* Collapse Toggle (bottom-right corner) */}
        <button
          onClick={toggleCollapsed}
          className="absolute -right-3 top-7 z-50 flex h-6 w-6 items-center justify-center rounded-full border border-border bg-background shadow-sm hover:bg-accent transition-colors"
        >
          {isCollapsed ? (
            <PanelLeftOpen className="h-3 w-3" />
          ) : (
            <PanelLeftClose className="h-3 w-3" />
          )}
        </button>
      </aside>

      {/* Mobile Sidebar (Sheet) */}
      <Sheet open={isMobileOpen} onOpenChange={setMobileOpen}>
        <SheetContent side="left" className="w-64 p-0 bg-sidebar">
          <SheetTitle className="sr-only">Navigation</SheetTitle>
          <SidebarContent
            collapsed={false}
            onNavigate={() => setMobileOpen(false)}
          />
        </SheetContent>
      </Sheet>
    </>
  );
}