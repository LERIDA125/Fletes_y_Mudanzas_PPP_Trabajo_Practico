import * as React from "react";

import { cn } from "@/lib/utils/cn";

export function Button({
  className,
  variant = "default",
  size = "default",
  ...props
}: React.ComponentProps<"button"> & {
  variant?: "default" | "outline" | "ghost";
  size?: "default" | "sm" | "icon";
}) {
  return (
    <button
      className={cn(
        "inline-flex cursor-pointer items-center justify-center rounded-lg text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 disabled:pointer-events-none disabled:opacity-50",
        variant === "default" && "bg-slate-950 text-white hover:bg-slate-800",
        variant === "outline" &&
          "border border-slate-200 bg-white hover:bg-slate-50 text-slate-700",
        variant === "ghost" && "hover:bg-slate-100 text-slate-700",
        size === "default" && "h-9 px-4 py-2 gap-2",
        size === "sm" && "h-8 rounded-lg px-3 text-xs gap-1.5",
        size === "icon" && "size-9",
        className,
      )}
      {...props}
    />
  );
}
