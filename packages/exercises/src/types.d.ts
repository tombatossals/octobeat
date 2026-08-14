export type Hand = "R" | "L";
export interface ExerciseBeat {
    /**
     * Mano del golpe. Para silencios no es significativa (se usa "R"
     * como valor interno).
     */
    hand: Hand;
    /**
     * Silencio: este hueco rítmico no suena pero mantiene su duración.
     */
    rest?: boolean;
    /**
     * Silencio con puntillo ("__"): dura una subdivisión y media.
     */
    restDotted?: boolean;
    /**
     * Final alternativo al que pertenece este golpe: el primer final
     * se toca en todas las repeticiones menos la última; el final
     * definitivo solo en la última.
     */
    ending?: "1st" | "final";
    /**
     * Mano del grace note / flam que precede a este golpe. Su presencia
     * indica que el golpe lleva adorno (p. ej. "gR", "lR").
     */
    grace?: Hand;
    /**
     * Golpe acentuado (dinámica no estándar).
     */
    accented?: boolean;
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
    /**
     * Finales alternativos ({1st: ...} / {final: ...}): índice de
     * compás donde empieza cada final dentro de `barLengths`. Sin
     * este campo el ejercicio se repite completo en cada pasada.
     */
    endings?: {
        /** Índice de compás donde empieza el primer final. */
        first?: number;
        /** Índice de compás donde empieza el final definitivo. */
        final?: number;
    };
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
