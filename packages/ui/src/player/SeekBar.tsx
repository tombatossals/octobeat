"use client";

import type { JSX } from "react";
import { usePlayerStore } from "@octobeat/player";

export function SeekBar(): JSX.Element {
    const player = usePlayerStore((state) => state.player);
    const currentTime = usePlayerStore((state) => state.currentTime);
    const duration = usePlayerStore((state) => state.duration);

    const handleChange = (
        event: React.ChangeEvent<HTMLInputElement>,
    ) => {
        if (!player) {
            return;
        }

        player.seek(Number(event.target.value));
    };

    return (
        <input
            type="range"
            min={0}
            max={duration || 0}
            step={0.01}
            value={Math.min(currentTime, duration || 0)}
            disabled={!player || duration === 0}
            onChange={handleChange}
            className="h-1.5 w-full cursor-pointer accent-primary disabled:cursor-not-allowed disabled:opacity-50"
        />
    );
}