"use client";

import { usePlayerStore } from "@octobeat/player";

function formatTime(seconds: number): string {
    if (!Number.isFinite(seconds) || seconds < 0) {
        return "00:00";
    }

    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);

    return `${minutes.toString().padStart(2, "0")}:${secs
        .toString()
        .padStart(2, "0")}`;
}

export function TimeDisplay() {
    const currentTime = usePlayerStore((state) => state.currentTime);
    const duration = usePlayerStore((state) => state.duration);

    return (
        <div className="font-mono text-sm text-muted-foreground tabular-nums">
            {formatTime(currentTime)} / {formatTime(duration)}
        </div>
    );
}