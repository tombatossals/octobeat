import type { SongMap } from "@octobeat/songmap";

import type { LyricLine } from "./lyrics";
import type { Metadata } from "./metadata";

export type { Metadata };
export type { LyricLine, LyricSyllable } from "./lyrics";

export interface Dataset {
    metadata: Metadata;

    songmap: SongMap;

    /**
     * Synced lyrics resource (`lyrics.json`), or `null` when the
     * dataset has none.
     */
    lyrics: LyricLine[] | null;
}