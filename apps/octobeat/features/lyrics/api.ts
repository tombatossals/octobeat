import type { Metadata } from "@octobeat/library";

import type { LyricLine } from "./types";

const LRCLIB_API = "https://lrclib.net/api";

/**
 * Parses an LRC document into timed lyric lines.
 */
export function parseLRC(
    lrc: string,
): LyricLine[] {
    const lines: LyricLine[] = [];

    const timestamp =
        /\[(\d{1,2}):(\d{1,2})(?:\.(\d{1,3}))?\]/g;

    for (const raw of lrc.split("\n")) {
        const matches = [
            ...raw.matchAll(timestamp),
        ];

        if (matches.length === 0) {
            continue;
        }

        const text = raw
            .replace(timestamp, "")
            .trim();

        if (!text) {
            continue;
        }

        for (const match of matches) {
            const minutes = parseInt(
                match[1]!,
                10,
            );

            const seconds = parseInt(
                match[2]!,
                10,
            );

            const fraction = match[3]
                ? parseInt(
                      match[3].padEnd(
                          3,
                          "0",
                      ),
                      10,
                  ) / 1000
                : 0;

            lines.push({
                time:
                    minutes * 60 +
                    seconds +
                    fraction,
                text,
            });
        }
    }

    return lines.sort(
        (a, b) => a.time - b.time,
    );
}

/**
 * Returns the last lyric line whose timestamp is not after `time`,
 * or null when playback is still before the first line.
 */
export function lyricAtTime(
    lyrics: readonly LyricLine[],
    time: number,
): LyricLine | null {
    let active: LyricLine | null =
        null;

    for (const line of lyrics) {
        if (line.time <= time) {
            active = line;
        } else {
            break;
        }
    }

    return active;
}

/**
 * Fetches synced lyrics for a song from LRCLIB.
 *
 * Returns an empty array when no synced lyrics are available.
 */
export async function fetchLyrics(
    metadata: Metadata,
): Promise<LyricLine[]> {
    const params = new URLSearchParams({
        artist_name:
            metadata.artist,
        track_name:
            metadata.title,
        album_name:
            metadata.album ?? "",
        duration: String(
            Math.round(
                metadata.duration,
            ),
        ),
    });

    const response = await fetch(
        `${LRCLIB_API}/get?${params.toString()}`,
    );

    if (!response.ok) {
        const searchParams =
            new URLSearchParams({
                artist_name:
                    metadata.artist,
                track_name:
                    metadata.title,
            });

        const searchResponse =
            await fetch(
                `${LRCLIB_API}/search?${searchParams.toString()}`,
            );

        if (!searchResponse.ok) {
            return [];
        }

        const results = (await searchResponse.json()) as ReadonlyArray<{
            syncedLyrics: string | null;
            instrumental: boolean;
            duration: number;
        }>;

        const candidates = results
            .filter(
                (result) =>
                    result.syncedLyrics &&
                    !result.instrumental,
            )
            .sort(
                (a, b) =>
                    Math.abs(
                        a.duration -
                            metadata.duration,
                    ) -
                    Math.abs(
                        b.duration -
                            metadata.duration,
                    ),
            );

        const match = candidates[0];

        if (!match) {
            return [];
        }

        return parseLRC(
            match.syncedLyrics!,
        );
    }

    const data = (await response.json()) as {
        syncedLyrics: string | null;
    };

    if (!data.syncedLyrics) {
        return [];
    }

    return parseLRC(
        data.syncedLyrics,
    );
}
