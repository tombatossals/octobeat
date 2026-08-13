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
 * Cada token entre corchetes (p. ej. "[RLRL]", "[RLR]") es un grupo
 * rítmico que dura lo mismo que dos golpes sueltos: cada golpe ocupa
 * 2/N de pulso, con N el número de letras del grupo. Un token de 3
 * letras sin corchetes (p. ej. "RLR") también es un tresillo. El resto
 * de tokens son golpes sueltos, uno por letra. Los compases se separan
 * con "|" o "-".
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
                /^\[([RLrl]+)\]$/,
            );

            if (bracketGroup) {
                const hands =
                    bracketGroup[1]!;

                groupId += 1;

                for (const hand of hands) {
                    beats.push({
                        hand: parseHand(hand),
                        group: groupId,
                        groupStrokes:
                            hands.length,
                    });
                }
            } else if (
                token.length === 3
            ) {
                groupId += 1;

                for (const hand of token) {
                    beats.push({
                        hand: parseHand(hand),
                        group: groupId,
                        groupStrokes: 3,
                    });
                }
            } else {
                for (const hand of token) {
                    beats.push({
                        hand: parseHand(hand),
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