import type { JSX } from "react";
import type { Exercise } from "@octobeat/exercises";
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
export declare function ExerciseRenderer({ exercise, currentBeat, repetition, }: ExerciseRendererProps): JSX.Element;
