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
    const beats = parseNotation(notation);

    return {
        id,
        title,
        beatsPerBar,
        beatUnit,
        beats,
    };
}

function parseNotation(
    notation: string,
): ExerciseBeat[] {
    return notation
        .replaceAll("|", " ")
        .trim()
        .split(/\s+/)
        .filter(Boolean)
        .map((token) => ({
            hand: parseHand(token),
        }));
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
    };
}