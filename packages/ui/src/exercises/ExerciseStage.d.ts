import type { JSX } from "react";
import type { Exercise } from "@octobeat/exercises";
export interface ExerciseStageProps {
    exercise: Exercise;
    preview: Exercise;
    /**
     * Índice absoluto del beat actual.
     */
    currentBeat: number;
    /**
     * Repetición actual del ejercicio.
     */
    repetition: number;
    /**
     * Contador que se muestra en la preview del siguiente ejercicio.
     */
    previewRepetition: number;
}
export declare function ExerciseStage({ exercise, preview, currentBeat, repetition, previewRepetition, }: ExerciseStageProps): JSX.Element;
