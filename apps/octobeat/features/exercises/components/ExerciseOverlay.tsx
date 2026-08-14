"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { JSX } from "react";

import {
    books,
    exerciseNoteDurations,
} from "@octobeat/exercises";
import { usePlayerStore } from "@octobeat/player";
import { ExerciseStage } from "@octobeat/ui";

import { useLibraryStore } from "@/features/library/store";

import {
    beatAtTime,
    nextBeat,
    type SongMap,
} from "@octobeat/songmap";

import {
    SPEED_FACTOR,
    useSpeedStore,
} from "../store";
import { useSettingsStore } from "@/features/settings/store";

import { SpeedSwitcher } from "./SpeedSwitcher";

interface ExerciseCycle {
    /**
     * Posición en pulsos del inicio de cada golpe dentro del ciclo
     * completo de ejercicios (longitud = totalNotes + 1).
     */
    offsets: number[];

    /**
     * Número total de golpes del ciclo.
     */
    totalNotes: number;

    /**
     * Duración total del ciclo en pulsos.
     */
    totalBeats: number;
}

/**
 * Mapea una posición musical (en pulsos) al índice global del golpe
 * activo del ciclo de ejercicios. Los golpes de tresillo duran 2/3 de
 * pulso, así que el puntero avanza más rápido al atravesarlos.
 */
function globalNoteIndexAt(
    musicalPosition: number,
    factor: number,
    cycle: ExerciseCycle,
): number {
    const { offsets, totalNotes, totalBeats } =
        cycle;

    if (totalBeats <= 0 || totalNotes === 0) {
        return 0;
    }

    const position =
        factor * musicalPosition;

    const cycles = Math.floor(
        position / totalBeats,
    );

    const within =
        position -
        cycles * totalBeats;

    let low = 0;
    let high = totalNotes;

    while (low < high) {
        const mid = (low + high) >> 1;

        if (offsets[mid]! <= within) {
            low = mid + 1;
        } else {
            high = mid;
        }
    }

    return (
        cycles * totalNotes +
        (low - 1)
    );
}

/**
 * Escala del beat grid de la canción: a cuántas negras equivale cada
 * punto del grid. La mayoría de canciones tienen el grid en negras
 * (1), pero algunas en corcheas (0.5), blancas (2) o semicorcheas
 * (0.25). Sin normalizar, el ejercicio avanzaría al doble (o a la
 * mitad) de la velocidad en esas canciones y la partitura se
 * desincronizaría de la música.
 */
function beatGridScale(
    songmap: SongMap,
): number {
    const bpm = songmap.timing?.bpm;

    if (bpm == null || bpm <= 0) {
        return 1;
    }

    const beats = songmap.beats;

    if (beats.length < 2) {
        return 1;
    }

    // Delta mediano entre beats consecutivos: robusto a cambios de
    // tempo puntuales y a grids irregulares.
    const deltas: number[] = [];

    for (
        let i = 1;
        i < beats.length &&
        deltas.length < 256;
        i++
    ) {
        deltas.push(
            beats[i]!.time -
                beats[i - 1]!.time,
        );
    }

    deltas.sort((a, b) => a - b);

    const median =
        deltas[Math.floor(deltas.length / 2)]!;

    const quarter = 60 / bpm;
    const ratio = median / quarter;

    if (ratio <= 0) {
        return 1;
    }

    // Ajusta a la potencia de 2 más cercana (negras, corcheas,
    // blancas…) y solo la aplica si la medida es fiable.
    const log2 = Math.log2(ratio);
    const snapped = Math.round(log2);
    const error = Math.abs(log2 - snapped);

    if (error > 0.45) {
        return 1;
    }

    return 2 ** snapped;
}

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

    // Estructura temporal del ciclo completo de ejercicios: la
    // duración en pulsos de cada golpe acumulada a lo largo de todas
    // las líneas y repeticiones. Se usa para mapear la posición
    // musical al golpe activo respetando los tresillos.
    const exerciseCycle = useMemo(() => {
        const offsets: number[] = [
            0,
        ];

        let runningBeats = 0;
        let totalNotes = 0;

        for (const exercise of exercises) {
            const durations =
                exerciseNoteDurations(
                    exercise,
                );

            for (
                let repetition = 0;
                repetition <
                repetitionsPerLine;
                repetition++
            ) {
                for (const duration of durations) {
                    runningBeats +=
                        duration;

                    offsets.push(
                        runningBeats,
                    );
                }
            }

            totalNotes +=
                durations.length *
                repetitionsPerLine;
        }

        return {
            offsets,
            totalNotes,
            totalBeats: runningBeats,
        };
    }, [
        exercises,
        repetitionsPerLine,
    ]);

    // Normaliza la resolución del beat grid de la canción: si el grid
    // está en corcheas/blancas en lugar de negras, la posición musical
    // se escala para que el ejercicio avance a la velocidad correcta.
    const gridScale = useMemo(() => {
        const map = dataset?.songmap;

        return map ? beatGridScale(map) : 1;
    }, [dataset]);

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

        // Margen máximo (segundos) que el reloj sintetizado puede
        // adelantarse al último valor reportado por el media. Un poco
        // más que un intervalo de actualización (~0.25s) para no
        // cortar la interpolación suave entre lecturas.
        const mediaMaxLead = 0.4;

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

                const frac = next
                    ? Math.min(
                          1,
                          (anchorMedia -
                              rawNow.time) /
                              duration,
                      )
                    : Math.min(
                          (factor - 1) /
                              factor,
                          (anchorMedia -
                              rawNow.time) /
                              duration,
                      );

                const musicalPosition =
                    (rawNow.index - 1) +
                    Math.max(
                        0,
                        frac,
                    );

                const rawBeat =
                    globalNoteIndexAt(
                        musicalPosition *
                            gridScale,
                        factor,
                        exerciseCycle,
                    ) + 1;

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

            // El reloj se extrapola a ritmo real entre lecturas del
            // media, pero nunca más de mediaMaxLead por delante del
            // último valor reportado. Sin este techo, un media que se
            // queda congelado (búfer atascado, fluctuación del
            // streaming) haría avanzar el reloj a ciegas y el guard
            // monótono de abajo dejaría el puntero del ejercicio
            // adelantado — acumulándose con cada micro-parón y
            // haciéndose visible al atravesar las semicorcheas de los
            // short rolls.
            const currentTime =
                adapter.isPlaying()
                    ? Math.min(
                          anchorMedia +
                              (now -
                                  anchorPerf) /
                                  1000,
                          media +
                              mediaMaxLead,
                      )
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

                const frac = next
                    ? Math.min(
                          1,
                          (currentTime -
                              beat.time) /
                              duration,
                      )
                    : Math.min(
                          (factor - 1) /
                              factor,
                          (currentTime -
                              beat.time) /
                              duration,
                      );

                const musicalPosition =
                    (beat.index - 1) +
                    Math.max(
                        0,
                        frac,
                    );

                const rawBeat =
                    globalNoteIndexAt(
                        musicalPosition *
                            gridScale,
                        factor,
                        exerciseCycle,
                    ) + 1;

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
        exerciseCycle,
        gridScale,
    ]);

    const songmap = dataset?.songmap;

    if (!songmap) {
        return null;
    }

    return (
        <div className="pointer-events-none absolute inset-x-0 bottom-24 z-30 flex justify-center px-4 short:bottom-14">
            <div className="flex w-full max-w-6xl flex-col items-center gap-3 short:gap-1.5">
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
