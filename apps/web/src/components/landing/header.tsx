"use client";

import React from "react";
import Link from "next/link";
import { Shield } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { MenuToggleIcon } from "@/components/ui/menu-toggle-icon";
import { createPortal } from "react-dom";

export function Header() {
  const [open, setOpen] = React.useState(false);
  const [scrolled, setScrolled] = React.useState(false);

  const links = [
    { label: "Features", href: "#features" },
    { label: "How It Works", href: "#how-it-works" },
    { label: "Awareness", href: "#awareness" },
  ];

  // Scroll detection
  React.useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Body overflow lock for mobile menu
  React.useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  return (
    <header
      className={cn(
        "fixed top-0 left-0 right-0 z-50 border-b transition-all duration-300",
        scrolled
          ? "border-zinc-800/50 bg-[#0a0a0f]/80 backdrop-blur-xl"
          : "border-transparent bg-transparent"
      )}
    >
      <nav className="mx-auto flex h-16 w-full max-w-7xl items-center justify-between px-6">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2">
          <Shield className="h-7 w-7 text-cyan-400" />
          <span className="text-lg font-bold">
            <span className="text-white">Cyber</span>
            <span className="text-cyan-400">Shield</span>
          </span>
        </Link>

        {/* Desktop nav links */}
        <div className="hidden md:flex items-center gap-8">
          {links.map((link) => (
            <a
              key={link.label}
              href={link.href}
              className="text-sm text-zinc-400 hover:text-white transition-colors"
            >
              {link.label}
            </a>
          ))}
        </div>

        {/* Desktop buttons */}
        <div className="hidden md:flex items-center gap-3">
          <Button
            variant="ghost"
            asChild
            className="text-zinc-400 hover:text-white hover:bg-white/5"
          >
            <Link href="/signin">Sign In</Link>
          </Button>

          <Button
            variant="shine"
            asChild
            className="bg-cyan-500 hover:bg-cyan-500/80 text-black font-semibold"
          >
            <Link href="/signup">Get Started →</Link>
          </Button>
        </div>

        {/* Mobile hamburger */}
        <Button
          size="icon"
          variant="ghost"
          onClick={() => setOpen(!open)}
          className="md:hidden text-zinc-400 hover:text-white hover:bg-white/5"
          aria-expanded={open}
          aria-controls="mobile-menu"
          aria-label="Toggle menu"
        >
          <MenuToggleIcon open={open} className="size-5" duration={300} />
        </Button>
      </nav>

      {/* Mobile menu */}
      <MobileMenu open={open}>
        <div className="grid gap-y-1">
          {links.map((link) => (
            <a
              key={link.label}
              href={link.href}
              onClick={() => setOpen(false)}
              className="flex items-center rounded-lg px-4 py-3 text-sm text-zinc-400 hover:text-white hover:bg-white/5 transition-colors"
            >
              {link.label}
            </a>
          ))}
        </div>

        <div className="flex flex-col gap-3 pt-4 border-t border-zinc-800/50">
          <Button
            variant="outline"
            asChild
            className="w-full bg-transparent border-zinc-700 text-zinc-300 hover:text-white hover:border-zinc-500"
          >
            <Link href="/signin" onClick={() => setOpen(false)}>
              Sign In
            </Link>
          </Button>

          <Button
            variant="shine"
            asChild
            className="w-full bg-cyan-500 hover:bg-cyan-500/80 text-black font-semibold"
          >
            <Link href="/signup" onClick={() => setOpen(false)}>
              Get Started →
            </Link>
          </Button>
        </div>
      </MobileMenu>
    </header>
  );
}

/* ── Mobile menu portal ── */
type MobileMenuProps = React.ComponentProps<"div"> & { open: boolean };

function MobileMenu({
  open,
  children,
  className,
  ...props
}: MobileMenuProps) {
  if (!open || typeof window === "undefined") return null;

  return createPortal(
    <div
      id="mobile-menu"
      className="fixed top-16 right-0 bottom-0 left-0 z-40 overflow-hidden border-t border-zinc-800/50 bg-[#0a0a0f]/95 backdrop-blur-xl md:hidden"
    >
      <div
        data-slot={open ? "open" : "closed"}
        className={cn(
          "data-[slot=open]:animate-in data-[slot=open]:fade-in-0 data-[slot=open]:zoom-in-97",
          "flex size-full flex-col justify-between p-6",
          className
        )}
        {...props}
      >
        {children}
      </div>
    </div>,
    document.body
  );
}