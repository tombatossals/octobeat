import type { Metadata } from "@octobeat/library";

export interface LibraryFilters {
    /**
     * Selected BPM range keys, e.g. "100-120".
     */
    bpmRanges: string[];

    /**
     * Selected genre names.
     */
    genres: string[];

    /**
     * Selected decade keys, e.g. "80s".
     */
    decades: string[];

    /**
     * Selected exercise set ids to practice (e.g. "single-beat-combinations").
     */
    exerciseSets: string[];
}

export const BPM_RANGES: ReadonlyArray<{
    key: string;
    label: string;
    min: number;
    max: number;
}> = [
    { key: "40-60", label: "40–60", min: 40, max: 60 },
    { key: "60-80", label: "60–80", min: 60, max: 80 },
    { key: "80-100", label: "80–100", min: 80, max: 100 },
    { key: "100-120", label: "100–120", min: 100, max: 120 },
    { key: "120-140", label: "120–140", min: 120, max: 140 },
    { key: "140-160", label: "140–160", min: 140, max: 160 },
    { key: "160-180", label: "160–180", min: 160, max: 180 },
    { key: "180-200", label: "180–200", min: 180, max: 200 },
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
};

export function isEmptyFilters(
    filters: LibraryFilters,
): boolean {
    return (
        filters.bpmRanges.length === 0 &&
        filters.genres.length === 0 &&
        filters.decades.length === 0 &&
        filters.exerciseSets.length === 0
    );
}

/**
 * Returns whether an entry matches the given filters. Empty criteria
 * match everything; each non-empty criterion is an OR within itself and
 * AND across criteria.
 */
export function matchesFilters(
    entry: Metadata,
    filters: LibraryFilters,
): boolean {
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
        const matchesGenre =
            filters.genres.some(
                (genre) =>
                    entry.genres.includes(
                        genre,
                    ),
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
