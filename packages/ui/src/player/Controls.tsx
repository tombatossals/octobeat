"use client";

import { Pause, Play, Square } from "lucide-react";

import { Button } from "../components/button";

import { usePlayerStore } from "@octobeat/player";

export function Controls() {
    const playing = usePlayerStore((state) => state.playing);

    const playPause = usePlayerStore((state) => state.playPause);
    const stop = usePlayerStore((state) => state.stop);

    async function handlePlayPause() {
        await playPause();
    }

    return (
        <div className="flex items-center gap-1">
            <Button
                type="button"
                variant="default"
                size="icon-sm"
                onClick={handlePlayPause}
            >
                {playing ? (
                    <Pause className="h-4 w-4" />
                ) : (
                    <Play className="h-4 w-4" />
                )}
            </Button>

            <Button
                type="button"
                variant="outline"
                size="icon-sm"
                onClick={stop}
            >
                <Square className="h-4 w-4" />
            </Button>
        </div>
    );
}