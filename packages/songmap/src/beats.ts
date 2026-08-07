import type { Beat, SongMap } from "./types";

import { lowerBound } from "./search";

export function beatAtTime(
    songmap: SongMap,
    time: number,
): Beat | null {
    const { beats } = songmap;

    if (beats.length === 0) {
        return null;
    }

    const index = lowerBound(
        beats,
        time,
        (beat) => beat.time,
    );

    return beats[index] ?? null;
}

export function beatByIndex(
    songmap: SongMap,
    index: number,
): Beat | null {
    return songmap.beats[index] ?? null;
}

export function nextBeat(
    songmap: SongMap,
    time: number,
): Beat | null {
    const beat = beatAtTime(
        songmap,
        time,
    );

    if (!beat) {
        return null;
    }

    return beatByIndex(
        songmap,
        beat.index + 1,
    );
}

export function previousBeat(
    songmap: SongMap,
    time: number,
): Beat | null {
    const beat = beatAtTime(
        songmap,
        time,
    );

    if (!beat) {
        return null;
    }

    return beatByIndex(
        songmap,
        beat.index - 1,
    );
}