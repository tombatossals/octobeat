import type {
    Beat,
    Bar,
    TempoSegment,
    SongMap,
} from "./types";

import {
    beatAtTime,
    nextBeat,
    previousBeat,
} from "./beats";

import { barAtTime } from "./bars";

export class SongMapModel {
    constructor(
        readonly songmap: SongMap,
    ) { }

    //
    // Timing
    //

    get bpm(): number {
        return this.songmap.timing.bpm;
    }

    get offset(): number {
        return this.songmap.timing.offset;
    }

    get timeSignature(): string {
        return this.songmap.timing.timeSignature;
    }

    get tempoMap(): TempoSegment[] {
        const map = this.songmap.timing.tempoMap;

        // Retrocompatibilidad: sin tempoMap se asume tempo constante.
        if (!map || map.length === 0) {
            return [
                {
                    time: 0,
                    bpm: this.bpm,
                },
            ];
        }

        return map;
    }

    //
    // Statistics
    //

    get totalBeats(): number {
        return this.songmap.beats.length;
    }

    get totalBars(): number {
        return this.songmap.bars.length;
    }

    //
    // Navigation
    //

    beatAtTime(time: number): Beat | null {
        return beatAtTime(this.songmap, time);
    }

    nextBeat(time: number): Beat | null {
        return nextBeat(this.songmap, time);
    }

    previousBeat(time: number): Beat | null {
        return previousBeat(this.songmap, time);
    }

    barAtTime(time: number): Bar | null {
        return barAtTime(this.songmap, time);
    }
}