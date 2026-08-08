"use client";

import type { JSX } from "react";

import { usePlayerStore } from "@octobeat/player";

import { lyricAtTime } from "../api";

import { useLyricsStore } from "../store";

const TEXT_OUTLINE =
    "1px 1px 0 #374151, -1px -1px 0 #374151, 1px -1px 0 #374151, -1px 1px 0 #374151, 1px 0 0 #374151, -1px 0 0 #374151, 0 1px 0 #374151, 0 -1px 0 #374151";

export function LyricsOverlay(): JSX.Element | null {
    const lyrics = useLyricsStore(
        (state) => state.lyrics,
    );

    const currentTime =
        usePlayerStore(
            (state) =>
                state.currentTime,
        );

    if (lyrics.length === 0) {
        return null;
    }

    const line = lyricAtTime(
        lyrics,
        currentTime,
    );

    if (!line) {
        return null;
    }

    return (
        <div className="pointer-events-none absolute inset-x-0 bottom-44 z-20 flex justify-center px-8">
            <div className="max-w-3xl rounded-lg border border-white/10 bg-gray-800/60 px-6 py-2 shadow-2xl backdrop-blur-md">
                <p
                    className="text-center text-xl font-bold leading-snug text-white"
                    style={{
                        textShadow:
                            TEXT_OUTLINE,
                    }}
                >
                    {line.text}
                </p>
            </div>
        </div>
    );
}
