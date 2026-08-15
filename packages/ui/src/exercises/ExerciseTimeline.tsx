"use client";

import { Fragment } from "react";
import type { JSX } from "react";

import type {
    Exercise,
    ExerciseBeat,
} from "@octobeat/exercises";
import { exercisePassView } from "@octobeat/exercises";

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

interface MeasureData {
    groups: BeatGroup[];
    markers: { label: number; pos: number }[][];
}

/**
 * Anchura en pulsos de un grupo: el espacio que ocupa dentro de la barra.
 * Un golpe suelto ocupa 1 pulso; un grupo rítmico de N golpes, 2 pulsos
 * (salvo "[N/M:...]" que ocupa M unidades de media pulso, es decir M/2, o
 * "[F:...]" que ocupa 2/F). Coincide con `exerciseNoteDurations`, así que
 * los números de beat se alinean con la posición real de cada golpe.
 */
function groupGrowOf(
    group: BeatGroup,
): number {
    const strokes =
        group.beats[0]?.groupStrokes;

    if (strokes == null) {
        return 1;
    }

    const groupUnits =
        group.beats[0]?.groupUnits;

    const density =
        group.beats[0]?.density;

    if (groupUnits != null) {
        return groupUnits / 2;
    }

    if (density != null) {
        return 2 / density;
    }

    return 2;
}

/**
 * Marcadores de beat de cada grupo de un compás. Por cada frontera de
 * pulso dentro del grupo se calcula la posición fraccional (dentro del
 * grupo) a la que anclar el número: centrado bajo el golpe que arranca
 * el pulso cuando existe, o en la propia frontera cuando el pulso cae a
 * mitad de un grupo continuo (p. ej. un roll de 2 pulsos).
 */
function groupBeatMarkers(
    groups: BeatGroup[],
): { label: number; pos: number }[][] {
    const all: { label: number; pos: number }[][] = [];

    let startBeat = 0;

    for (const group of groups) {
        const grow = groupGrowOf(group);
        const strokes = group.beats.length;
        const strokeGrow = grow / strokes;
        const markers: { label: number; pos: number }[] = [];

        const first = Math.ceil(
            startBeat - 1e-9,
        );
        const last = Math.floor(
            startBeat + grow - 1e-9,
        );

        for (
            let beat = first;
            beat <= last;
            beat++
        ) {
            const boundary =
                beat - startBeat;
            const strokeIndex =
                Math.round(
                    boundary /
                        strokeGrow,
                );

            let pos =
                boundary / grow;

            if (
                strokeIndex >= 0 &&
                strokeIndex < strokes &&
                Math.abs(
                    strokeIndex *
                        strokeGrow -
                        boundary,
                ) < 1e-6
            ) {
                pos =
                    (strokeIndex *
                        strokeGrow +
                        strokeGrow / 2) /
                    grow;
            }

            markers.push({
                label: beat + 1,
                pos,
            });
        }

        all.push(markers);
        startBeat += grow;
    }

    return all;
}

