import {
    EMPTY_FILTERS,
} from "./filters";
import type { LibraryFilters } from "./filters";

import { GENRE_GROUP_BY_KEY } from "./genres";

const STORAGE_KEY =
    "octobeat.filters";

function hasStorage(): boolean {
    return typeof window !== "undefined";
}

/**
 * Loads filters from localStorage. Falls back to empty filters when the
 * stored value is missing or invalid.
 */
export function loadFilters(): LibraryFilters {
    if (!hasStorage()) {
        return EMPTY_FILTERS;
    }

    const raw =
        window.localStorage.getItem(
            STORAGE_KEY,
        );

    if (!raw) {
        return EMPTY_FILTERS;
    }

    try {
        const parsed =
            JSON.parse(raw) as Partial<LibraryFilters>;

        return {
            bpmRanges: Array.isArray(
                parsed.bpmRanges,
            )
                ? parsed.bpmRanges
                : [],
            genres: Array.isArray(
                parsed.genres,
            )
                ? parsed.genres.filter(
                      (genre) =>
                          genre in
                          GENRE_GROUP_BY_KEY,
                  )
                : [],
            decades: Array.isArray(
                parsed.decades,
            )
                ? parsed.decades
                : [],
            favoritesOnly:
                parsed.favoritesOnly ===
                true,
        };
    } catch {
        return EMPTY_FILTERS;
    }
}

/**
 * Persists filters to localStorage.
 */
export function saveFilters(
    filters: LibraryFilters,
): void {
    if (!hasStorage()) {
        return;
    }

    window.localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(filters),
    );
}

/**
 * Removes persisted filters.
 */
export function clearFilters(): void {
    if (!hasStorage()) {
        return;
    }

    window.localStorage.removeItem(
        STORAGE_KEY,
    );
}
