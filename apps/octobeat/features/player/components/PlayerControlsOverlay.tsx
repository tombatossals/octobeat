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
    "drop-shadow(1px 1px 0 var(--icon-outline)) drop-shadow(-1px -1px 0 var(--icon-outline)) drop-shadow(1px -1px 0 var(--icon-outline)) drop-shadow(-1px 1px 0 var(--icon-outline)) drop-shadow(1px 0 0 var(--icon-outline)) drop-shadow(-1px 0 0 var(--icon-outline)) drop-shadow(0 1px 0 var(--icon-outline)) drop-shadow(0 -1px 0 var(--icon-outline))";

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
            <div className="pointer-events-auto absolute left-[8%] top-1/2 -translate-y-1/2">
                <button
                    type="button"
                    aria-label="Previous song"
                    onClick={() =>
                        void previous()
                    }
                    className="flex cursor-pointer items-center justify-center text-foreground opacity-50 transition-all hover:opacity-100"
                    style={{
                        filter: ICON_OUTLINE,
                    }}
                >
                    <SkipBack className="h-9 w-9" />
                </button>

                {revealed && (
                    <span className="absolute left-1/2 -top-6 -translate-x-1/2">
                        <ShortcutBadge
                            label="P"
                            className="border border-border"
                        />
                    </span>
                )}
            </div>

            <div className="pointer-events-auto absolute left-[25%] top-1/2 -translate-y-1/2">
                <button
                    type="button"
                    aria-label="Rewind 5 seconds"
                    onClick={() =>
                        seekRelative(
                            -SEEK_SECONDS,
                        )
                    }
                    className="flex cursor-pointer items-center justify-center text-foreground opacity-50 transition-all hover:opacity-100"
                    style={{
                        filter: ICON_OUTLINE,
                    }}
                >
                    <Rewind className="h-8 w-8" />
                </button>

                {revealed && (
                    <span className="absolute left-1/2 -top-6 -translate-x-1/2">
                        <ShortcutBadge
                            label="←"
                            className="border border-border"
                        />
                    </span>
                )}
            </div>

            <div className="pointer-events-auto absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
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
                    className="flex cursor-pointer items-center justify-center text-foreground opacity-50 transition-all hover:opacity-100"
                    style={{
                        filter: ICON_OUTLINE,
                    }}
                >
                    {playing ? (
                        <Pause className="h-14 w-14" />
                    ) : (
                        <Play className="h-14 w-14" />
                    )}
                </button>

                {revealed && (
                    <span className="absolute left-1/2 -top-6 -translate-x-1/2">
                        <ShortcutBadge
                            label="Space"
                            className="border border-border"
                        />
                    </span>
                )}
            </div>

            <div className="pointer-events-auto absolute right-[25%] top-1/2 -translate-y-1/2">
                <button
                    type="button"
                    aria-label="Forward 5 seconds"
                    onClick={() =>
                        seekRelative(
                            SEEK_SECONDS,
                        )
                    }
                    className="flex cursor-pointer items-center justify-center text-foreground opacity-50 transition-all hover:opacity-100"
                    style={{
                        filter: ICON_OUTLINE,
                    }}
                >
                    <FastForward className="h-8 w-8" />
                </button>

                {revealed && (
                    <span className="absolute left-1/2 -top-6 -translate-x-1/2">
                        <ShortcutBadge
                            label="→"
                            className="border border-border"
                        />
                    </span>
                )}
            </div>

            <div className="pointer-events-auto absolute right-[8%] top-1/2 -translate-y-1/2">
                <button
                    type="button"
                    aria-label="Next song"
                    onClick={() =>
                        void next()
                    }
                    className="flex cursor-pointer items-center justify-center text-foreground opacity-50 transition-all hover:opacity-100"
                    style={{
                        filter: ICON_OUTLINE,
                    }}
                >
                    <SkipForward className="h-9 w-9" />
                </button>

                {revealed && (
                    <span className="absolute left-1/2 -top-6 -translate-x-1/2">
                        <ShortcutBadge
                            label="N"
                            className="border border-border"
                        />
                    </span>
                )}
            </div>

            <div className="pointer-events-auto absolute bottom-0 left-0 right-0 flex justify-center px-6 pb-4">
                <div className="w-full max-w-md">
                    <SeekBar />

                    <div className="mt-2 flex items-center justify-between text-sm text-foreground">
                        <TimeDisplay />

                        <span className="tabular-nums">
                            {percentage}%
                        </span>
                    </div>
                </div>
            </div>
        </div>
    );
}
