import type { JSX, ReactNode } from "react";
import type { Exercise } from "@octobeat/exercises";
export interface ExerciseRendererProps {
    exercise: Exercise;
    /**
     * Título del libro al que pertenece el ejercicio.
     */
    bookTitle?: string;
    /**
     * Título de la sección a la que pertenece el ejercicio.
     */
    setTitle?: string;
    /**
     * Encabezado personalizado (libro · sección) que sustituye a la
     * línea de títulos por defecto. Solo se usa en la línea activa.
     */
    header?: ReactNode;
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
export declare function ExerciseRenderer({ exercise, bookTitle, setTitle, header, currentBeat, repetition, preview, lastPass, }: ExerciseRendererProps): JSX.Element;
