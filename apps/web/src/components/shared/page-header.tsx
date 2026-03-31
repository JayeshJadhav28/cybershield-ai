import type { LucideIcon } from "lucide-react";

interface PageHeaderProps {
  title: string;
  description?: string;
  icon?: LucideIcon;
  children?: React.ReactNode;
}

export function PageHeader({
  title,
  description,
  icon: Icon,
  children,
}: PageHeaderProps) {
  return (
    <div className="flex items-start justify-between gap-4">
      <div className="flex items-start gap-3">
        {Icon && (
          <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-zinc-800/80">
            <Icon className="h-5 w-5 text-cyan-400" />
          </div>
        )}
        <div>
          <h1 className="text-xl font-bold tracking-tight text-zinc-100">
            {title}
          </h1>
          {description && (
            <p className="mt-0.5 text-sm text-zinc-400">{description}</p>
          )}
        </div>
      </div>
      {children && <div className="shrink-0">{children}</div>}
    </div>
  );
}