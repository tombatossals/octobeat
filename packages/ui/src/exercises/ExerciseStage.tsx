"use client";

import { useEffect, useRef, useState } from "react";
import type { JSX } from "react";

import type { Exercise } from "@octobeat/exercises";

import { cn } from "../lib/utils";

import { ExerciseRenderer } from "./ExerciseRenderer";

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

const TRANSITION_MS = 600;

export function ExerciseStage({
    exercise,
    preview,
    currentBeat,
    repetition,
    previewRepetition,
}: ExerciseStageProps): JSX.Element {
    const [leaving, setLeaving] =
        useState<Exercise | null>(
            null,
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

        const timer = setTimeout(
            () => setLeaving(null),
            TRANSITION_MS,
        );

        return () => {
            clearTimeout(timer);
        };
    }, [exercise]);

    return (
        <div className="flex items-center gap-3">
            <div className="relative">
                {leaving && (
                    <div className="pointer-events-none absolute inset-0 animate-[exerciseExit_600ms_ease-in-out_forwards]">
                        <ExerciseRenderer
                            exercise={leaving}
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
                        ? "opacity-90 drop-shadow-[0_0_6px_rgba(37,99,235,0.6)]"
                        : "opacity-40",
                )}
            >
                <ExerciseRenderer
                    exercise={preview}
                    currentBeat={0}
                    repetition={previewRepetition}
                    preview
                />
            </div>
        </div>
    );
}
