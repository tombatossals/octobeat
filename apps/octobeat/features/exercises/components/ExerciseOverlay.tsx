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
    SPEED_FACTOR,
    useSpeedStore,
} from "../store";
import { useSettingsStore } from "@/features/settings/store";

import { SpeedSwitcher } from "./SpeedSwitcher";

export function ExerciseOverlay(): JSX.Element | null {
    const dataset = useLibraryStore(
        (state) => state.dataset,
    );

    const player = usePlayerStore(
        (state) => state.player,
    );

    const speed =
        useSpeedStore(
            (state) =>
                state.speed,
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

    // Compensa el salto del rawBeat al cambiar de velocidad: al reducir
    // el factor el rawBeat recalcula un valor más pequeño y el guard
    // monótono lo bloquearía, congelando el contador.
    const biasRef =
        useRef(0);

    const prevFactorRef =
        useRef<number | null>(
            null,
        );

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
            biasRef.current = 0;
        }

        datasetIdRef.current = id;
    }, [dataset?.metadata.id]);

    const exerciseSets = useLibraryStore(
        (state) =>
            state.filters
                .exerciseSets,
    );

    const exercises = useMemo(() => {
        const all = Object.values(
            books.stickControl.sets,
        ).flatMap((set) =>
            Object.values(
                set.exercises,
            ),
        );

        if (
            exerciseSets.length ===
            0
        ) {
            return all;
        }

        return Object.values(
            books.stickControl.sets,
        )
            .filter((set) =>
                exerciseSets.includes(
                    set.id,
                ),
            )
            .flatMap((set) =>
                Object.values(
                    set.exercises,
                ),
            );
    }, [exerciseSets]);

    const factor =
        SPEED_FACTOR[speed];

    // La estructura del ejercicio (beats por línea y repeticiones) es
    // independiente de la velocidad: el factor solo acelera el reloj
    // del beat en el tick de abajo, no cambia la rutina.
    const lineTotals = useMemo(() => {
        return exercises.map(
            (exercise) =>
                exercise.beats.length *
                repetitionsPerLine,
        );
    }, [
        exercises,
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
                            exercises[i]!
                                .beats.length,
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

        // Al cambiar de velocidad el rawBeat salta (mayor o menor según
        // el factor) y el guard monótono abajo lo bloquearía. Recalibra
        // el bias para que el contador continúe desde la última posición
        // confirmada.
        if (
            prevFactorRef.current !==
                null &&
            prevFactorRef.current !==
                factor
        ) {
            const rawNow =
                beatAtTime(
                    map,
                    anchorMedia,
                );

            if (rawNow) {
                const next =
                    nextBeat(
                        map,
                        rawNow.time,
                    );

                const duration =
                    next
                        ? next.time -
                          rawNow.time
                        : 0.5;

                const sub =
                    Math.min(
                        factor - 1,
                        Math.floor(
                            ((anchorMedia -
                                rawNow.time) /
                                duration) *
                                factor,
                        ),
                    );

                const rawBeat =
                    (rawNow.index - 1) *
                        factor +
                        sub +
                        1;

                biasRef.current =
                    lastExerciseBeatRef.current -
                    baseOffsetRef.current -
                    rawBeat;
            }
        }

        prevFactorRef.current =
            factor;

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
                    biasRef.current +
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
        <div className="pointer-events-none absolute inset-x-0 bottom-24 z-30 flex justify-center px-4 short:bottom-14">
            <div className="flex w-full max-w-4xl flex-col items-center gap-3 short:gap-1.5">
                <ExerciseStage
                    exercise={exercise}
                    preview={preview}
                    currentBeat={exerciseBeat}
                    repetition={repetition}
                    previewRepetition={
                        repetitionsPerLine
                    }
                />

                <SpeedSwitcher />
            </div>
        </div>
    );
}
