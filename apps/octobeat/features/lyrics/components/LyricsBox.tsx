"use client";

import { usePlayerStore } from "@octobeat/player";

import { useLibraryStore } from "@/features/library/store";

import { activeLyricLine } from "../activeLine";

/**
 * Compact synced-lyrics box showing only the currently active line.
 *
 * Renders a small centred pill at the top of the screen with the text
 * of the line being sung. It is purely informational: it never captures
 * pointer events and hides when no line is active (or the dataset has
 * no lyrics).
 */
export function LyricsBox() {
    const lyrics = useLibraryStore(
        (state) => state.dataset?.lyrics,
    );

    const currentTime = usePlayerStore(
        (state) => state.currentTime,
    );

    const active = activeLyricLine(
        lyrics,
        currentTime,
    );

    if (!active) {
        return null;
    }

    return (
        <div className="pointer-events-none fixed left-1/2 top-[4.5rem] z-40 -translate-x-1/2 short:top-16">
            <div
                key={active.index}
                title={active.text}
                className="animate-[fadeIn_200ms_ease-out] rounded-lg border border-neutral-300/60 bg-background/60 px-5 py-2 text-center backdrop-blur-xl short:px-4 short:py-1.5 dark:border-neutral-600/60"
                style={{
                    boxShadow:
                        "var(--summary-shadow)",
                }}
            >
                <span className="block max-w-[min(60vw,32rem)] truncate text-lg font-semibold leading-tight text-foreground short:text-base">
                    {active.text}
                </span>
            </div>
        </div>
    );
}
