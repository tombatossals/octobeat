"use client";

import { useLibraryStore } from "@/features/library/store";
import { usePlayerStore } from "@octobeat/player";

import {
    beatAtTime,
    barAtTime,
} from "@octobeat/songmap";

export function DebugHud() {
    const dataset = useLibraryStore(
        (state) => state.dataset,
    );

    const currentTime = usePlayerStore(
        (state) => state.currentTime,
    );

    const model = dataset?.songmap;

    if (!model) {
        return null;
    }

    const beat = beatAtTime(
        dataset.songmap,
        currentTime,
    );

    const bar = barAtTime(
        model,
        currentTime,
    );

    return (
        <div className="fixed bottom-4 right-4 z-40 rounded-lg border border-border bg-background/70 p-4 font-mono text-sm text-foreground backdrop-blur">
            <div>
                Beat: {beat?.index ?? "-"}
            </div>

            <div>
                Bar: {bar?.index ?? "-"}
            </div>

            <div>
                Time: {currentTime.toFixed(3)} s
            </div>

            <div>
                BPM: {model.timing.bpm.toFixed(2)}
            </div>
        </div>
    );
}