import React from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Chrome } from "lucide-react";

type ChromeExtensionButtonProps = React.ComponentProps<typeof Button>;

export function ChromeExtensionButton({ className, ...props }: Omit<ChromeExtensionButtonProps, "children">) {
  return (
    <Button className={cn("h-12 gap-2 bg-white/5 border border-white/10 hover:bg-white/10 text-white", className)} {...props}>
      <Chrome className="size-5" />
      <div className="text-left flex flex-col items-start justify-center pr-2">
        <span className="text-[10px] leading-none tracking-tighter opacity-70">Available as</span>
        <p className="text-sm font-bold leading-none">Chrome Extension</p>
      </div>
    </Button>
  );
}