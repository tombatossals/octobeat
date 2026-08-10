import { create } from "zustand";

import type { Dataset } from "@octobeat/library";
import { usePlayerStore } from "@octobeat/player";

import { getLibrary } from "@/lib/library";

import { getManualOffset } from "@/features/player/videoOffsetStorage";

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

            const ids = shuffle(
                catalog.map(
                    (entry) => entry.id,
                ),
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

            // Reset the video offset while the new dataset loads so a
            // stale offset never positions the new video incorrectly.
            usePlayerStore
                .getState()
                .setVideoOffset(0);

            const dataset =
                await getLibrary().load(
                    id,
                );

            // A manual correction (made in the UI) overrides the SongMap
            // offset; otherwise use the synced offset.
            const manualOffset =
                getManualOffset(id);

            const videoOffset =
                manualOffset
                ?? dataset.songmap.media
                    ?.video?.offset
                ?? 0;

            usePlayerStore
                .getState()
                .setVideoOffset(
                    videoOffset,
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