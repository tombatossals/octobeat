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
}

export function ExerciseRenderer({
    exercise,
    currentBeat,
}: ExerciseRendererProps): JSX.Element {
    return (
        <div className="rounded-lg border border-neutral-200 bg-white px-3 py-1 shadow-2xl">
            <ExerciseTimeline
                exercise={exercise}
                currentBeat={currentBeat}
            />
        </div>
    );
}