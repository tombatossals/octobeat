"use client";

import { useEffect, useMemo, useState } from "react";
import type { JSX } from "react";

import { books, subdivideExercise } from "@octobeat/exercises";
import { usePlayerStore } from "@octobeat/player";
import { ExerciseRenderer } from "@octobeat/ui";

import { useLibraryStore } from "@/features/library/store";

import {
    beatAtTime,
    nextBeat,
} from "@octobeat/songmap";

import {
    DIFFICULTY_FACTOR,
    useDifficultyStore,
} from "../store";

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

    const [currentBeat, setCurrentBeat] =
        useState(0);

    const exercise = useMemo(() => {
        const line1 =
            books.stickControl.exercises
                .line1;

        const factor =
            DIFFICULTY_FACTOR[
                difficulty
            ];

        if (factor === 1) {
            return line1;
        }

        return subdivideExercise(
            line1,
            factor,
        );
    }, [difficulty]);

    const factor =
        DIFFICULTY_FACTOR[difficulty];

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

                setCurrentBeat(
                    (beat.index - 1) *
                        factor +
                        sub +
                        1,
                );
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
        <div className="pointer-events-none absolute inset-x-0 top-[72%] z-30 flex -translate-y-1/2 justify-center">
            <ExerciseRenderer
                exercise={exercise}
                currentBeat={currentBeat}
            />
        </div>
    );
}
