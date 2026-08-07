"use client";

import { useEffect, useRef, useState } from "react";
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

import { useLibraryStore } from "@/features/library/store";

const HIDE_DELAY = 1200;

const SEEK_SECONDS = 5;

const HOTKEY_CODES = new Set([
    "Space",
    "ArrowLeft",
    "ArrowRight",
    "Home",
    "End",
    "KeyN",
    "KeyP",
]);

const ICON_OUTLINE =
    "drop-shadow(1px 1px 0 #374151) drop-shadow(-1px -1px 0 #374151) drop-shadow(1px -1px 0 #374151) drop-shadow(-1px 1px 0 #374151) drop-shadow(1px 0 0 #374151) drop-shadow(-1px 0 0 #374151) drop-shadow(0 1px 0 #374151) drop-shadow(0 -1px 0 #374151)";

export function PlayerControlsOverlay(): JSX.Element {
    const [visible, setVisible] =
        useState(false);

    const hideTimer = useRef<
        ReturnType<typeof setTimeout> | null
    >(null);

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

    useEffect(() => {
        function wake() {
            setVisible(true);

            if (hideTimer.current) {
                clearTimeout(
                    hideTimer.current,
                );
            }

            hideTimer.current =
                setTimeout(
                    () =>
                        setVisible(
                            false,
                        ),
                    HIDE_DELAY,
                );
        }

        function onKeyDown(
            event: KeyboardEvent,
        ) {
            const target =
                event.target as HTMLElement | null;

            if (
                target &&
                (target.tagName === "INPUT" ||
                    target.tagName ===
                        "TEXTAREA" ||
                    target.isContentEditable)
            ) {
                return;
            }

            if (
                HOTKEY_CODES.has(
                    event.code,
                )
            ) {
                wake();
            }
        }

        window.addEventListener(
            "keydown",
            onKeyDown,
        );

        window.addEventListener(
            "mousemove",
            wake,
        );

        window.addEventListener(
            "mousedown",
            wake,
        );

        return () => {
            window.removeEventListener(
                "keydown",
                onKeyDown,
            );

            window.removeEventListener(
                "mousemove",
                wake,
            );

            window.removeEventListener(
                "mousedown",
                wake,
            );

            if (hideTimer.current) {
                clearTimeout(
                    hideTimer.current,
                );
            }
        };
    }, []);

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
        <div
            className={[
                "pointer-events-none fixed inset-0 z-40 transition-opacity duration-300 ease-out",
                visible
                    ? "opacity-100"
                    : "opacity-0",
            ].join(" ")}
        >
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
