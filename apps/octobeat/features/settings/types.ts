export type Theme = "dark" | "light";

export interface Settings {
    /**
     * Remote catalog location.
     */
    catalogUrl: string;

    /**
     * Preferred default difficulty (1..5).
     */
    defaultDifficulty: number;

    /**
     * Preferred genres.
     */
    preferredGenres: string[];

    /**
     * Repetitions of each exercise line before advancing.
     */
    repetitionsPerLine: number;

    /**
     * Interface color theme.
     */
    theme: Theme;
}
