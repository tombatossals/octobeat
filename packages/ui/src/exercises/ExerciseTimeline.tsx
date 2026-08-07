"use client";

import { Fragment } from "react";
import type { JSX } from "react";

import type {
    Exercise,
    ExerciseBeat,
} from "@octobeat/exercises";

import { cn } from "../lib/utils";

export interface ExerciseTimelineProps {
    exercise: Exercise;
    currentBeat: number;
}

export function ExerciseTimeline({
    exercise,
    currentBeat,
}: ExerciseTimelineProps): JSX.Element {
    const activeBeat =
        ((currentBeat - 1) % exercise.beats.length +
            exercise.beats.length) %
        exercise.beats.length;

    const measures: ExerciseBeat[][] = [];

    for (
        let i = 0;
        i < exercise.beats.length;
        i += exercise.beatsPerBar
    ) {
        measures.push(
            exercise.beats.slice(
                i,
                i + exercise.beatsPerBar,
            ),
        );
    }

    return (
        <div className="mx-auto w-full max-w-3xl">
            <div className="mx-auto flex items-center">
                {measures.map(
                    (measure, measureIndex) => (
                        <Fragment key={measureIndex}>
                            {measureIndex > 0 && (
                                <div className="mx-2 flex h-8 items-center">
                                    <div className="h-full w-[2px] rounded-full bg-neutral-300" />
                                </div>
                            )}

                            <div className="flex flex-1 items-center justify-between">
                                {measure.map((beat, beatIndex) => {
                                    const index =
                                        measureIndex *
                                        exercise.beatsPerBar +
                                        beatIndex;

                                    return (
                                        <BeatCell
                                            key={index}
                                            beat={beat}
                                            active={
                                                index === activeBeat
                                            }
                                        />
                                    );
                                })}
                            </div>
                        </Fragment>
                    ),
                )}
            </div>
        </div>
    );
}

interface BeatCellProps {
    beat: ExerciseBeat;
    active: boolean;
}

function BeatCell({
    beat,
    active,
}: BeatCellProps): JSX.Element {
    return (
        <div className="relative flex justify-center py-1.5">
            {active && (
                <>
                    <div className="absolute -top-1 text-sm text-blue-600">
                        ▼
                    </div>

                    <div className="absolute inset-x-1 inset-y-1 rounded-xl bg-blue-100" />
                </>
            )}

            <div
                className={cn(
                    "relative z-10 flex items-center justify-center font-mono font-black transition-all duration-150",
                    active
                        ? "scale-110 text-blue-700"
                        : "text-black",
                )}
                style={{
                    fontSize:
                        "clamp(1.4rem,2vw,2rem)",
                    textShadow:
                        "1px 1px 0 #e5e5e5, -1px -1px 0 #e5e5e5, 1px -1px 0 #e5e5e5, -1px 1px 0 #e5e5e5, 1px 0 0 #e5e5e5, -1px 0 0 #e5e5e5, 0 1px 0 #e5e5e5, 0 -1px 0 #e5e5e5, 0 2px 4px rgb(0 0 0 / 25%)",
                }}
            >
                {beat.hand}
            </div>
        </div>
    );
}