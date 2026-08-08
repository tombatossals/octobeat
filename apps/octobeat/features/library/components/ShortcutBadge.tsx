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
            className={`rounded bg-white/15 px-1.5 py-0.5 text-[10px] font-medium leading-none text-white/80 ${className}`}
        >
            {label}
        </kbd>
    );
}
