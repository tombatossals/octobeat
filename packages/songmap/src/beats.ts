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

    // La música aún no ha empezado: no hay beat activo.
    if (time < songmap.timing.offset) {
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

    // `beat.index` es 1-based (posicion de array + 1), asi que el
    // siguiente beat vive en `beats[beat.index]`.
    return beatByIndex(
        songmap,
        beat.index,
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
        beat.index - 2,
    );
}