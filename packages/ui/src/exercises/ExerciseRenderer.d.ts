import type { JSX } from "react";
import type { Exercise } from "@octobeat/exercises";
export interface ExerciseRendererProps {
    exercise: Exercise;
    /**
     * Índice absoluto del beat actual.
     */
    currentBeat: number;
}
export declare function ExerciseRenderer({ exercise, currentBeat, }: ExerciseRendererProps): JSX.Element;
