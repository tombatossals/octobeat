import type { Metadata } from "@octobeat/library";

import { genreGroupKeys } from "./genres";

export interface LibraryFilters {
    /**
     * Selected BPM range keys, e.g. "100-120".
     */
    bpmRanges: string[];

    /**
     * Selected big genre keys, e.g. "rock".
     */
    genres: string[];

    /**
     * Selected decade keys, e.g. "80s".
     */
    decades: string[];

    /**
     * Selected exercise set ids to practice (e.g. "01-single-beat-combinations").
     */
    exerciseSets: string[];

    /**
     * Whether to restrict the queue to favorite songs.
     */
    favoritesOnly: boolean;
}

export const BPM_RANGES: ReadonlyArray<{
    key: string;
    label: string;
    min: number;
    max: number;
}> = [
    { key: "40-80", label: "40–80", min: 40, max: 80 },
    { key: "80-120", label: "80–120", min: 80, max: 120 },
    { key: "120-160", label: "120–160", min: 120, max: 160 },
    { key: "160-200", label: "160–200", min: 160, max: 200 },
    { key: "200-", label: "200–", min: 200, max: Infinity },
];

export const DECADES: ReadonlyArray<{
    key: string;
    label: string;
    min: number;
    max: number;
}> = [
    { key: "80s", label: "80s", min: 1980, max: 1989 },
    { key: "90s", label: "90s", min: 1990, max: 1999 },
    { key: "2000s", label: "2000s", min: 2000, max: 2009 },
    { key: "2010s", label: "2010s", min: 2010, max: 2019 },
    { key: "2020s", label: "2020s", min: 2020, max: 2029 },
];

export const EMPTY_FILTERS: LibraryFilters = {
    bpmRanges: [],
    genres: [],
    decades: [],
    exerciseSets: [],
    favoritesOnly: false,
};

export function isEmptyFilters(
    filters: LibraryFilters,
): boolean {
    return (
        filters.bpmRanges.length === 0 &&
        filters.genres.length === 0 &&
        filters.decades.length === 0 &&
        filters.exerciseSets.length === 0 &&
        !filters.favoritesOnly
    );
}

/**
 * Returns whether an entry matches the given filters. Empty criteria
 * match everything; each non-empty criterion is an OR within itself and
 * AND across criteria. `favoriteIds` is required to evaluate the
 * favorites-only criterion.
 */
export function matchesFilters(
    entry: Metadata,
    filters: LibraryFilters,
    favoriteIds: ReadonlySet<string> = new Set(),
): boolean {
    if (
        filters.favoritesOnly &&
        !favoriteIds.has(entry.id)
    ) {
        return false;
    }

    if (filters.bpmRanges.length > 0) {
        const matchesBpm = filters.bpmRanges.some(
            (key) => {
                const range =
                    BPM_RANGES.find(
                        (candidate) =>
                            candidate.key ===
                            key,
                    );

                if (!range) {
                    return false;
                }

                return (
                    entry.bpm >=
                        range.min &&
                    entry.bpm <
                        range.max
                );
            },
        );

        if (!matchesBpm) {
            return false;
        }
    }

    if (filters.genres.length > 0) {
        const entryKeys =
            genreGroupKeys(
                entry.genres,
            );

        const matchesGenre =
            filters.genres.some(
                (key) =>
                    entryKeys.has(key),
            );

        if (!matchesGenre) {
            return false;
        }
    }

    if (filters.decades.length > 0) {
        const year = entry.year;

        if (year == null) {
            return false;
        }

        const matchesDecade =
            filters.decades.some(
                (key) => {
                    const decade =
                        DECADES.find(
                            (candidate) =>
                                candidate.key ===
                                key,
                        );

                    if (!decade) {
                        return false;
                    }

                    return (
                        year >=
                            decade.min &&
                        year <=
                            decade.max
                    );
                },
            );

        if (!matchesDecade) {
            return false;
        }
    }

    return true;
}
