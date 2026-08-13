"use client";

import type { JSX } from "react";

import type { Exercise } from "@octobeat/exercises";

import { cn } from "../lib/utils";

import { ExerciseTimeline } from "./ExerciseTimeline";

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

export function ExerciseRenderer({
    exercise,
    currentBeat,
    repetition = 1,
    preview = false,
    lastPass = false,
}: ExerciseRendererProps): JSX.Element {
    return (
        <div className="flex w-full items-center gap-3 rounded-lg border border-neutral-200 bg-white px-3 py-1 shadow-2xl">
            <div className="flex shrink-0 items-center">
                <span className="font-mono text-sm font-black text-neutral-500">
                    {exercise.title}
                </span>
            </div>

            <div className="min-w-0 flex-1">
                <ExerciseTimeline
                    exercise={exercise}
                    currentBeat={currentBeat}
                    preview={preview}
                    lastPass={lastPass}
                />
            </div>

            <div className="flex shrink-0 items-center border-l border-neutral-200 pl-3 pr-0.5">
                <span
                    className={cn(
                        "flex h-8 min-w-8 items-center justify-center rounded-full border-2 px-1.5 font-mono text-base font-black",
                        preview
                            ? "border-neutral-300 text-neutral-400"
                            : "border-blue-600 text-blue-700",
                    )}
                >
                    {repetition}
                </span>
            </div>
        </div>
    );
}
