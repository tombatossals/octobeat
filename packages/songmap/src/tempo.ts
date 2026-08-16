import type { SongMap } from "./types";

import { lowerBound } from "./search";

/**
 * Returns the active BPM at the given song time, honoring the optional
 * tempo map. Falls back to the global `timing.bpm` when there is no tempo
 * map or the time precedes every segment.
 */
export function bpmAtTime(
    songmap: SongMap,
    time: number,
): number {
    const {
        bpm,
        tempoMap,
    } = songmap.timing;

    if (!tempoMap || tempoMap.length === 0) {
        return bpm;
    }

    const index = lowerBound(
        tempoMap,
        time,
        (segment) => segment.time,
    );

    return (
        tempoMap[index]?.bpm ??
        bpm
    );
}
