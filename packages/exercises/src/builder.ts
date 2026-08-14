import type {
    Exercise,
    ExerciseBeat,
    Hand,
} from "./types";

export interface CreateExerciseOptions {
    id: string;

    title: string;

    notation: string;

    beatsPerBar?: number;

    beatUnit?: number;
}

export function createExercise({
    id,
    title,
    notation,
    beatsPerBar = 4,
    beatUnit = 4,
}: CreateExerciseOptions): Exercise {
    const parsed = parseNotation(notation);

    return {
        id,
        title,
        beatsPerBar,
        beatUnit,
        beats: parsed.beats,
        barLengths: parsed.barLengths,
        endings: parsed.endings,
    };
}

interface ParsedNotation {
    beats: ExerciseBeat[];
    barLengths: number[];
    endings?: {
        first?: number;
        final?: number;
    };
}

/**
 * Cada token entre corchetes (p. ej. "[RLRL]", "[gRRLL]") es un grupo
 * rítmico que dura lo mismo que dos golpes sueltos: cada golpe ocupa
 * 2/N de pulso, con N el número de golpes del grupo. Un token
 * "(3:RLR)" es un tresillo explícito con la misma regla de duración;
 * "(N/M:...)" indica además el número M de unidades temporales que
 * ocupa el grupo (cada unidad equivale a media pulso).
 * El resto de tokens son golpes sueltos, uno por letra. Cada nota
 * admite la sintaxis [grace][mano][acento] del manifiesto: "g"/"l"/"r"
 * en minúscula antecede a la mano (mayúscula), "!" marca el acento y
 * "_" es un silencio ("__" con puntillo). Los compases se separan con
 * "|" o "-". Los finales alternativos "{1st: ... }" y "{final: ... }"
 * se marcan como compases propios dentro del ejercicio.
 */
function parseNotation(
    notation: string,
): ParsedNotation {
    const beats: ExerciseBeat[] = [];
    const barLengths: number[] = [];
    const endings: {
        first?: number;
        final?: number;
    } = {};
    let groupId = 0;
    let barIndex = 0;

    const measures = notation
        .split(/[|\\-]/)
        .map((measure) =>
            measure.trim(),
        )
        .filter(Boolean);

    const parseBar = (
        text: string,
        ending?: "1st" | "final",
    ) => {
        const start = beats.length;
        const tokens = text
            .split(/\s+/)
            .filter(Boolean);

        for (const token of tokens) {
            const bracketGroup = token.match(
                /^\[([^\]]+)\]$/,
            );

            const tupletGroup = token.match(
                /^\((\d+)(?:\/(\d+))?:([^)]+)\)$/,
            );

            if (bracketGroup) {
                const strokes =
                    parseStrokes(
                        bracketGroup[1]!,
                    );

                groupId += 1;

                for (const stroke of strokes) {
                    beats.push({
                        hand: stroke.hand,
                        grace: stroke.grace,
                        accented:
                            stroke.accented,
                        rest: stroke.rest,
                        restDotted:
                            stroke.restDotted,
                        ending,
                        group: groupId,
                        groupStrokes:
                            strokes.length,
                    });
                }
            } else if (tupletGroup) {
                const strokes =
                    parseStrokes(
                        tupletGroup[3]!,
                    );

                const units =
                    tupletGroup[2] != null
                        ? Number(
                              tupletGroup[2],
                          )
                        : undefined;

                groupId += 1;

                for (const stroke of strokes) {
                    beats.push({
                        hand: stroke.hand,
                        grace: stroke.grace,
                        accented:
                            stroke.accented,
                        rest: stroke.rest,
                        restDotted:
                            stroke.restDotted,
                        ending,
                        group: groupId,
                        groupStrokes:
                            strokes.length,
                        ...(units != null
                            ? { groupUnits: units }
                            : {}),
                    });
                }
            } else {
                for (const stroke of parseStrokes(
                    token,
                )) {
                    beats.push({
                        hand: stroke.hand,
                        grace: stroke.grace,
                        accented:
                            stroke.accented,
                        rest: stroke.rest,
                        restDotted:
                            stroke.restDotted,
                        ending,
                    });
                }
            }
        }

        barLengths.push(
            beats.length - start,
        );

        if (ending === "1st") {
            endings.first = barIndex;
        } else if (ending === "final") {
            endings.final = barIndex;
        }

        barIndex += 1;
    };

    for (const measure of measures) {
        const endingPattern =
            /{(1st|final):\s*([^}]*)}/g;

        let match: RegExpExecArray | null;
        let lastIndex = 0;
        let found = false;

        while (
            (match =
                endingPattern.exec(
                    measure,
                )) !== null
        ) {
            found = true;

            const before = measure
                .slice(lastIndex, match.index)
                .trim();

            if (before) {
                parseBar(before);
            }

            const kind =
                match[1] === "1st"
                    ? "1st"
                    : "final";

            parseBar(match[2]!, kind);

            lastIndex =
                endingPattern.lastIndex;
        }

        const rest = measure
            .slice(lastIndex)
            .trim();

        if (found) {
            if (rest) {
                parseBar(rest);
            }
        } else if (rest) {
            parseBar(rest);
        }
    }

    return {
        beats,
        barLengths,
        endings:
            endings.first != null ||
            endings.final != null
                ? endings
                : undefined,
    };
}

interface ParsedStroke {
    hand: Hand;
    grace?: Hand;
    accented?: boolean;
    rest?: boolean;
    restDotted?: boolean;
}

