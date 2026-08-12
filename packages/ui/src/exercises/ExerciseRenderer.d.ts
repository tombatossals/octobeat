import type { JSX } from "react";
import type { Exercise } from "@octobeat/exercises";
export interface ExerciseRendererProps {
    exercise: Exercise;
    /**
     * Índice absoluto del beat actual.
     */
    currentBeat: number;
    /**
     * Repetición actual del ejercicio. Arranca en 1 y avanza
     * según el valor configurado de repeticiones por línea.
     */
    repetition?: number;
    /**
     * Renderiza una vista previa: sin beat activo ni badge de
     * repetición, reservada para ejercicios aún no activos.
     */
    preview?: boolean;
    /**
     * Última repetición de la línea; propaga a la timeline.
     */
    lastPass?: boolean;
}
export declare function ExerciseRenderer({ exercise, currentBeat, repetition, preview, lastPass, }: ExerciseRendererProps): JSX.Element;
