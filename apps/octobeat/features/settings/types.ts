export type Theme = "dark" | "light";

export interface Settings {
    /**
     * Remote catalog location.
     */
    catalogUrl: string;

    /**
     * Repetitions of each exercise line before advancing.
     */
    repetitionsPerLine: number;

    /**
     * Interface color theme.
     */
    theme: Theme;
}
