import { Input as InputPrimitive } from "@base-ui/react/input"

import { cn } from "../lib/utils"

function Input({
  className,
  type,
  ...props
}: InputPrimitive.Props) {
  return (
    <InputPrimitive
      type={type}
      data-slot="input"
      className={cn(
        "flex h-8 w-full rounded-lg border border-input bg-background px-2.5 text-sm text-foreground shadow-xs transition-[color,box-shadow] outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50",
        className
      )}
      {...props}
    />
  )
}

export { Input }
