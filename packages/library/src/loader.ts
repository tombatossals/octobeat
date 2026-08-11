import {
    SongMapSchema,
    type SongMap,
} from "@octobeat/songmap";

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

        const response =
            await fetch(
                `${datasetUrl}/songmap.json`,
            );

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
                    audio: `${datasetUrl}/${metadata.resources.audio}`,
                },
            },
            songmap,
        };
    }
}