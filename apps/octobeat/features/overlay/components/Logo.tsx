"use client";

export function Logo() {
    return (
        <div className="pointer-events-none fixed left-4 top-4 z-50 flex items-center rounded-full border border-border bg-background/60 pl-0 pr-5 shadow-2xl backdrop-blur-xl">
            <img
                src="/logo.png"
                alt="Octobeat logo"
                className="h-15 w-auto object-contain"
            />

            <span
                className="mx-1.5 h-8 w-px bg-foreground"
                style={{
                    boxShadow:
                        "1px 1px 0 var(--icon-outline), -1px -1px 0 var(--icon-outline), 1px -1px 0 var(--icon-outline), -1px 1px 0 var(--icon-outline), 1px 0 0 var(--icon-outline), -1px 0 0 var(--icon-outline), 0 1px 0 var(--icon-outline), 0 -1px 0 var(--icon-outline)",
                }}
                aria-hidden="true"
            />

            <span
                className="text-4xl font-black leading-none tracking-[-0.08em] text-foreground"
                style={{
                    textShadow:
                        "1px 1px 0 var(--icon-outline), -1px -1px 0 var(--icon-outline), 1px -1px 0 var(--icon-outline), -1px 1px 0 var(--icon-outline), 1px 0 0 var(--icon-outline), -1px 0 0 var(--icon-outline), 0 1px 0 var(--icon-outline), 0 -1px 0 var(--icon-outline)",
                }}
            >
                Octobeat
            </span>
        </div>
    );
}
