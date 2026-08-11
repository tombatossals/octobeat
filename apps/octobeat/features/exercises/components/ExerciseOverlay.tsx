"use client";

import { useEffect, useMemo, useState } from "react";
import type { JSX } from "react";

import { books } from "@octobeat/exercises";
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

// Secuencia del count-in de entrada (la típica "1, 2, 1, 2, 3, 4" de
// Rock Band): 2 golpes de anacrusa más el compás completo de 4.
const COUNT_IN_PATTERN = [
    1,
    2,
    1,
    2,
    3,
    4,
];

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

    const [currentTime, setCurrentTime] =
        useState(0);

    const exercise = useMemo(() => {
        return books.stickControl.exercises
            .line1;
    }, []);

    const factor =
        DIFFICULTY_FACTOR[difficulty];

    const beatsPerPass =
        exercise.beats.length * factor;

    const repetition =
        currentBeat > 0
            ? ((Math.floor(
                      (currentBeat - 1) /
                          beatsPerPass,
                  ) %
                    20) +
                  1)
            : 1;

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

            setCurrentTime(
                currentTime,
            );

            const beat = beatAtTime(
                map,
                currentTime,
            );

            if (!beat) {
                setCurrentBeat(0);

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

    const timing = songmap.timing;

    const countInStart =
        timing.countInStart;

    const songStart =
        timing.songStart;

    // Fuentes con count-in (p.ej. SNG): la rejilla arranca con los
    // golpes de baqueta antes de que empiece la canción. En ese caso la
    // línea del ejercicio se muestra desde el principio.
    const hasCountIn =
        countInStart !==
            undefined &&
        songStart !==
            undefined;

    // El arranque de la música: para fuentes con count-in (SNG) es
    // `songStart`; en el resto, el offset detectado.
    const musicStart =
        songStart ??
        timing.offset;

    const musicStarted =
        currentTime >= musicStart;

    // Count-in activo: los golpes de baqueta entre `countInStart` y el
    // arranque real de la canción.
    const countInActive =
        !musicStarted &&
        countInStart !==
            undefined &&
        currentTime >=
            countInStart;

    // Golpes de baqueta individuales (cuando la fuente los lleva, p.ej.
    // el song.opus de un SNG). El contador se sincroniza con ellos.
    const countInClicks =
        timing.countInClicks;

    const countInNumber =
        countInActive &&
        countInStart !==
            undefined
            ? (() => {
                  if (
                      countInClicks &&
                      countInClicks.length
                  ) {
                      // Último click <= tiempo actual: cada golpe avanza
                      // la secuencia "1, 2, 1, 2, 3, 4".
                      let clickIndex = -1;

                      for (
                          let index = 0;
                          index <
                          countInClicks.length;
                          index++
                      ) {
                          if (
                              countInClicks[index]! <=
                              currentTime
                          ) {
                              clickIndex =
                                  index;
                          } else {
                              break;
                          }
                      }

                      if (clickIndex < 0) {
                          return null;
                      }

                      return COUNT_IN_PATTERN[
                          clickIndex %
                              COUNT_IN_PATTERN.length
                      ]!;
                  }

                  // Sin clicks detectados: ancla la cuenta al beat grid
                  // desde el primer golpe audible.
                  const current =
                      beatAtTime(
                          songmap,
                          currentTime,
                      );

                  const first =
                      songmap.beats.find(
                          (beat) =>
                              beat.time >=
                              countInStart,
                      );

                  if (
                      !current ||
                      !first
                  ) {
                      return null;
                  }

                  const position =
                      current.index -
                      first.index;

                  return COUNT_IN_PATTERN[
                      ((position %
                          COUNT_IN_PATTERN.length) +
                          COUNT_IN_PATTERN.length) %
                          COUNT_IN_PATTERN.length
                  ]!;
              })()
            : null;

    const remaining =
        musicStart - currentTime;

    return (
        <div className="pointer-events-none absolute inset-x-0 bottom-24 z-30 flex justify-center">
            {hasCountIn ? (
                <div className="flex items-center gap-4">
                    {countInActive &&
                        countInNumber !==
                            null && (
                            <div className="flex flex-col items-center gap-1 rounded-lg border border-white/10 bg-gray-800/60 px-5 py-3 shadow-2xl backdrop-blur-md">
                                <span
                                    className="text-xs uppercase tracking-widest text-white"
                                    style={{
                                        textShadow:
                                            "1px 1px 0 #374151, -1px -1px 0 #374151, 1px -1px 0 #374151, -1px 1px 0 #374151, 1px 0 0 #374151, -1px 0 0 #374151, 0 1px 0 #374151, 0 -1px 0 #374151",
                                    }}
                                >
                                    Empieza en
                                </span>

                                <span
                                    className="font-mono text-5xl font-black leading-none text-white"
                                    style={{
                                        textShadow:
                                            "1px 1px 0 #374151, -1px -1px 0 #374151, 1px -1px 0 #374151, -1px 1px 0 #374151, 1px 0 0 #374151, -1px 0 0 #374151, 0 1px 0 #374151, 0 -1px 0 #374151",
                                    }}
                                >
                                    {countInNumber}
                                </span>
                            </div>
                        )}

                    <ExerciseRenderer
                        exercise={exercise}
                        currentBeat={currentBeat}
                        repetition={repetition}
                    />
                </div>
            ) : musicStarted ? (
                <ExerciseRenderer
                    exercise={exercise}
                    currentBeat={currentBeat}
                    repetition={repetition}
                />
            ) : (
                <div className="flex flex-col items-center gap-1 rounded-lg border border-white/10 bg-gray-800/60 px-6 py-3 shadow-2xl backdrop-blur-md">
                    <span
                        className="text-xs uppercase tracking-widest text-white"
                        style={{
                            textShadow:
                                "1px 1px 0 #374151, -1px -1px 0 #374151, 1px -1px 0 #374151, -1px 1px 0 #374151, 1px 0 0 #374151, -1px 0 0 #374151, 0 1px 0 #374151, 0 -1px 0 #374151",
                        }}
                    >
                        Empieza en
                    </span>

                    <span
                        className="font-mono font-black leading-none text-white"
                        style={{
                            fontSize: "1.875rem",
                            textShadow:
                                "1px 1px 0 #374151, -1px -1px 0 #374151, 1px -1px 0 #374151, -1px 1px 0 #374151, 1px 0 0 #374151, -1px 0 0 #374151, 0 1px 0 #374151, 0 -1px 0 #374151",
                        }}
                    >
                        {Math.max(
                            0,
                            Math.ceil(
                                remaining,
                            ),
                        )}
                        s
                    </span>
                </div>
            )}
        </div>
    );
}
