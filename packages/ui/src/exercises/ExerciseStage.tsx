"use client";

import { useEffect, useRef, useState } from "react";
import type { JSX, ReactNode } from "react";

import type { Exercise } from "@octobeat/exercises";

import { cn } from "../lib/utils";

import { ExerciseRenderer } from "./ExerciseRenderer";

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

    /**
     * Encabezado interactivo (selector de libro y sección) que
     * sustituye a la línea de títulos por defecto de la línea activa.
     */
    header?: ReactNode;

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

const TRANSITION_MS = 600;

export function ExerciseStage({
    exercise,
    exerciseBookTitle,
    exerciseSetTitle,
    header,
    preview,
    previewBookTitle,
    previewSetTitle,
    currentBeat,
    repetition,
    previewRepetition,
}: ExerciseStageProps): JSX.Element {
    const [leaving, setLeaving] =
        useState<Exercise | null>(
            null,
        );

    const [leavingBookTitle, setLeavingBookTitle] =
        useState<string | undefined>(
            undefined,
        );

    const [leavingSetTitle, setLeavingSetTitle] =
        useState<string | undefined>(
            undefined,
        );

    const prevExerciseRef =
        useRef(exercise);

    useEffect(() => {
        const prev =
            prevExerciseRef.current;

        prevExerciseRef.current =
            exercise;

        if (prev.id === exercise.id) {
            return;
        }

        setLeaving(prev);
        setLeavingBookTitle(
            exerciseBookTitle,
        );
        setLeavingSetTitle(
            exerciseSetTitle,
        );

        const timer = setTimeout(
            () => setLeaving(null),
            TRANSITION_MS,
        );

        return () => {
            clearTimeout(timer);
        };
    }, [exercise, exerciseBookTitle, exerciseSetTitle]);

    return (
        <div className="flex w-full flex-col gap-2">
            <div className="relative w-full">
                {leaving && (
                    <div className="pointer-events-none absolute inset-0 animate-[exerciseExit_600ms_ease-in-out_forwards]">
                        <ExerciseRenderer
                            exercise={leaving}
                            bookTitle={
                                leavingBookTitle
                            }
                            setTitle={
                                leavingSetTitle
                            }
                            currentBeat={0}
                            repetition={previewRepetition}
                            preview
                        />
                    </div>
                )}

                <div
                    key={exercise.id}
                    className="animate-[exerciseEnter_600ms_ease-in-out]"
                >
                    <ExerciseRenderer
                        exercise={exercise}
                        bookTitle={
                            exerciseBookTitle
                        }
                        setTitle={
                            exerciseSetTitle
                        }
                        header={header}
                        currentBeat={currentBeat}
                        repetition={repetition}
                        lastPass={
                            repetition === 1
                        }
                    />
                </div>
            </div>

            <div
                className={cn(
                    "pointer-events-none transition-all duration-500",
                    repetition === 1
                        ? "opacity-100 drop-shadow-[0_0_6px_rgba(37,99,235,0.6)]"
                        : "opacity-70",
                )}
            >
                <ExerciseRenderer
                    exercise={preview}
                    bookTitle={
                        previewBookTitle
                    }
                    setTitle={
                        previewSetTitle
                    }
                    currentBeat={0}
                    repetition={previewRepetition}
                    preview
                />
            </div>
        </div>
    );
}
