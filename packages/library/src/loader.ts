import {
    SongMapSchema,
    type SongMap,
} from "@octobeat/songmap";

import {
    parseLyrics,
    type LyricLine,
} from "./lyrics";

import type {
    Dataset,
    Metadata,
} from "./types";

/**
 * Dataset loader.
 */
export class Loader {
    constructor(
        private readonly baseUrl: string,
    ) { }

    /**
     * Loads a dataset.
     */
    async load(
        metadata: Metadata,
    ): Promise<Dataset> {
        const datasetUrl =
            `${this.baseUrl}/${metadata.id}`;

        const [response, lyrics] =
            await Promise.all([
                fetch(
                    `${datasetUrl}/songmap.json`,
                ),
                this.loadLyrics(
                    datasetUrl,
                    metadata,
                ),
            ]);

        if (!response.ok) {
            throw new Error(
                `Unable to load dataset '${metadata.id}'.`,
            );
        }

        const songmap =
            SongMapSchema.parse(
                await response.json(),
            );

        return {
            metadata: {
                ...metadata,
                resources: {
                    ...metadata.resources,
                    audio: `${datasetUrl}/${metadata.resources.audio}`,
                },
            },
            songmap,
            lyrics,
        };
    }

    /**
     * Loads the dataset's synced lyrics resource, if present.
     */
    private async loadLyrics(
        datasetUrl: string,
        metadata: Metadata,
    ): Promise<LyricLine[] | null> {
        const resource =
            metadata.resources.lyrics;

        if (!resource) {
            return null;
        }

        const response = await fetch(
            `${datasetUrl}/${resource}`,
        );

        if (!response.ok) {
            return null;
        }

        try {
            return parseLyrics(
                await response.json(),
            );
        } catch {
            return null;
        }
    }
}