/**
 * Parsea una secuencia de notas (dentro de un grupo o suelta) con la
 * sintaxis [grace][mano][acento]: "g"/"l"/"r" en minúscula marcan un
 * grace note antes de la mano (mayúscula), "!" marca el acento y "_"
 * es un silencio que ocupa el hueco rítmico sin sonar. "g" usa la
 * misma mano que la nota principal; "l"/"r" fuerzan la mano del adorno.
 */
function parseStrokes(
    text: string,
): ParsedStroke[] {
    const strokes: ParsedStroke[] = [];

    for (let i = 0; i < text.length; i++) {
        const c = text[i]!;

        if (c === "_") {
            if (text[i + 1] === "_") {
                strokes.push({
                    hand: "R",
                    rest: true,
                    restDotted: true,
                });

                i += 1;
            } else {
                strokes.push({
                    hand: "R",
                    rest: true,
                });
            }

            continue;
        }

        if (c === "!") {
            const last =
                strokes[strokes.length - 1];

            if (!last) {
                throw new Error(
                    `Unexpected accent marker "!" in "${text}".`,
                );
            }

            last.accented = true;

            continue;
        }

        if (c === "g" || c === "l" || c === "r") {
            const next = text[i + 1];

            if (
                next == null ||
                !/[RL]/.test(next)
            ) {
                throw new Error(
                    `Grace note "${c}" must be followed by a hand in "${text}".`,
                );
            }

            const hand = parseHand(next);

            strokes.push({
                hand,
                grace:
                    c === "g"
                        ? hand
                        : c === "l"
                          ? "L"
                          : "R",
            });

            i += 1;

            continue;
        }

        strokes.push({
            hand: parseHand(c),
        });
    }

    return strokes;
}

function parseHand(
    token: string,
): Hand {
    const hand = token.toUpperCase();

    if (hand !== "R" && hand !== "L") {
        throw new Error(
            `Invalid hand "${token}". Expected "R" or "L".`,
        );
    }

    return hand;
}

/**
 * Duración en pulsos de cada golpe de un ejercicio. Un golpe suelto
 * ocupa 1 pulso; los golpes de un grupo rítmico (tresillo o roll)
 * ocupan 2/N de pulso, ya que un grupo de N golpes dura lo mismo que
 * dos golpes sueltos (p. ej. un tresillo LRL dura lo mismo que un LR).
 * Un grupo "(N/M:...)" se distribuye sobre M unidades equivalentes de
 * media pulso: cada golpe ocupa M/(2N) de pulso. Un silencio con
 * puntillo ("__") dura una subdivisión y media.
 */
export function exerciseNoteDurations(
    exercise: Exercise,
): number[] {
    return exercise.beats.map((beat) => {
        const base =
            beat.group == null
                ? 1
                : beat.groupUnits != null
                  ? beat.groupUnits /
                    (2 * beat.groupStrokes!)
                  : 2 / beat.groupStrokes!;

        return beat.restDotted
            ? base * 1.5
            : base;
    });
}

/**
 * Vista de un ejercicio para una pasada concreta. Cuando el ejercicio
 * tiene finales alternativos, todas las pasadas salvo la última tocan
 * los compases principales seguidos del primer final; la última pasada
 * toca los compases principales seguidos del final definitivo.
 */
export function exercisePassView(
    exercise: Exercise,
    lastPass: boolean,
): {
    beats: ExerciseBeat[];
    barLengths: number[];
} {
    const { first, final } =
        exercise.endings ?? {};

    if (first == null && final == null) {
        return {
            beats: exercise.beats,
            barLengths: exercise.barLengths,
        };
    }

    const firstBar = first ?? 0;
    const finalBar =
        final ??
        exercise.barLengths.length;

    let mainBeats = 0;

    for (
        let i = 0;
        i < firstBar;
        i++
    ) {
        mainBeats += exercise.barLengths[i]!;
    }

    let firstEndingBeats = 0;

    for (
        let i = firstBar;
        i < finalBar;
        i++
    ) {
        firstEndingBeats +=
            exercise.barLengths[i]!;
    }

    if (lastPass) {
        return {
            beats: [
                ...exercise.beats.slice(
                    0,
                    mainBeats,
                ),
                ...exercise.beats.slice(
                    mainBeats +
                        firstEndingBeats,
                ),
            ],
            barLengths: [
                ...exercise.barLengths.slice(
                    0,
                    firstBar,
                ),
                ...exercise.barLengths.slice(
                    finalBar,
                ),
            ],
        };
    }

    return {
        beats: exercise.beats.slice(
            0,
            mainBeats + firstEndingBeats,
        ),
        barLengths: exercise.barLengths.slice(
            0,
            finalBar,
        ),
    };
}

/**
 * Duración total del ejercicio en pulsos (la suma de las duraciones
 * de todos sus golpes).
 */
export function exerciseDurationInBeats(
    exercise: Exercise,
): number {
    return exerciseNoteDurations(
        exercise,
    ).reduce((sum, duration) => sum + duration, 0);
}

/**
 * Subdivide every beat of an exercise, producing `factor`
 * alternating notes per original beat.
 */
export function subdivideExercise(
    exercise: Exercise,
    factor: number,
): Exercise {
    const firstHand =
        exercise.beats[0]?.hand ?? "R";

    const beats: ExerciseBeat[] =
        [];

    for (
        let i = 0;
        i <
        exercise.beats.length *
            factor;
        i++
    ) {
        beats.push({
            hand:
                (firstHand === "R"
                    ? i % 2 === 0
                    : i % 2 === 1)
                    ? "R"
                    : "L",
        });
    }

    return {
        ...exercise,
        id: `${exercise.id}-x${factor}`,
        beats,
        barLengths: exercise.barLengths.map(
            (length) =>
                length * factor,
        ),
    };
}