"use client"

import type { ReactNode } from "react"
import { Select } from "@base-ui/react/select"
import { Check, ChevronDown } from "lucide-react"

import { cn } from "../lib/utils"

interface MultiSelectOption {
  value: string
  label: ReactNode
}

interface MultiSelectProps {
  value: string[]
  onValueChange: (value: string[]) => void
  options: ReadonlyArray<MultiSelectOption>
  placeholder?: string
  countLabel?: (count: number) => ReactNode
  className?: string
  popupClassName?: string
}

function MultiSelect({
  value,
  onValueChange,
  options,
  placeholder = "Select...",
  countLabel = (count) =>
    count === 1 ? "1 selected" : `${count} selected`,
  className,
  popupClassName,
}: MultiSelectProps) {
  return (
    <Select.Root
      multiple
      value={value}
      onValueChange={onValueChange}
    >
      <Select.Trigger
        data-slot="multi-select"
        className={cn(
          "flex h-8 w-full items-center justify-between gap-2 rounded-lg border border-input bg-background px-2.5 text-sm text-foreground shadow-xs outline-none transition-[color,box-shadow] focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 data-popup-open:border-ring",
          className
        )}
      >
        <Select.Value className="truncate">
          {(selected: string[]) =>
            selected.length > 0 ? (
              <span className="text-foreground">
                {countLabel(selected.length)}
              </span>
            ) : (
              <span className="text-muted-foreground">
                {placeholder}
              </span>
            )
          }
        </Select.Value>

        <Select.Icon className="shrink-0 text-muted-foreground">
          <ChevronDown className="size-4" />
        </Select.Icon>
      </Select.Trigger>

      <Select.Portal>
        <Select.Positioner className="z-[95]">
          <Select.Popup
            className={cn(
              "max-h-72 w-[var(--anchor-width)] overflow-y-auto rounded-lg border border-border bg-popover p-1 text-popover-foreground shadow-lg",
              popupClassName
            )}
          >
            <Select.List>
              {options.map((option) => {
                const checked = value.includes(option.value)

                return (
                  <Select.Item
                    key={option.value}
                    value={option.value}
                    className={cn(
                      "flex cursor-pointer select-none items-center gap-2 rounded-md px-2 py-1.5 text-sm outline-none data-highlighted:bg-accent data-highlighted:text-accent-foreground",
                      checked &&
                        "text-foreground"
                    )}
                  >
                    <Select.ItemIndicator className="shrink-0 text-primary">
                      <Check className="size-4" />
                    </Select.ItemIndicator>

                    <Select.ItemText className="truncate">
                      {option.label}
                    </Select.ItemText>
                  </Select.Item>
                )
              })}
            </Select.List>
          </Select.Popup>
        </Select.Positioner>
      </Select.Portal>
    </Select.Root>
  )
}

export { MultiSelect }
