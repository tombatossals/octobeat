"use client";

import { useLibraryStore } from "@/features/library/store";

export function NowPlayingSummary() {
    const dataset = useLibraryStore(
        (state) => state.dataset,
    );

    if (!dataset) {
        return null;
    }

    const { metadata } = dataset;

    return (
        <div className="pointer-events-none fixed left-4 top-28 z-40 flex flex-col gap-0.5 border-l-2 border-l-white bg-black/50 py-2 pl-3 pr-4 text-white">
            <div className="text-sm font-bold leading-tight">
                {metadata.title}
            </div>

            <div className="text-xs text-white/80">
                {metadata.artist}
            </div>

            {metadata.album && (
                <div className="text-xs text-white/60">
                    {metadata.album}
                </div>
            )}

            <div className="text-xs text-white/60">
                {metadata.genres.join(
                    ", ",
                )}
                {" · "}
                {metadata.year ?? "—"}
            </div>

            <div className="text-xs text-white/60">
                {Math.round(
                    metadata.bpm,
                )}{" "}
                BPM
            </div>
        </div>
    );
}
