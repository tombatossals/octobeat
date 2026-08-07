import type {
    Bar,
    SongMap,
} from "./types";

import { beatAtTime } from "./beats";

export function barAtTime(
    songmap: SongMap,
    time: number,
): Bar | null {
    const beat = beatAtTime(
        songmap,
        time,
    );

    if (!beat) {
        return null;
    }

    const { bars } = songmap;

    let low = 0;
    let high = bars.length - 1;

    while (low <= high) {
        const mid = (low + high) >> 1;

        const bar = bars[mid];

        if (!bar) {
            break;
        }

        if (bar.firstBeat <= beat.index) {
            low = mid + 1;
        } else {
            high = mid - 1;
        }
    }

    return bars[Math.max(0, low - 1)] ?? null;
}