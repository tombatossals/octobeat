"use client";

import type { JSX } from "react";

import type { Exercise } from "@octobeat/exercises";

import { cn } from "../lib/utils";

import { ExerciseTimeline } from "./ExerciseTimeline";

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
    bookTitle,
    setTitle,
    currentBeat,
    repetition = 1,
    preview = false,
    lastPass = false,
}: ExerciseRendererProps): JSX.Element {
    const titleColor = "var(--title-color)";

    const titleWeight = "var(--title-weight)";

    const titleShadow =
        "1px 1px 0 var(--title-outline), -1px -1px 0 var(--title-outline), 1px -1px 0 var(--title-outline), -1px 1px 0 var(--title-outline), 1px 0 0 var(--title-outline), -1px 0 0 var(--title-outline), 0 1px 0 var(--title-outline), 0 -1px 0 var(--title-outline)";

    return (
        <div className="flex w-full flex-col gap-0.5">
            <div className="flex items-center gap-1.5 px-1">
                {preview ? (
                    <span
                        className="font-mono text-xs uppercase tracking-wider text-muted-foreground"
                        style={{
                            textShadow: titleShadow,
                        }}
                    >
                        Next line…
                    </span>
                ) : (
                    <>
                        {bookTitle != null && (
                            <span
                                className="font-mono text-xs uppercase tracking-wider"
                                style={{
                                    color: titleColor,
                                    fontWeight: titleWeight,
                                    textShadow: titleShadow,
                                }}
                            >
                                {bookTitle}
                            </span>
                        )}

                        {bookTitle != null && setTitle != null && (
                            <span
                                className=""
                                style={{
                                    color: titleColor,
                                    fontWeight: titleWeight,
                                    textShadow: titleShadow,
                                }}
                            >
                                ·
                            </span>
                        )}

                        {setTitle != null && (
                            <span
                                className="font-mono text-xs uppercase tracking-wider"
                                style={{
                                    color: titleColor,
                                    fontWeight: titleWeight,
                                    textShadow: titleShadow,
                                }}
                            >
                                {setTitle}
                            </span>
                        )}
                    </>
                )}
            </div>

            <div
                className={cn(
                    "flex w-full items-center gap-3 rounded-lg border border-neutral-200 bg-white px-3 shadow-2xl",
                    preview
                        ? "py-0.5"
                        : "py-1",
                )}
            >
                {!preview && (
                    <div className="flex shrink-0 translate-y-2 items-center">
                        <span className="font-mono text-sm font-black text-neutral-700">
                            {exercise.title}
                        </span>
                    </div>
                )}

                <div className="min-w-0 flex-1">
                    <ExerciseTimeline
                        exercise={exercise}
                        currentBeat={currentBeat}
                        preview={preview}
                        lastPass={lastPass}
                    />
                </div>

                {!preview && (
                    <div className="flex shrink-0 items-center border-l border-neutral-200 pl-3 pr-0.5">
                        <span className="flex h-8 min-w-8 items-center justify-center rounded-full border-2 border-blue-600 px-1.5 font-mono text-base font-black text-blue-700">
                            {repetition}
                        </span>
                    </div>
                )}
            </div>
        </div>
    );
}
