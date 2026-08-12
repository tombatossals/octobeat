import { create } from "zustand";

export type Difficulty =
    | "easy"
    | "medium"
    | "hard";

export const DIFFICULTY_FACTOR:
    Record<Difficulty, number> = {
        easy: 1,
        medium: 2,
        hard: 4,
    };

export const DIFFICULTY_LABELS:
    Record<Difficulty, string> = {
        easy: "1x",
        medium: "2x",
        hard: "4x",
    };

interface DifficultyState {
    difficulty: Difficulty;

    setDifficulty(
        difficulty: Difficulty,
    ): void;
}

export const useDifficultyStore =
    create<DifficultyState>((set) => ({
        difficulty: "easy",

        setDifficulty(difficulty) {
            set({
                difficulty,
            });
        },
    }));
