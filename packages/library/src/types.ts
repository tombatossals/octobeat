import type { SongMap } from "@octobeat/songmap";

import type { Metadata } from "./metadata";

export type { Metadata };

export interface Dataset {
    metadata: Metadata;

    songmap: SongMap;
}