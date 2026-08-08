import { create } from "zustand";

import type { Metadata } from "@octobeat/library";

import { fetchLyrics } from "./api";

import type { LyricLine } from "./types";

interface LyricsState {
    /**
     * Timed lyric lines for the current song.
     */
    lyrics: readonly LyricLine[];

    /**
     * Whether lyrics are being fetched.
     */
    loading: boolean;

    /**
     * Fetch and store lyrics for a song from LRCLIB.
     */
    load(metadata: Metadata): Promise<void>;

    /**
     * Store lyrics already embedded in the dataset.
     */
    setLyrics(lyrics: readonly LyricLine[]): void;

    /**
     * Clear the current lyrics.
     */
    clear(): void;
}

export const useLyricsStore =
    create<LyricsState>((set) => ({
        lyrics: [],

        loading: false,

        async load(metadata) {
            set({
                loading: true,
            });

            try {
                const lyrics =
                    await fetchLyrics(
                        metadata,
                    );

                set({
                    lyrics,
                    loading: false,
                });
            } catch {
                set({
                    lyrics: [],
                    loading: false,
                });
            }
        },

        setLyrics(lyrics) {
            set({
                lyrics,
                loading: false,
            });
        },

        clear() {
            set({
                lyrics: [],
                loading: false,
            });
        },
    }));
