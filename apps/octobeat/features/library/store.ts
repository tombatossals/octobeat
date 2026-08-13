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

        async initialize() {
            const catalog =
                await getLibrary().list();

            const filters =
                loadFilters();

            const ids = shuffle(
                catalog
                    .filter((entry) =>
                        matchesFilters(
                            entry,
                            filters,
                        ),
                    )
                    .map(
                        (entry) =>
                            entry.id,
                    ),
            );

            set({
                entries: catalog,
                filters,
                ids,
            });

            return ids;
        },

        setFilters(filters) {
            saveFilters(filters);

            const ids = shuffle(
                get()
                    .entries.filter(
                        (entry) =>
                            matchesFilters(
                                entry,
                                filters,
                            ),
                    )
                    .map(
                        (entry) =>
                            entry.id,
                    ),
            );

            set({ filters, ids });
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