export function ExerciseTimeline({
    exercise,
    currentBeat,
    preview = false,
    lastPass = false,
}: ExerciseTimelineProps): JSX.Element {
    // La pasada activa: los compases principales más el primer final
    // (pasadas previas) o el final definitivo (última pasada).
    const view = exercisePassView(
        exercise,
        lastPass,
    );

    const activeBeat =
        ((currentBeat - 1) %
            view.beats.length +
            view.beats.length) %
        view.beats.length;

    let currentMeasure = 0;
    let measureStart = 0;

    for (
        let i = 0;
        i < view.barLengths.length;
        i++
    ) {
        if (
            activeBeat <
            measureStart +
                view.barLengths[i]!
        ) {
            currentMeasure = i;
            break;
        }

        measureStart +=
            view.barLengths[i]!;
    }

    const measures: MeasureData[] = [];
    let offset = 0;

    for (const barLength of view.barLengths) {
        const barBeats = view.beats.slice(
            offset,
            offset + barLength,
        );
        offset += barLength;

        const groups: BeatGroup[] = [];
        let index = 0;

        while (index < barBeats.length) {
            const beat = barBeats[index]!;

            if (beat.group == null) {
                groups.push({
                    beats: [beat],
                    startIndex: offset - barLength + index,
                });
                index += 1;
                continue;
            }

            const group = beat.group;
            const groupBeats: ExerciseBeat[] = [];
            const startIndex = offset - barLength + index;

            while (
                index < barBeats.length &&
                barBeats[index]?.group ===
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

        measures.push({
            groups,
            markers: groupBeatMarkers(
                groups,
            ),
        });
    }

    return (
        <div
            className={cn(
                "w-full",
                preview ? "pt-1" : "pt-4",
            )}
        >
            <div className="flex items-center">
                {measures.map(
                    (
                        { groups, markers },
                        measureIndex,
                    ) => (
                        <Fragment key={measureIndex}>
                            {measureIndex > 0 && (
                                <div className="mx-2 flex h-8 items-center">
                                    <div className="h-full w-[2px] rounded-full bg-neutral-300" />
                                </div>
                            )}

                            <div
                                className={cn(
                                    "flex flex-1 flex-col transition-opacity duration-500",
                                    lastPass &&
                                        measureIndex <
                                            currentMeasure
                                        ? "opacity-30"
                                        : "opacity-100",
                                )}
                            >
                                <div className="flex items-center">
                                    {groups.map(
                                        (
                                            group,
                                            groupIndex,
                                        ) => (
                                            <GroupRenderer
                                                key={groupIndex}
                                                group={group}
                                                preview={preview}
                                                activeBeat={activeBeat}
                                            />
                                        ),
                                    )}
                                </div>

                                <BeatNumbersRow
                                    groups={groups}
                                    markers={markers}
                                    preview={preview}
                                />
                            </div>
                        </Fragment>
                    ),
                )}
            </div>
        </div>
    );
}

interface GroupRendererProps {
    group: BeatGroup;
    preview: boolean;
    activeBeat: number;
}

function GroupRenderer({
    group,
    preview,
    activeBeat,
}: GroupRendererProps): JSX.Element {
    const strokes =
        group.beats[0]?.groupStrokes;

    const groupUnits =
        group.beats[0]?.groupUnits;

    const density =
        group.beats[0]?.density;

    const articulation =
        group.beats[0]?.articulation;

    // Un grupo de 4 golpes sin densidad, unidades ni articulación es la
    // subdivisión por defecto: el marcador "--- N ---" es redundante y
    // no debe mostrarse.
    const isDefaultGroup =
        strokes === 4 &&
        groupUnits == null &&
        density == null &&
        articulation == null;

    // Un grupo rítmico (tresillo o roll) de N golpes dura lo mismo que
    // 2 golpes sueltos: cada golpe ocupa 2/N de la anchura de un golpe
    // suelto, de modo que la línea siempre encaja en el contenedor. Un
    // grupo "[F:...]" ocupa 2/F de esa anchura y un grupo "[N/M:...]"
    // ocupa M unidades de media pulso (anchura M/2).
    const grow = groupGrowOf(group);
    const strokeGrow =
        strokes != null
            ? grow / strokes
            : 1;

    const beats = group.beats.map(
        (beat, beatIndex) => {
            const index =
                group.startIndex +
                beatIndex;

            return (
                <BeatCell
                    key={index}
                    beat={beat}
                    grow={strokeGrow}
                    preview={preview}
                    active={
                        !preview &&
                        index ===
                            activeBeat
                    }
                />
            );
        },
    );

    return (
        <div
            className={cn(
                "relative flex min-w-0 items-center",
                strokes != null &&
                    "mx-1",
            )}
            style={{
                flexGrow: grow,
                flexBasis: 0,
            }}
        >
            {!preview &&
                strokes != null &&
                !isDefaultGroup && (
                    <div
                        className="pointer-events-none absolute left-0 right-0 flex flex-col items-center"
                        style={{ bottom: "100%" }}
                    >
                        <span className="bg-white px-1 text-xs font-black leading-none text-neutral-500">
                            {articulation != null
                                ? `${articulation} ${strokes}`
                                : strokes}
                        </span>

                        <div className="mt-0.5 h-[2px] w-full bg-neutral-400" />
                    </div>
                )}

            {beats}
        </div>
    );
}

interface BeatNumbersRowProps {
    groups: BeatGroup[];
    markers: { label: number; pos: number }[][];
    preview: boolean;
}

/**
 * Fila de números de beat (1, 2, 3, 4) bajo cada compás. Replica la
 * estructura flex de los golpes (mismos flexGrow y márgenes) para que
 * cada número quede centrado exactamente bajo el golpe que arranca el
 * pulso, anclando visualmente el beat — clave en ejercicios de tresillo.
 */
function BeatNumbersRow({
    groups,
    markers,
    preview,
}: BeatNumbersRowProps): JSX.Element {
    return (
        <div
            className={cn(
                "flex items-center",
                preview ? "h-3" : "h-4",
            )}
        >
            {groups.map((group, groupIndex) => {
                const strokes =
                    group.beats[0]
                        ?.groupStrokes;

                const grow =
                    groupGrowOf(group);

                return (
                    <div
                        key={groupIndex}
                        className={cn(
                            "relative flex min-w-0 items-center",
                            strokes != null &&
                                "mx-1",
                        )}
                        style={{
                            flexGrow: grow,
                            flexBasis: 0,
                        }}
                    >
                        {markers[
                            groupIndex
                        ]!.map((marker) => (
                            <span
                                key={marker.label}
                                className={cn(
                                    "absolute -translate-x-1/2 font-mono font-bold leading-none text-neutral-400",
                                    preview
                                        ? "text-[9px]"
                                        : "text-[10px]",
                                )}
                                style={{
                                    left: `${marker.pos * 100}%`,
                                }}
                            >
                                {marker.label}
                            </span>
                        ))}
                    </div>
                );
            })}
        </div>
    );
}

interface BeatCellProps {
    beat: ExerciseBeat;

    /**
     * Anchura proporcional del golpe en pulsos (1 para golpes sueltos,
     * 2/3 para golpes de tresillo, 1/2 para golpes de roll).
     */
    grow: number;

    preview: boolean;

    active: boolean;
}

function BeatCell({
    beat,
    grow,
    preview,
    active,
}: BeatCellProps): JSX.Element {
    const isRest = beat.rest === true;
    const dotted =
        beat.restDotted === true;
    const hasGrace =
        beat.grace != null;

    const graceMark =
        hasGrace
            ? beat.grace === beat.hand
                ? "g"
                : beat.grace === "L"
                  ? "l"
                  : "r"
            : null;

    return (
        <div
            className="relative flex min-w-0 justify-center py-0.5"
            style={{
                flexGrow: grow,
                flexBasis: 0,
            }}
        >
            {beat.accented &&
                !isRest && (
                    <div className="absolute -top-3 text-lg font-black leading-none text-neutral-700">
                        &gt;
                    </div>
                )}

            <div
                className={cn(
                    "relative z-10 flex items-baseline justify-center font-mono font-black transition-all duration-150",
                    isRest &&
                        "text-neutral-400",
                    beat.accented &&
                        !isRest &&
                        "text-red-600",
                    active
                        ? "scale-125 text-blue-500"
                        : "text-black",
                )}
                style={{
                    fontSize: preview
                        ? "clamp(0.8rem,1.1vw,1.1rem)"
                        : "clamp(1.4rem,2vw,2rem)",
                    textShadow:
                        "1px 1px 0 #e5e5e5, -1px -1px 0 #e5e5e5, 1px -1px 0 #e5e5e5, -1px 1px 0 #e5e5e5, 1px 0 0 #e5e5e5, -1px 0 0 #e5e5e5, 0 1px 0 #e5e5e5, 0 -1px 0 #e5e5e5, 0 2px 4px rgb(0 0 0 / 25%)",
                    ...(active
                        ? { WebkitTextStroke: "2px #1e40af" }
                        : {}),
                }}
            >
                {graceMark != null && (
                    <span className="-mr-0.5 text-[0.55em] opacity-40">
                        {graceMark}
                    </span>
                )}

                {isRest ? (
                    <>
                        <span>–</span>
                        {dotted && (
                            <span className="ml-px text-[0.6em]">
                                .
                            </span>
                        )}
                    </>
                ) : (
                    <span>{beat.hand}</span>
                )}
            </div>
        </div>
    );
}
