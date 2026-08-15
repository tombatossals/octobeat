"use client";

import { Button, cn } from "@octobeat/ui";

import { useShortcut } from "@/lib/useShortcut";

import { ShortcutBadge } from "@/features/library/components/ShortcutBadge";
import { useUiStore } from "@/features/ui/store";
import { useLibraryStore } from "@/features/library/store";

import {
    SPEED_FACTOR,
    SPEED_LABELS,
    useSpeedStore,
} from "../store";
import type { Speed } from "../store";

const ORDER: Speed[] = [
    "x1",
    "x2",
    "x4",
];

const TEXT_SHADOW =
    "1px 1px 0 var(--icon-outline), -1px -1px 0 var(--icon-outline), 1px -1px 0 var(--icon-outline), -1px 1px 0 var(--icon-outline), 1px 0 0 var(--icon-outline), -1px 0 0 var(--icon-outline), 0 1px 0 var(--icon-outline), 0 -1px 0 var(--icon-outline)";

export function SpeedSwitcher() {
    const speed =
        useSpeedStore(
            (state) =>
                state.speed,
        );

    const setSpeed =
        useSpeedStore(
            (state) =>
                state.setSpeed,
        );

    const revealed = useUiStore(
        (state) => state.revealed,
    );

    const bpm = useLibraryStore(
        (state) =>
            state.dataset?.metadata.bpm,
    );

    const currentBpm =
        bpm != null
            ? Math.round(
                  bpm *
                      SPEED_FACTOR[speed],
              )
            : null;

    useShortcut(
        { code: "Digit1" },
        () =>
            setSpeed(
                ORDER[0]!,
            ),
    );

    useShortcut(
        { code: "Digit2" },
        () =>
            setSpeed(
                ORDER[1]!,
            ),
    );

    useShortcut(
        { code: "Digit4" },
        () =>
            setSpeed(
                ORDER[2]!,
            ),
    );

    return (
        <div className="pointer-events-auto fixed left-4 top-[5.5rem] z-50 flex flex-col gap-1 short:left-2 short:top-[4.5rem]">
            <div className="px-1 font-mono text-[10px] font-black uppercase tracking-wider text-foreground">
                Speed
            </div>

            <div className="flex items-center gap-1 rounded-md border border-border bg-background/60 p-1.5 shadow-2xl backdrop-blur-md short:p-1">
                {ORDER.map((option) => {
                const active =
                    speed === option;

                return (
                    <Button
                        key={option}
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() =>
                            setSpeed(
                                option,
                            )
                        }
                        className={cn(
                            "relative flex cursor-pointer items-center rounded-sm text-lg text-foreground short:text-sm",
                            active
                                ? "bg-foreground/15 shadow-sm"
                                : "hover:bg-foreground/10",
                        )}
                        style={{
                            textShadow: TEXT_SHADOW,
                        }}
                    >
                        {
                            SPEED_LABELS[
                                option
                            ]
                        }

                        {revealed && (
                            <span className="absolute -right-2 -top-4">
                                <ShortcutBadge
                                    label={String(
                                        SPEED_FACTOR[
                                            option
                                        ],
                                    )}
                                    className="border border-border"
                                />
                            </span>
                        )}
                    </Button>
                );
            })}

            {bpm != null && currentBpm != null && (
                <div className="ml-2 flex items-center gap-1.5 border-l border-border pl-2 pr-1 font-mono text-sm text-foreground short:text-xs">
                    <span>BPM</span>

                    <span
                        className="font-black"
                        style={{
                            textShadow: TEXT_SHADOW,
                        }}
                    >
                        {currentBpm}
                    </span>
                </div>
            )}
            </div>
        </div>
    );
}
