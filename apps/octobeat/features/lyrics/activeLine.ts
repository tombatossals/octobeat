import type { LyricLine } from "@octobeat/songmap";

/**
 * Returns the lyric line active at `currentTime`.
 *
 * Lines are ordered by `startTime`; the active line is the last one
 * whose start is not past the current position. Returns `null` before
 * the first line (and when there are no lyrics).
 */
export function activeLyricLine(
    lyrics: readonly LyricLine[] | null | undefined,
    currentTime: number,
): LyricLine | null {
    if (!lyrics || lyrics.length === 0) {
        return null;
    }

    let active: LyricLine | null = null;

    for (const line of lyrics) {
        if (line.startTime <= currentTime) {
            active = line;
        } else {
            break;
        }
    }

    return active;
}
