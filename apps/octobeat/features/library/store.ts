import { create } from "zustand";

import type { Dataset, Metadata } from "@octobeat/library";
import { usePlayerStore } from "@octobeat/player";

import { getLibrary } from "@/lib/library";

import {
    EMPTY_FILTERS,
    matchesFilters,
} from "./filters";
import type { LibraryFilters } from "./filters";

import {
    loadFilters,
    saveFilters,
} from "./filterStorage";

import {
    loadFavorites,
    saveFavorites,
} from "./favoritesStorage";

/**
 * Fisher-Yates shuffle. Returns a new array.
 */
function shuffle<T>(items: readonly T[]): T[] {
    const result = [...items];

    for (let i = result.length - 1; i > 0; i--) {
        const j = Math.floor(
            Math.random() * (i + 1),
        );

        [result[i], result[j]] = [
            result[j],
            result[i],
        ];
    }

    return result;
}

/**
 * Rebuilds the playback queue from the catalog using the given filters
 * and favorites.
 */
function computeIds(
    entries: readonly Metadata[],
    filters: LibraryFilters,
    favorites: readonly string[],
): string[] {
    const favoriteIds =
        new Set(favorites);

    return shuffle(
        entries
            .filter((entry) =>
                matchesFilters(
                    entry,
                    filters,
                    favoriteIds,
                ),
            )
            .map(
                (entry) =>
                    entry.id,
            ),
    );
}

interface LibraryState {
    /**
     * Full catalog entries, kept so filters can be re-applied without
     * re-fetching.
     */
    entries: readonly Metadata[];

    /**
     * Available dataset ids, filtered and shuffled.
     */
    ids: string[];

    /**
     * Current dataset index.
     */
    index: number;

    /**
     * Loaded dataset.
     */
    dataset: Dataset | null;

    /**
     * Active filters applied to the playback queue.
     */
    filters: LibraryFilters;

    /**
     * Dataset ids marked as favorites.
     */
    favorites: string[];

    /**
     * Load the catalog and populate the available dataset ids.
     */
    initialize(): Promise<readonly string[]>;

    /**
     * Update the active filters and rebuild the playback queue.
     */
    setFilters(
        filters: LibraryFilters,
    ): void;

    /**
     * Toggle whether a dataset is a favorite.
     */
    toggleFavorite(id: string): void;

    /**
     * Returns whether a dataset is a favorite.
     */
    isFavorite(id: string): boolean;

    /**
     * Open a dataset by id.
     */
    open(id: string): Promise<void>;

    /**
     * Open the next dataset.
     */
    next(): Promise<void>;

    /**
     * Open the previous dataset.
     */
    previous(): Promise<void>;

    /**
     * Close the current dataset.
     */
    close(): void;
}

export const useLibraryStore =
    create<LibraryState>((set, get) => ({
        entries: [],

        ids: [],

        index: 0,

        dataset: null,

        filters: EMPTY_FILTERS,

        favorites: [],

        async initialize() {
            const catalog =
                await getLibrary().list();

            const filters =
                loadFilters();

            const favorites =
                loadFavorites();

            const ids = computeIds(
                catalog,
                filters,
                favorites,
            );

            set({
                entries: catalog,
                filters,
                favorites,
                ids,
            });

            return ids;
        },

        setFilters(filters) {
            saveFilters(filters);

            const { entries, favorites } =
                get();

            set({
                filters,
                ids: computeIds(
                    entries,
                    filters,
                    favorites,
                ),
            });
        },

        toggleFavorite(id) {
            const favorites =
                get().favorites;

            const next =
                favorites.includes(id)
                    ? favorites.filter(
                          (favorite) =>
                              favorite !==
                              id,
                      )
                    : [...favorites, id];

            saveFavorites(next);

            const {
                entries,
                filters,
            } = get();

            set(
                filters.favoritesOnly
                    ? {
                          favorites: next,
                          ids: computeIds(
                              entries,
                              filters,
                              next,
                          ),
                      }
                    : { favorites: next },
            );
        },

        isFavorite(id) {
            return get().favorites.includes(
                id,
            );
        },

        async open(id: string) {
            // Stop the current recording before switching datasets so
            // the previous player stops emitting position updates and
            // the new recording starts from a clean slate.
            usePlayerStore
                .getState()
                .stop();

            const dataset =
                await getLibrary().load(
                    id,
                );

            const index =
                get().ids.indexOf(id);

            set({
                dataset,
                index:
                    index >= 0
                        ? index
                        : 0,
            });
        },

        async next() {
            const {
                ids,
                index,
            } = get();

            const next =
                (index + 1) %
                ids.length;

            await get().open(
                ids[next],
            );
        },

        async previous() {
            const {
                ids,
                index,
            } = get();

            const previous =
                (index - 1 + ids.length) %
                ids.length;

            await get().open(
                ids[previous],
            );
        },

        close() {
            set({
                dataset: null,
            });
        },
    }));