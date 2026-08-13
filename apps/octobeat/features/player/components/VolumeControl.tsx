"use client";

import { useEffect, useRef, useState } from "react";
import {
    Volume1,
    Volume2,
    VolumeX,
} from "lucide-react";

import { usePlayerStore } from "@octobeat/player";

import { useShortcut } from "@/lib/useShortcut";

import { ShortcutBadge } from "@/features/library/components/ShortcutBadge";
import { useUiStore } from "@/features/ui/store";

const ICON_OUTLINE =
    "drop-shadow(1px 1px 0 var(--icon-outline)) drop-shadow(-1px -1px 0 var(--icon-outline)) drop-shadow(1px -1px 0 var(--icon-outline)) drop-shadow(-1px 1px 0 var(--icon-outline)) drop-shadow(1px 0 0 var(--icon-outline)) drop-shadow(-1px 0 0 var(--icon-outline)) drop-shadow(0 1px 0 var(--icon-outline)) drop-shadow(0 -1px 0 var(--icon-outline))";

const TRACK_HEIGHT = 112;

const VOLUME_STEP = 0.05;

export function VolumeControl() {
    const volume = usePlayerStore(
        (state) => state.volume,
    );

    const setVolume = usePlayerStore(
        (state) => state.setVolume,
    );

    const revealed = useUiStore(
        (state) => state.revealed,
    );

    const [open, setOpen] =
        useState(false);

    const trackRef =
        useRef<HTMLDivElement>(null);

    const hideTimer =
        useRef<number | null>(null);

    function scheduleHide() {
        if (
            hideTimer.current !== null
        ) {
            window.clearTimeout(
                hideTimer.current,
            );
        }

        hideTimer.current =
            window.setTimeout(() => {
                setOpen(false);
            }, 1000);
    }

    function revealSlider() {
        setOpen(true);

        scheduleHide();
    }

    useEffect(() => {
        return () => {
            if (
                hideTimer.current !== null
            ) {
                window.clearTimeout(
                    hideTimer.current,
                );
            }
        };
    }, []);

    useShortcut(
        { code: "ArrowUp" },
        () => {
            setVolume(
                volume + VOLUME_STEP,
            );

            revealSlider();

            useUiStore.getState().wakePointer();
        },
    );

    useShortcut(
        { code: "ArrowDown" },
        () => {
            setVolume(
                volume - VOLUME_STEP,
            );

            revealSlider();

            useUiStore.getState().wakePointer();
        },
    );

    useEffect(() => {
        if (!open) {
            return;
        }

        function handlePointerDown(
            event: PointerEvent,
        ) {
            const track =
                trackRef.current;

            if (
                track &&
                !track.contains(
                    event.target as Node,
                )
            ) {
                setOpen(false);

                if (
                    hideTimer.current !==
                    null
                ) {
                    window.clearTimeout(
                        hideTimer.current,
                    );
                }
            }
        }

        window.addEventListener(
            "pointerdown",
            handlePointerDown,
        );

        return () => {
            window.removeEventListener(
                "pointerdown",
                handlePointerDown,
            );
        };
    }, [open]);

    function handleTrackPointerDown(
        event: React.PointerEvent<HTMLDivElement>,
    ) {
        event.preventDefault();

        event.currentTarget.setPointerCapture(
            event.pointerId,
        );

        updateFromPointer(
            event,
        );

        scheduleHide();
    }

    function handleTrackPointerMove(
        event: React.PointerEvent<HTMLDivElement>,
    ) {
        if (event.buttons > 0) {
            updateFromPointer(
                event,
            );

            scheduleHide();
        }
    }

    function updateFromPointer(
        event: React.PointerEvent<HTMLDivElement>,
    ) {
        const track =
            event.currentTarget;

        const rect =
            track.getBoundingClientRect();

        const ratio =
            1 -
            (event.clientY -
                rect.top) /
                rect.height;

        setVolume(
            Math.max(
                0,
                Math.min(1, ratio),
            ),
        );
    }

    const percentage =
        Math.round(
            volume * 100,
        );

    const Icon =
        volume === 0
            ? VolumeX
            : volume < 0.5
              ? Volume1
              : Volume2;

    return (
        <div className="relative">
            <button
                type="button"
                aria-label="Volume"
                aria-pressed={open}
                onClick={() => {
                    if (open) {
                        setOpen(false);
                    } else {
                        revealSlider();
                    }
                }}
                className="relative flex cursor-pointer items-center text-foreground transition-colors outline-none focus:outline-none hover:text-muted-foreground"
            >
                <span
                    style={{
                        filter: ICON_OUTLINE,
                    }}
                >
                    <Icon className="h-7 w-7" />
                </span>

                {revealed && (
                    <span className="absolute -right-4 -top-2">
                        <ShortcutBadge
                            label="↑"
                            className="border border-border"
                        />
                    </span>
                )}

                {revealed && (
                    <span className="absolute -bottom-2 -right-4">
                        <ShortcutBadge
                            label="↓"
                            className="border border-border"
                        />
                    </span>
                )}
            </button>

            {open && (
                <div className="absolute left-1/2 top-full mt-3 flex -translate-x-1/2 flex-col items-center rounded-lg border border-border bg-background/60 p-1.5 shadow-2xl backdrop-blur-md">
                    <div
                        ref={trackRef}
                        role="slider"
                        aria-label="Volume"
                        aria-valuemin={0}
                        aria-valuemax={100}
                        aria-valuenow={percentage}
                        onPointerDown={
                            handleTrackPointerDown
                        }
                        onPointerMove={
                            handleTrackPointerMove
                        }
                        className="relative h-24 w-3 cursor-pointer touch-none"
                        style={{
                            height: TRACK_HEIGHT,
                        }}
                    >
                        <div className="absolute bottom-0 left-1/2 top-0 w-1.5 -translate-x-1/2 overflow-hidden rounded-full bg-foreground/20">
                            <div
                                className="absolute bottom-0 left-0 right-0 bg-foreground"
                                style={{
                                    height: `${percentage}%`,
                                }}
                            />
                        </div>

                        <div
                            className="absolute left-1/2 h-3 w-3 -translate-x-1/2 rounded-full bg-foreground shadow"
                            style={{
                                top: `calc(${100 - percentage}% - 6px)`,
                            }}
                        />

                        <div
                            className="pointer-events-none absolute left-full ml-2 whitespace-nowrap text-xs font-medium tabular-nums text-foreground"
                            style={{
                                top: `calc(${100 - percentage}% - 6px)`,
                                textShadow:
                                    "1px 1px 0 var(--icon-outline), -1px -1px 0 var(--icon-outline), 1px 0 0 var(--icon-outline), -1px 0 0 var(--icon-outline), 0 1px 0 var(--icon-outline), 0 -1px 0 var(--icon-outline)",
                            }}
                        >
                            {percentage}%
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
