export type Hand = "R" | "L";

/**
 * Nivel de dificultad de un libro de ejercicios.
 */
export type Difficulty = "easy" | "medium" | "hard";

/**
 * Orden de dificultad de menor a mayor, usado para ordenar libros.
 */
export const DIFFICULTY_ORDER: readonly Difficulty[] = [
    "easy",
    "medium",
    "hard",
];

/**
 * Etiqueta de visualización para cada nivel de dificultad.
 */
export const DIFFICULTY_LABELS: Record<Difficulty, string> = {
    easy: "Easy",
    medium: "Medium",
    hard: "Hard",
};

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

    /**
     * Número de unidades temporales equivalentes que ocupa el grupo
     * (la `M` de `(N/M:...)` o `[N/M:...]`, p. ej. 2 en "[3/2:RLR]").
     * Cuando está presente, el grupo de `groupStrokes` golpes se
     * distribuye sobre esas unidades; sin él, el grupo ocupa dos golpes
     * sueltos.
     */
    groupUnits?: number;

    /**
     * Factor de compresión temporal del grupo (la `N` de "[N:...]",
     * p. ej. 2 en "[2:RLRL]"). El grupo ocupa la mitad, un tercio…
     * del tiempo que ocuparía sin prefijo. Cuando está presente, no
     * hay `groupUnits`.
     */
    density?: number;

    /**
     * Articulación que afecta a todo el grupo (la `art` de
     * "[art:N/M:...]" o "[art:...]", p. ej. "openroll" en
     * "[openroll:9/4:RRLLRRLLR]"). No altera la duración del grupo y
     * se conserva en cada golpe que lo compone.
     */
    articulation?: string;
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

    /**
     * Nivel de dificultad del libro (p. ej. "easy", "medium").
     */
    difficulty: Difficulty;

    sets: Record<string, ExerciseSet>;
}