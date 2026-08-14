import type { Exercise, ExerciseBeat } from "./types";
export interface CreateExerciseOptions {
    id: string;
    title: string;
    notation: string;
    beatsPerBar?: number;
    beatUnit?: number;
}
export declare function createExercise({ id, title, notation, beatsPerBar, beatUnit, }: CreateExerciseOptions): Exercise;
/**
 * Duración en pulsos de cada golpe de un ejercicio. Un golpe suelto
 * ocupa 1 pulso; los golpes de un grupo rítmico (tresillo o roll)
 * ocupan 2/N de pulso, ya que un grupo de N golpes dura lo mismo que
 * dos golpes sueltos (p. ej. un tresillo LRL dura lo mismo que un LR).
 * Un silencio con puntillo ("__") dura una subdivisión y media.
 */
export declare function exerciseNoteDurations(exercise: Exercise): number[];
/**
 * Vista de un ejercicio para una pasada concreta. Cuando el ejercicio
 * tiene finales alternativos, todas las pasadas salvo la última tocan
 * los compases principales seguidos del primer final; la última pasada
 * toca los compases principales seguidos del final definitivo.
 */
export declare function exercisePassView(exercise: Exercise, lastPass: boolean): {
    beats: ExerciseBeat[];
    barLengths: number[];
};
/**
 * Duración total del ejercicio en pulsos (la suma de las duraciones
 * de todos sus golpes).
 */
export declare function exerciseDurationInBeats(exercise: Exercise): number;
/**
 * Subdivide every beat of an exercise, producing `factor`
 * alternating notes per original beat.
 */
export declare function subdivideExercise(exercise: Exercise, factor: number): Exercise;
