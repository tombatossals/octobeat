import type { Exercise } from "./types";
export interface CreateExerciseOptions {
    id: string;
    title: string;
    notation: string;
    beatsPerBar?: number;
    beatUnit?: number;
}
export declare function createExercise({ id, title, notation, beatsPerBar, beatUnit, }: CreateExerciseOptions): Exercise;
/**
 * Subdivide every beat of an exercise, producing `factor`
 * alternating notes per original beat.
 */
export declare function subdivideExercise(exercise: Exercise, factor: number): Exercise;
