"use client";

import * as React from "react";
import * as TooltipPrimitive from "@radix-ui/react-tooltip";
import * as PopoverPrimitive from "@radix-ui/react-popover";
import * as DialogPrimitive from "@radix-ui/react-dialog";

// ── Utility ──
type ClassValue = string | number | boolean | null | undefined;
function cn(...inputs: ClassValue[]): string {
  return inputs.filter(Boolean).join(" ");
}

// ── Radix Primitives (self-contained to avoid conflicts with your existing shadcn) ──
const TooltipProvider = TooltipPrimitive.Provider;
const Tooltip = TooltipPrimitive.Root;
const TooltipTrigger = TooltipPrimitive.Trigger;
const TooltipContent = React.forwardRef<
  React.ElementRef<typeof TooltipPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof TooltipPrimitive.Content> & {
    showArrow?: boolean;
  }
>(({ className, sideOffset = 4, showArrow = false, ...props }, ref) => (
  <TooltipPrimitive.Portal>
    <TooltipPrimitive.Content
      ref={ref}
      sideOffset={sideOffset}
      className={cn(
        "relative z-50 max-w-[280px] rounded-md bg-popover text-popover-foreground px-1.5 py-1 text-xs",
        "animate-in fade-in-0 zoom-in-95",
        "data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95",
        "data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2",
        "data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2",
        className
      )}
      {...props}
    >
      {props.children}
      {showArrow && (
        <TooltipPrimitive.Arrow className="-my-px fill-popover" />
      )}
    </TooltipPrimitive.Content>
  </TooltipPrimitive.Portal>
));
TooltipContent.displayName = TooltipPrimitive.Content.displayName;

const Popover = PopoverPrimitive.Root;
const PopoverTrigger = PopoverPrimitive.Trigger;
const PopoverContent = React.forwardRef<
  React.ElementRef<typeof PopoverPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof PopoverPrimitive.Content>
>(({ className, align = "center", sideOffset = 4, ...props }, ref) => (
  <PopoverPrimitive.Portal>
    <PopoverPrimitive.Content
      ref={ref}
      align={align}
      sideOffset={sideOffset}
      className={cn(
        "z-50 w-64 rounded-xl bg-popover dark:bg-zinc-800 p-2 text-popover-foreground dark:text-white shadow-md outline-none",
        "animate-in data-[state=open]:fade-in-0 data-[state=closed]:fade-out-0",
        "data-[state=open]:zoom-in-95 data-[state=closed]:zoom-out-95",
        "data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2",
        "data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2",
        className
      )}
      {...props}
    />
  </PopoverPrimitive.Portal>
));
PopoverContent.displayName = PopoverPrimitive.Content.displayName;

const Dialog = DialogPrimitive.Root;
const DialogOverlay = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Overlay>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Overlay>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Overlay
    ref={ref}
    className={cn(
      "fixed inset-0 z-50 bg-black/60 backdrop-blur-sm",
      "data-[state=open]:animate-in data-[state=closed]:animate-out",
      "data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
      className
    )}
    {...props}
  />
));
DialogOverlay.displayName = DialogPrimitive.Overlay.displayName;

const DialogContent = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content>
>(({ className, children, ...props }, ref) => (
  <DialogPrimitive.Portal>
    <DialogOverlay />
    <DialogPrimitive.Content
      ref={ref}
      className={cn(
        "fixed left-[50%] top-[50%] z-50 grid w-full max-w-[90vw] md:max-w-[800px]",
        "translate-x-[-50%] translate-y-[-50%] gap-4 border-none bg-transparent p-0 shadow-none duration-300",
        "data-[state=open]:animate-in data-[state=closed]:animate-out",
        "data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
        "data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95",
        className
      )}
      {...props}
    >
      <div className="relative bg-card dark:bg-zinc-800 rounded-[28px] overflow-hidden shadow-2xl p-1">
        {children}
        <DialogPrimitive.Close className="absolute right-3 top-3 z-10 rounded-full bg-background/50 dark:bg-zinc-800 p-1 hover:bg-accent dark:hover:bg-zinc-700 transition-all">
          <XIcon className="h-5 w-5 text-muted-foreground dark:text-gray-200 hover:text-foreground dark:hover:text-white" />
          <span className="sr-only">Close</span>
        </DialogPrimitive.Close>
      </div>
    </DialogPrimitive.Content>
  </DialogPrimitive.Portal>
));
DialogContent.displayName = DialogPrimitive.Content.displayName;

// ── SVG Icons ──
const PlusIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" {...props}>
    <path d="M12 5V19" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M5 12H19" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const Settings2Icon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M20 7h-9" />
    <path d="M14 17H5" />
    <circle cx="17" cy="17" r="3" />
    <circle cx="7" cy="7" r="3" />
  </svg>
);

const SendIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" {...props}>
    <path d="M12 5.25L12 18.75" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M18.75 12L12 5.25L5.25 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const XIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <line x1="18" y1="6" x2="6" y2="18" />
    <line x1="6" y1="6" x2="18" y2="18" />
  </svg>
);

const LoaderIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="animate-spin" {...props}>
    <path d="M21 12a9 9 0 1 1-6.219-8.56" />
  </svg>
);

// ── Types ──
export interface ToolItem {
  id: string;
  name: string;
  shortName: string;
  icon: React.FC<React.SVGProps<SVGSVGElement>>;
  extra?: string;
}

export interface PromptBoxProps {
  /** Controlled value */
  value?: string;
  /** Called when value changes (controlled mode) */
  onValueChange?: (value: string) => void;
  /** Called when user clicks send */
  onSend?: (value: string) => void;
  /** Disables send and shows spinner */
  isLoading?: boolean;
  /** Custom tools list */
  tools?: ToolItem[];
  /** Called when a tool is selected */
  onToolSelect?: (toolId: string) => void;
  /** Show attach button (default: true) */
  showAttach?: boolean;
  /** Show tools button (default: true) */
  showTools?: boolean;
  /** Placeholder text */
  placeholder?: string;
  /** Additional className */
  className?: string;
  /** Footer text below the input */
  footerText?: string;
}

// ── Component ──
export const PromptBox = React.forwardRef<HTMLTextAreaElement, PromptBoxProps>(
  (
    {
      value: controlledValue,
      onValueChange,
      onSend,
      isLoading = false,
      tools = [],
      onToolSelect,
      showAttach = false,
      showTools = true,
      placeholder = "Message...",
      className,
      footerText,
    },
    ref
  ) => {
    const internalTextareaRef = React.useRef<HTMLTextAreaElement>(null);
    const fileInputRef = React.useRef<HTMLInputElement>(null);

    // ── Controlled / uncontrolled value ──
    const [internalValue, setInternalValue] = React.useState("");
    const isControlled = controlledValue !== undefined;
    const value = isControlled ? controlledValue : internalValue;

    const setValue = React.useCallback(
      (v: string) => {
        if (!isControlled) setInternalValue(v);
        onValueChange?.(v);
      },
      [isControlled, onValueChange]
    );

    // ── Other state ──
    const [imagePreview, setImagePreview] = React.useState<string | null>(null);
    const [selectedTool, setSelectedTool] = React.useState<string | null>(null);
    const [isPopoverOpen, setIsPopoverOpen] = React.useState(false);
    const [isImageDialogOpen, setIsImageDialogOpen] = React.useState(false);

    React.useImperativeHandle(ref, () => internalTextareaRef.current!, []);

    // ── Auto-resize textarea ──
    React.useLayoutEffect(() => {
      const textarea = internalTextareaRef.current;
      if (textarea) {
        textarea.style.height = "auto";
        textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
      }
    }, [value]);

    // ── Handlers ──
    const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      setValue(e.target.value);
    };

    const handleSend = () => {
      const trimmed = value.trim();
      if (!trimmed || isLoading) return;
      onSend?.(trimmed);
      setValue("");
      setSelectedTool(null);
      internalTextareaRef.current?.focus();
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    };

    const handlePlusClick = () => fileInputRef.current?.click();

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];
      if (file && file.type.startsWith("image/")) {
        const reader = new FileReader();
        reader.onloadend = () => setImagePreview(reader.result as string);
        reader.readAsDataURL(file);
      }
      event.target.value = "";
    };

    const handleRemoveImage = (e: React.MouseEvent<HTMLButtonElement>) => {
      e.stopPropagation();
      setImagePreview(null);
    };

    const handleToolSelect = (toolId: string) => {
      setSelectedTool(toolId);
      setIsPopoverOpen(false);
      onToolSelect?.(toolId);
      internalTextareaRef.current?.focus();
    };

    const hasValue = value.trim().length > 0 || !!imagePreview;
    const activeTool = selectedTool
      ? tools.find((t) => t.id === selectedTool)
      : null;
    const ActiveToolIcon = activeTool?.icon;

    return (
      <div className="flex-none">
        <div
          className={cn(
            "flex flex-col rounded-[28px] p-2 shadow-sm transition-colors cursor-text",
            "bg-zinc-900 border border-zinc-700/50",
            className
          )}
          onClick={() => internalTextareaRef.current?.focus()}
        >
          {/* Hidden file input */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            className="hidden"
            accept="image/*"
          />

          {/* Image preview */}
          {imagePreview && (
            <Dialog open={isImageDialogOpen} onOpenChange={setIsImageDialogOpen}>
              <div className="relative mb-1 w-fit rounded-[1rem] px-1 pt-1">
                <button
                  type="button"
                  className="transition-transform"
                  onClick={() => setIsImageDialogOpen(true)}
                >
                  <img
                    src={imagePreview}
                    alt="Preview"
                    className="h-14 w-14 rounded-[1rem] object-cover"
                  />
                </button>
                <button
                  onClick={handleRemoveImage}
                  className="absolute -right-1 -top-1 z-10 flex h-5 w-5 items-center justify-center rounded-full bg-zinc-700 text-white transition-colors hover:bg-zinc-600"
                  aria-label="Remove image"
                >
                  <XIcon className="h-3 w-3" />
                </button>
              </div>
              <DialogContent>
                <img
                  src={imagePreview}
                  alt="Full preview"
                  className="w-full max-h-[95vh] object-contain rounded-[24px]"
                />
              </DialogContent>
            </Dialog>
          )}

          {/* Textarea */}
          <textarea
            ref={internalTextareaRef}
            rows={1}
            value={value}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            className={cn(
              "custom-scrollbar w-full resize-none border-0 bg-transparent p-3",
              "text-zinc-200 placeholder:text-zinc-500",
              "focus:ring-0 focus-visible:outline-none min-h-[48px]"
            )}
          />

          {/* Toolbar */}
          <div className="mt-0.5 p-1 pt-0">
            <TooltipProvider delayDuration={100}>
              <div className="flex items-center gap-2">
                {/* Attach button */}
                {showAttach && (
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <button
                        type="button"
                        onClick={handlePlusClick}
                        className="flex h-8 w-8 items-center justify-center rounded-full text-zinc-400 transition-colors hover:bg-zinc-800 hover:text-zinc-200 focus-visible:outline-none"
                      >
                        <PlusIcon className="h-5 w-5" />
                        <span className="sr-only">Attach</span>
                      </button>
                    </TooltipTrigger>
                    <TooltipContent side="top" showArrow>
                      <p>Attach image</p>
                    </TooltipContent>
                  </Tooltip>
                )}

                {/* Tools popover */}
                {showTools && tools.length > 0 && (
                  <Popover open={isPopoverOpen} onOpenChange={setIsPopoverOpen}>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <PopoverTrigger asChild>
                          <button
                            type="button"
                            className="flex h-8 items-center gap-1.5 rounded-full px-2.5 text-xs font-medium text-zinc-400 transition-colors hover:bg-zinc-800 hover:text-zinc-200 focus-visible:outline-none"
                          >
                            <Settings2Icon className="h-4 w-4" />
                            {!selectedTool && "Quick Actions"}
                          </button>
                        </PopoverTrigger>
                      </TooltipTrigger>
                      <TooltipContent side="top" showArrow>
                        <p>Quick actions</p>
                      </TooltipContent>
                    </Tooltip>
                    <PopoverContent side="top" align="start">
                      <div className="flex flex-col gap-0.5">
                        {tools.map((tool) => (
                          <button
                            key={tool.id}
                            onClick={() => handleToolSelect(tool.id)}
                            className="flex w-full items-center gap-2.5 rounded-lg p-2 text-left text-sm text-zinc-300 hover:bg-zinc-700/50 transition-colors"
                          >
                            <tool.icon className="h-4 w-4 text-zinc-400" />
                            <span>{tool.name}</span>
                            {tool.extra && (
                              <span className="ml-auto text-[10px] text-zinc-500">
                                {tool.extra}
                              </span>
                            )}
                          </button>
                        ))}
                      </div>
                    </PopoverContent>
                  </Popover>
                )}

                {/* Active tool badge */}
                {activeTool && (
                  <>
                    <div className="h-4 w-px bg-zinc-700" />
                    <button
                      onClick={() => setSelectedTool(null)}
                      className="flex h-7 items-center gap-1.5 rounded-full px-2.5 text-xs font-medium text-cyan-400 hover:bg-zinc-800 transition-colors"
                    >
                      {ActiveToolIcon && <ActiveToolIcon className="h-3.5 w-3.5" />}
                      {activeTool.shortName}
                      <XIcon className="h-3 w-3" />
                    </button>
                  </>
                )}

                {/* Right: Send button */}
                <div className="ml-auto flex items-center gap-1.5">
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <button
                        type="button"
                        disabled={!hasValue || isLoading}
                        onClick={handleSend}
                        className={cn(
                          "flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium transition-all focus-visible:outline-none",
                          "disabled:pointer-events-none",
                          hasValue && !isLoading
                            ? "bg-cyan-600 text-white hover:bg-cyan-500 shadow-lg shadow-cyan-500/20"
                            : "bg-zinc-800 text-zinc-500"
                        )}
                      >
                        {isLoading ? (
                          <LoaderIcon className="h-4 w-4" />
                        ) : (
                          <SendIcon className="h-5 w-5" />
                        )}
                        <span className="sr-only">Send</span>
                      </button>
                    </TooltipTrigger>
                    <TooltipContent side="top" showArrow>
                      <p>{isLoading ? "Processing…" : "Send"}</p>
                    </TooltipContent>
                  </Tooltip>
                </div>
              </div>
            </TooltipProvider>
          </div>
        </div>

        {/* Footer text */}
        {footerText && (
          <p className="text-[10px] text-zinc-600 mt-2 text-center">
            {footerText}
          </p>
        )}
      </div>
    );
  }
);
PromptBox.displayName = "PromptBox";