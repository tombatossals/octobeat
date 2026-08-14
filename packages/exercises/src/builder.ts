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
    };
}

interface ParsedNotation {
    beats: ExerciseBeat[];
    barLengths: number[];
}

/**
 * Cada token entre corchetes (p. ej. "[RLRL]", "[gRRLL]") es un grupo
 * rítmico que dura lo mismo que dos golpes sueltos: cada golpe ocupa
 * 2/N de pulso, con N el número de golpes del grupo. Un token
 * "(3:RLR)" es un tresillo explícito con la misma regla de duración.
 * El resto de tokens son golpes sueltos, uno por letra. Cada nota
 * admite la sintaxis [grace][mano][acento] del manifiesto: "g"/"l"/"r"
 * en minúscula antecede a la mano (mayúscula) y "!" marca el acento.
 * Los compases se separan con "|" o "-".
 */
function parseNotation(
    notation: string,
): ParsedNotation {
    const beats: ExerciseBeat[] = [];
    const barLengths: number[] = [];
    let groupId = 0;

    const measures = notation
        .split(/[|\\-]/)
        .map((measure) =>
            measure.trim(),
        )
        .filter(Boolean);

    for (const measure of measures) {
        const start = beats.length;
        const tokens = measure
            .split(/\s+/)
            .filter(Boolean);

        for (const token of tokens) {
            const bracketGroup = token.match(
                /^\[([^\]]+)\]$/,
            );

            const tupletGroup = token.match(
                /^\((\d+):([^)]+)\)$/,
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
                        group: groupId,
                        groupStrokes:
                            strokes.length,
                    });
                }
            } else if (tupletGroup) {
                const strokes =
                    parseStrokes(
                        tupletGroup[2]!,
                    );

                groupId += 1;

                for (const stroke of strokes) {
                    beats.push({
                        hand: stroke.hand,
                        grace: stroke.grace,
                        accented:
                            stroke.accented,
                        rest: stroke.rest,
                        group: groupId,
                        groupStrokes:
                            strokes.length,
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
                    });
                }
            }
        }

        barLengths.push(
            beats.length - start,
        );
    }

    return { beats, barLengths };
}

interface ParsedStroke {
    hand: Hand;
    grace?: Hand;
    accented?: boolean;
    rest?: boolean;
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
            strokes.push({
                hand: "R",
                rest: true,
            });

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
 */
export function exerciseNoteDurations(
    exercise: Exercise,
): number[] {
    return exercise.beats.map((beat) =>
        beat.group == null
            ? 1
            : 2 / beat.groupStrokes!,
    );
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