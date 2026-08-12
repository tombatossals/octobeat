export type Hand = "R" | "L";

export interface ExerciseBeat {
    hand: Hand;

    /**
     * Grupo de tresillo al que pertenece este golpe. Todos los golpes
     * de un mismo tresillo comparten el mismo id; los golpes sueltos
     * no tienen este campo.
     */
    triplet?: number;
}

export interface Exercise {
    id: string;

    title: string;

    beatsPerBar: number;

    beatUnit: number;

    beats: ExerciseBeat[];

    /**
     * Número de golpes de cada compás. Con tresillos los compases
     * pueden tener longitudes distintas.
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