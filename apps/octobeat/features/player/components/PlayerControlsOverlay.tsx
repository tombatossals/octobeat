"use client";

import type { JSX } from "react";
import {
    FastForward,
    Pause,
    Play,
    Rewind,
    SkipBack,
    SkipForward,
} from "lucide-react";

import { usePlayerStore } from "@octobeat/player";
import { SeekBar, TimeDisplay } from "@octobeat/ui";

import { ShortcutBadge } from "@/features/library/components/ShortcutBadge";
import { useLibraryStore } from "@/features/library/store";
import { useUiStore } from "@/features/ui/store";

const SEEK_SECONDS = 5;

const ICON_OUTLINE =
    "drop-shadow(1px 1px 0 #374151) drop-shadow(-1px -1px 0 #374151) drop-shadow(1px -1px 0 #374151) drop-shadow(-1px 1px 0 #374151) drop-shadow(1px 0 0 #374151) drop-shadow(-1px 0 0 #374151) drop-shadow(0 1px 0 #374151) drop-shadow(0 -1px 0 #374151)";

export function PlayerControlsOverlay(): JSX.Element {
    const playing = usePlayerStore(
        (state) => state.playing,
    );

    const playPause = usePlayerStore(
        (state) => state.playPause,
    );

    const seek = usePlayerStore(
        (state) => state.seek,
    );

    const currentTime =
        usePlayerStore(
            (state) =>
                state.currentTime,
        );

    const duration = usePlayerStore(
        (state) => state.duration,
    );

    const next = useLibraryStore(
        (state) => state.next,
    );

    const previous =
        useLibraryStore(
            (state) => state.previous,
        );

    const revealed = useUiStore(
        (state) => state.revealed,
    );

    const percentage =
        duration > 0
            ? Math.round(
                  (currentTime /
                      duration) *
                      100,
              )
            : 0;

    function seekRelative(
        seconds: number,
    ) {
        seek(
            Math.max(
                0,
                Math.min(
                    duration,
                    currentTime +
                        seconds,
                ),
            ),
        );
    }

    return (
        <div className="pointer-events-none fixed inset-0 z-40">
            <button
                type="button"
                aria-label="Previous song"
                onClick={() =>
                    void previous()
                }
                className="pointer-events-auto absolute left-[8%] top-1/2 flex h-14 w-14 -translate-y-1/2 cursor-pointer items-center justify-center rounded-full bg-black/10 text-white opacity-50 transition-all hover:bg-black/50 hover:opacity-100"
                style={{
                    filter: ICON_OUTLINE,
                }}
            >
                <SkipBack className="h-7 w-7" />

                {revealed && (
                    <span className="absolute -right-2 -top-2">
                        <ShortcutBadge label="P" />
                    </span>
                )}
            </button>

            <button
                type="button"
                aria-label="Rewind 5 seconds"
                onClick={() =>
                    seekRelative(
                        -SEEK_SECONDS,
                    )
                }
                className="pointer-events-auto absolute left-[25%] top-1/2 flex h-12 w-12 -translate-y-1/2 cursor-pointer items-center justify-center rounded-full bg-black/10 text-white opacity-50 transition-all hover:bg-black/50 hover:opacity-100"
                style={{
                    filter: ICON_OUTLINE,
                }}
            >
                <Rewind className="h-6 w-6" />

                {revealed && (
                    <span className="absolute -right-2 -top-2">
                        <ShortcutBadge label="←" />
                    </span>
                )}
            </button>

            <button
                type="button"
                aria-label={
                    playing
                        ? "Pause"
                        : "Play"
                }
                onClick={() =>
                    void playPause()
                }
                className="pointer-events-auto absolute left-1/2 top-1/2 flex h-20 w-20 -translate-x-1/2 -translate-y-1/2 cursor-pointer items-center justify-center rounded-full bg-black/10 text-white opacity-50 transition-all hover:bg-black/50 hover:opacity-100"
                style={{
                    filter: ICON_OUTLINE,
                }}
            >
                {playing ? (
                    <Pause className="h-10 w-10" />
                ) : (
                    <Play className="h-10 w-10" />
                )}

                {revealed && (
                    <span className="absolute -right-2 -top-2">
                        <ShortcutBadge label="Space" />
                    </span>
                )}
            </button>

            <button
                type="button"
                aria-label="Forward 5 seconds"
                onClick={() =>
                    seekRelative(
                        SEEK_SECONDS,
                    )
                }
                className="pointer-events-auto absolute right-[25%] top-1/2 flex h-12 w-12 -translate-y-1/2 cursor-pointer items-center justify-center rounded-full bg-black/10 text-white opacity-50 transition-all hover:bg-black/50 hover:opacity-100"
                style={{
                    filter: ICON_OUTLINE,
                }}
            >
                <FastForward className="h-6 w-6" />

                {revealed && (
                    <span className="absolute -right-2 -top-2">
                        <ShortcutBadge label="→" />
                    </span>
                )}
            </button>

            <button
                type="button"
                aria-label="Next song"
                onClick={() =>
                    void next()
                }
                className="pointer-events-auto absolute right-[8%] top-1/2 flex h-14 w-14 -translate-y-1/2 cursor-pointer items-center justify-center rounded-full bg-black/10 text-white opacity-50 transition-all hover:bg-black/50 hover:opacity-100"
                style={{
                    filter: ICON_OUTLINE,
                }}
            >
                <SkipForward className="h-7 w-7" />

                {revealed && (
                    <span className="absolute -right-2 -top-2">
                        <ShortcutBadge label="N" />
                    </span>
                )}
            </button>

            <div className="pointer-events-auto absolute bottom-10 left-1/2 w-[min(80vw,36rem)] -translate-x-1/2">
                <SeekBar />

                <div className="mt-2 flex items-center justify-between text-sm text-white">
                    <TimeDisplay />

                    <span className="tabular-nums">
                        {percentage}%
                    </span>
                </div>
            </div>
        </div>
    );
}
