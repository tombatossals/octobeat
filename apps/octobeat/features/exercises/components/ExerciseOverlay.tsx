"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { JSX } from "react";

import { books } from "@octobeat/exercises";
import { usePlayerStore } from "@octobeat/player";
import { ExerciseStage } from "@octobeat/ui";

import { useLibraryStore } from "@/features/library/store";

import {
    beatAtTime,
    nextBeat,
} from "@octobeat/songmap";

import {
    DIFFICULTY_FACTOR,
    useDifficultyStore,
} from "../store";
import { useSettingsStore } from "@/features/settings/store";

import { DifficultySwitcher } from "./DifficultySwitcher";

export function ExerciseOverlay(): JSX.Element | null {
    const dataset = useLibraryStore(
        (state) => state.dataset,
    );

    const player = usePlayerStore(
        (state) => state.player,
    );

    const difficulty =
        useDifficultyStore(
            (state) =>
                state.difficulty,
        );

    const repetitionsPerLine =
        useSettingsStore(
            (state) =>
                state.settings
                    .repetitionsPerLine,
        );

    // Posición del ejercicio acumulada entre canciones: cuando la
    // canción cambia el beat grid se reinicia, así que sumamos un
    // offset para continuar donde nos quedamos.
    const [exerciseBeat, setExerciseBeat] =
        useState(0);

    const baseOffsetRef =
        useRef(0);

    const lastExerciseBeatRef =
        useRef(0);

    const datasetIdRef =
        useRef<string | null>(
            null,
        );

    // Al cambiar de canción el beat grid se reinicia: el offset base
    // pasa a ser la última posición confirmada para que el ejercicio
    // continúe en la línea en la que estábamos.
    useEffect(() => {
        const id =
            dataset?.metadata.id ??
            null;

        if (
            datasetIdRef.current !==
                null &&
            id !== datasetIdRef.current
        ) {
            baseOffsetRef.current =
                lastExerciseBeatRef.current;

            lastExerciseBeatRef.current = 0;
        }

        datasetIdRef.current = id;
    }, [dataset?.metadata.id]);

    const exercises = useMemo(() => {
        return Object.values(
            books.stickControl.sets,
        ).flatMap((set) =>
            Object.values(
                set.exercises,
            ),
        );
    }, []);

    const factor =
        DIFFICULTY_FACTOR[difficulty];

    const lineTotals = useMemo(() => {
        return exercises.map(
            (exercise) =>
                exercise.beats.length *
                factor *
                repetitionsPerLine,
        );
    }, [
        exercises,
        factor,
        repetitionsPerLine,
    ]);

    const totalBeats = useMemo(() => {
        return lineTotals.reduce(
            (sum, length) =>
                sum + length,
            0,
        );
    }, [lineTotals]);

    let lineIndex = 0;
    let repetition =
        repetitionsPerLine;

    if (exerciseBeat > 0) {
        let position =
            (exerciseBeat - 1) %
            totalBeats;

        for (
            let i = 0;
            i < lineTotals.length;
            i++
        ) {
            if (
                position <
                lineTotals[i]!
            ) {
                lineIndex = i;

                repetition =
                    repetitionsPerLine -
                    Math.floor(
                        position /
                            (exercises[i]!
                                .beats.length *
                                factor),
                    );

                break;
            }

            position -= lineTotals[i]!;
        }
    }

    const exercise =
        exercises[lineIndex]!;

    const preview =
        exercises[
            (lineIndex + 1) %
                exercises.length
        ]!;

    useEffect(() => {
        const map = dataset?.songmap;
        const adapter = player;

        if (!map || !adapter) {
            return;
        }

        let frame = 0;

        // El tiempo del media se actualiza en saltos (~4Hz), así que
        // sintetizamos un reloj fluido anclado al media y avanzado
        // con performance.now() entre lecturas.
        let anchorMedia =
            adapter.currentTime();

        let anchorPerf =
            performance.now();

        function tick() {
            if (!map || !adapter) {
                return;
            }

            const now =
                performance.now();

            const media =
                adapter.currentTime();

            if (media !== anchorMedia) {
                anchorMedia = media;
                anchorPerf = now;
            }

            const currentTime =
                adapter.isPlaying()
                    ? anchorMedia +
                      (now -
                          anchorPerf) /
                          1000
                    : media;

            const beat = beatAtTime(
                map,
                currentTime,
            );

            if (!beat) {
                frame =
                    requestAnimationFrame(
                        tick,
                    );

                return;
            }

            if (beat) {
                const next = nextBeat(
                    map,
                    beat.time,
                );

                const duration = next
                    ? next.time - beat.time
                    : 0.5;

                const sub = Math.min(
                    factor - 1,
                    Math.floor(
                        ((currentTime -
                            beat.time) /
                            duration) *
                            factor,
                    ),
                );

                const rawBeat =
                    (beat.index - 1) *
                        factor +
                        sub +
                        1;

                const nextBeatValue =
                    baseOffsetRef.current +
                    rawBeat;

                // Al cambiar de canción el media se reinicia a 0 y el
                // tick de la canción antigua recalcula un rawBeat
                // pequeño; solo confirmamos posiciones que avanzan.
                if (
                    nextBeatValue >
                    lastExerciseBeatRef.current
                ) {
                    lastExerciseBeatRef.current =
                        nextBeatValue;

                    setExerciseBeat(
                        nextBeatValue,
                    );
                }
            }

            frame =
                requestAnimationFrame(
                    tick,
                );
        }

        frame = requestAnimationFrame(
            tick,
        );

        return () => {
            cancelAnimationFrame(
                frame,
            );
        };
    }, [
        dataset,
        player,
        factor,
    ]);

    const songmap = dataset?.songmap;

    if (!songmap) {
        return null;
    }

    return (
        <div className="pointer-events-none absolute inset-x-0 bottom-24 z-30 flex justify-center">
            <div className="flex flex-col items-start gap-3">
                <ExerciseStage
                    exercise={exercise}
                    preview={preview}
                    currentBeat={exerciseBeat}
                    repetition={repetition}
                    previewRepetition={
                        repetitionsPerLine
                    }
                />

                <DifficultySwitcher />
            </div>
        </div>
    );
}
