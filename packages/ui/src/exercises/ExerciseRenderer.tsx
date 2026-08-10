"use client";

import type { JSX } from "react";

import type { Exercise } from "@octobeat/exercises";

import { ExerciseTimeline } from "./ExerciseTimeline";

export interface ExerciseRendererProps {
    exercise: Exercise;

    /**
     * Índice absoluto del beat actual.
     */
    currentBeat: number;

    /**
     * Repetición actual del ejercicio. Arranca en 1 y al llegar a 20
     * vuelve a empezar.
     */
    repetition?: number;
}

export function ExerciseRenderer({
    exercise,
    currentBeat,
    repetition = 1,
}: ExerciseRendererProps): JSX.Element {
    return (
        <div className="flex items-center gap-3 rounded-lg border border-neutral-200 bg-white px-3 py-1 shadow-2xl">
            <div className="min-w-0 flex-1">
                <ExerciseTimeline
                    exercise={exercise}
                    currentBeat={currentBeat}
                />
            </div>

            <div className="flex shrink-0 items-center border-l border-neutral-200 pl-3 pr-0.5">
                <span className="flex h-8 min-w-8 items-center justify-center rounded-full border-2 border-blue-600 px-1.5 font-mono text-base font-black text-blue-700">
                    {repetition}
                </span>
            </div>
        </div>
    );
}
