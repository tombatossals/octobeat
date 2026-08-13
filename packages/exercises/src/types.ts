export type Hand = "R" | "L";

export interface ExerciseBeat {
    hand: Hand;

    /**
     * Grupo rítmico al que pertenece este golpe (un tresillo, un roll…).
     * Todos los golpes de un mismo grupo comparten el mismo id; los
     * golpes sueltos no tienen este campo.
     */
    group?: number;

    /**
     * Número de golpes del grupo (3 en un tresillo, 4 en un roll de
     * golpe simple).
     */
    groupStrokes?: number;
}

export interface Exercise {
    id: string;

    title: string;

    beatsPerBar: number;

    beatUnit: number;

    beats: ExerciseBeat[];

    /**
     * Número de golpes de cada compás. Con grupos rítmicos (tresillos,
     * rolls…) los compases pueden tener longitudes distintas.
     */
    barLengths: number[];
}

/**
 * Un conjunto de ejercicios dentro de un libro (p. ej. "Single Beat
 * Combinations" o "Triplets").
 */
export interface ExerciseSet {
    id: string;

    title: string;

    exercises: Record<string, Exercise>;
}

export interface ExerciseBook {
    id: string;

    title: string;

    sets: Record<string, ExerciseSet>;
}