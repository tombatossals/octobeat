import type { JSX } from "react";
import type { Exercise } from "@octobeat/exercises";
export interface ExerciseStageProps {
    exercise: Exercise;
    /**
     * Título del libro al que pertenece el ejercicio.
     */
    exerciseBookTitle?: string;
    /**
     * Título de la sección a la que pertenece el ejercicio.
     */
    exerciseSetTitle?: string;
    preview: Exercise;
    /**
     * Título del libro al que pertenece la preview.
     */
    previewBookTitle?: string;
    /**
     * Título de la sección a la que pertenece la preview.
     */
    previewSetTitle?: string;
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
export declare function ExerciseStage({ exercise, exerciseBookTitle, exerciseSetTitle, preview, previewBookTitle, previewSetTitle, currentBeat, repetition, previewRepetition, }: ExerciseStageProps): JSX.Element;
