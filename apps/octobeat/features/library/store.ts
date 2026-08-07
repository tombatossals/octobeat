import { create } from "zustand";

import type { Dataset } from "@octobeat/library";
import { usePlayerStore } from "@octobeat/player";

import { getLibrary } from "@/lib/library";

interface LibraryState {
    /**
     * Available dataset ids, loaded from the catalog.
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
     * Load the catalog and populate the available dataset ids.
     */
    initialize(): Promise<readonly string[]>;

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
        ids: [],

        index: 0,

        dataset: null,

        async initialize() {
            const catalog =
                await getLibrary().list();

            const ids = catalog.map(
                (entry) => entry.id,
            );

            set({ ids });

            return ids;
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