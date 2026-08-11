"use client";

import type { JSX } from "react";

import { usePlayerStore } from "@octobeat/player";

import { useLibraryStore } from "@/features/library/store";

const NUMBER_OUTLINE =
    "2px 2px 0 #374151, -2px -2px 0 #374151, 2px -2px 0 #374151, -2px 2px 0 #374151, 2px 0 0 #374151, -2px 0 0 #374151, 0 2px 0 #374151, 0 -2px 0 #374151";

/**
 * Countdown over the Rock Band count-in lead-in.
 *
 * When a dataset starts with a count-in (a few seconds of stick clicks
 * before the song really kicks in), this overlay shows the seconds
 * remaining until the song starts, so playback lands on the beat.
 */
export function CountdownOverlay(): JSX.Element | null {
    const dataset = useLibraryStore(
        (state) => state.dataset,
    );

    const currentTime =
        usePlayerStore(
            (state) =>
                state.currentTime,
        );

    if (!dataset) {
        return null;
    }

    const {
        countInStart,
        songStart,
    } = dataset.songmap.timing;

    if (
        countInStart == null ||
        songStart == null ||
        songStart <= countInStart
    ) {
        return null;
    }

    if (
        currentTime < countInStart ||
        currentTime >= songStart
    ) {
        return null;
    }

    const remaining = Math.max(
        1,
        Math.ceil(
            songStart - currentTime,
        ),
    );

    return (
        <div className="pointer-events-none fixed inset-0 z-30 flex items-center justify-center">
            <div
                key={remaining}
                className="animate-[countPulse_1s_ease-in-out] text-[16rem] font-black leading-none text-white"
                style={{
                    textShadow:
                        NUMBER_OUTLINE,
                }}
            >
                {remaining}
            </div>
        </div>
    );
}
