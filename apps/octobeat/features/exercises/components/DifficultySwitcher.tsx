"use client";

import { Button, cn } from "@octobeat/ui";

import { useShortcut } from "@/lib/useShortcut";

import { ShortcutBadge } from "@/features/library/components/ShortcutBadge";
import { useUiStore } from "@/features/ui/store";

import {
    DIFFICULTY_LABELS,
    useDifficultyStore,
} from "../store";
import type { Difficulty } from "../store";

const ORDER: Difficulty[] = [
    "easy",
    "medium",
    "hard",
];

const TEXT_SHADOW =
    "1px 1px 0 #374151, -1px -1px 0 #374151, 1px -1px 0 #374151, -1px 1px 0 #374151, 1px 0 0 #374151, -1px 0 0 #374151, 0 1px 0 #374151, 0 -1px 0 #374151";

export function DifficultySwitcher() {
    const difficulty =
        useDifficultyStore(
            (state) =>
                state.difficulty,
        );

    const setDifficulty =
        useDifficultyStore(
            (state) =>
                state.setDifficulty,
        );

    const revealed = useUiStore(
        (state) => state.revealed,
    );

    useShortcut(
        { code: "Digit1" },
        () =>
            setDifficulty(
                ORDER[0]!,
            ),
    );

    useShortcut(
        { code: "Digit2" },
        () =>
            setDifficulty(
                ORDER[1]!,
            ),
    );

    useShortcut(
        { code: "Digit3" },
        () =>
            setDifficulty(
                ORDER[2]!,
            ),
    );

    return (
        <div className="pointer-events-auto fixed left-1/2 top-8 z-50 flex -translate-x-1/2 items-center gap-1 rounded-md border border-white/10 bg-gray-800/60 p-1.5 shadow-2xl backdrop-blur-md">
            {ORDER.map((option, index) => {
                const active =
                    difficulty === option;

                return (
                    <Button
                        key={option}
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() =>
                            setDifficulty(
                                option,
                            )
                        }
                        className={cn(
                            "relative flex cursor-pointer items-center rounded-sm text-lg text-white",
                            active
                                ? "bg-white/15 shadow-sm"
                                : "hover:bg-white/10",
                        )}
                        style={{
                            textShadow: TEXT_SHADOW,
                        }}
                    >
                        {
                            DIFFICULTY_LABELS[
                                option
                            ]
                        }

                        {revealed && (
                            <span className="absolute -right-2 -top-2">
                                <ShortcutBadge
                                    label={String(
                                        index + 1,
                                    )}
                                />
                            </span>
                        )}
                    </Button>
                );
            })}
        </div>
    );
}
