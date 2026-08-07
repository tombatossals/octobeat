"use client";

import { Button, cn } from "@octobeat/ui";

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

    return (
        <div className="pointer-events-auto fixed left-1/2 top-4 z-50 flex -translate-x-1/2 items-center gap-1 rounded-full border border-border/60 bg-background/70 p-1 shadow-2xl backdrop-blur-md">
            {ORDER.map((option) => {
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
                            "rounded-full",
                            active
                                ? "bg-background text-foreground shadow-sm"
                                : "text-muted-foreground hover:text-foreground",
                        )}
                    >
                        {
                            DIFFICULTY_LABELS[
                                option
                            ]
                        }
                    </Button>
                );
            })}
        </div>
    );
}
