import { SidebarProvider } from "@/providers/sidebar-provider";
import { AppSidebar } from "@/components/layout/app-sidebar";
import { AppShell } from "./app-shell";

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <SidebarProvider>
      <div className="relative min-h-screen">
        <AppSidebar />
        <AppShell>{children}</AppShell>
      </div>
    </SidebarProvider>
  );
}