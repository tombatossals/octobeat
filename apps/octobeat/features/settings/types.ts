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
}
