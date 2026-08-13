"use client";

export function ShortcutBadge({
    label,
    className = "",
}: {
    label: string;
    className?: string;
}) {
    return (
        <kbd
            className={`rounded bg-foreground/15 px-1.5 py-0.5 text-[10px] font-medium leading-none text-foreground/80 ${className}`}
        >
            {label}
        </kbd>
    );
}
