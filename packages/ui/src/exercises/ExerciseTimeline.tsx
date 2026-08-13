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

    /**
     * Desactiva el resaltado del beat activo (vista previa).
     */
    preview?: boolean;

    /**
     * Última repetición de la línea: los compases ya superados se
     * atenúan para indicar que no volverán a sonar.
     */
    lastPass?: boolean;
}

interface BeatGroup {
    beats: ExerciseBeat[];
    startIndex: number;
}

export function ExerciseTimeline({
    exercise,
    currentBeat,
    preview = false,
    lastPass = false,
}: ExerciseTimelineProps): JSX.Element {
    const activeBeat =
        ((currentBeat - 1) % exercise.beats.length +
            exercise.beats.length) %
        exercise.beats.length;

    let currentMeasure = 0;
    let measureStart = 0;

    for (
        let i = 0;
        i < exercise.barLengths.length;
        i++
    ) {
        if (
            activeBeat <
            measureStart +
                exercise.barLengths[i]!
        ) {
            currentMeasure = i;
            break;
        }

        measureStart +=
            exercise.barLengths[i]!;
    }

    const measures: BeatGroup[][] = [];
    let offset = 0;

    for (const barLength of exercise.barLengths) {
        const barBeats = exercise.beats.slice(
            offset,
            offset + barLength,
        );
        offset += barLength;

        const groups: BeatGroup[] = [];
        let index = 0;

        while (index < barBeats.length) {
            const beat = barBeats[index]!;

            if (beat.triplet == null) {
                groups.push({
                    beats: [beat],
                    startIndex: offset - barLength + index,
                });
                index += 1;
                continue;
            }

            const group = beat.triplet;
            const groupBeats: ExerciseBeat[] = [];
            const startIndex = offset - barLength + index;

            while (
                index < barBeats.length &&
                barBeats[index]?.triplet ===
                    group
            ) {
                groupBeats.push(
                    barBeats[index]!,
                );
                index += 1;
            }

            groups.push({
                beats: groupBeats,
                startIndex,
            });
        }

        measures.push(groups);
    }

    return (
        <div className="w-full">
            <div className="flex items-center">
                {measures.map(
                    (groups, measureIndex) => (
                        <Fragment key={measureIndex}>
                            {measureIndex > 0 && (
                                <div className="mx-2 flex h-8 items-center">
                                    <div className="h-full w-[2px] rounded-full bg-neutral-300" />
                                </div>
                            )}

                            <div
                                className={cn(
                                    "flex flex-1 items-center justify-between transition-opacity duration-500",
                                    lastPass &&
                                        measureIndex <
                                            currentMeasure
                                        ? "opacity-30"
                                        : "opacity-100",
                                )}
                            >
                                {groups.map(
                                    (
                                        group,
                                        groupIndex,
                                    ) => (
                                        <TripletGroup
                                            key={groupIndex}
                                            group={group}
                                            preview={preview}
                                            activeBeat={activeBeat}
                                        />
                                    ),
                                )}
                            </div>
                        </Fragment>
                    ),
                )}
            </div>
        </div>
    );
}

interface TripletGroupProps {
    group: BeatGroup;
    preview: boolean;
    activeBeat: number;
}

function TripletGroup({
    group,
    preview,
    activeBeat,
}: TripletGroupProps): JSX.Element {
    const triplet =
        group.beats[0]?.triplet != null;

    return (
        <div className="relative flex items-center">
            {triplet && (
                <span className="absolute -top-4 left-1/2 -translate-x-1/2 text-xs font-black text-neutral-400">
                    3
                </span>
            )}

            {group.beats.map(
                (beat, beatIndex) => {
                    const index =
                        group.startIndex +
                        beatIndex;

                    return (
                        <BeatCell
                            key={index}
                            beat={beat}
                            active={
                                !preview &&
                                index ===
                                    activeBeat
                            }
                        />
                    );
                },
            )}
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
