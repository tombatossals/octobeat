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
 * Cada token de 3 letras (p. ej. "RLR", "LRL") es un tresillo; el resto
 * de tokens son golpes sueltos, uno por letra. Los compases se separan
 * con "|" o "-".
 */
function parseNotation(
    notation: string,
): ParsedNotation {
    const beats: ExerciseBeat[] = [];
    const barLengths: number[] = [];
    let tripletId = 0;

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
            if (token.length === 3) {
                tripletId += 1;

                for (const hand of token) {
                    beats.push({
                        hand: parseHand(hand),
                        triplet: tripletId,
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